# -*- coding: utf-8 -*-
"""微信公众号文章采集核心模块。

流程（复用原 main.py 中 EmsCnpl 的思路）：
1. 用 searchbiz 接口按公众号名搜索，拿到该公众号的 fakeid。
2. 用 appmsg?action=list_ex 接口按 fakeid 翻页，拿到最新 N 篇文章的
   标题、链接、发布时间。
3. 逐篇打开文章页，提取正文「第一段」作为文章摘要。
"""

import time
import logging
import requests
from bs4 import BeautifulSoup

import config

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("wechat_crawler")


class WeChatCrawler:
    """微信公众号文章采集器。"""

    SEARCH_BIZ_URL = "https://mp.weixin.qq.com/cgi-bin/searchbiz"
    APPMSG_LIST_URL = "https://mp.weixin.qq.com/cgi-bin/appmsg"

    def __init__(self, cookie=None, token=None, account_name=None):
        self.cookie = cookie or config.COOKIE
        self.token = token or config.TOKEN
        self.account_name = account_name or config.ACCOUNT_NAME
        self.headers = {
            "Cookie": self.cookie,
            "User-Agent": config.USER_AGENT,
            "Referer": "https://mp.weixin.qq.com/cgi-bin/appmsg"
                       "?t=media/appmsg_list&action=list_card&type=10&token="
                       + str(self.token) + "&lang=zh_CN",
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        # 关闭 SSL 校验告警（原 main.py 也用的 verify=False）
        self.session.verify = False

    # ---------- 1. 获取公众号 fakeid ----------
    def get_fakeid(self, account_name=None):
        """按公众号名称搜索 fakeid。

        对应微信公众平台后台「搜索公众号」功能。
        返回 (fakeid, nickname) 或 (None, None)。
        """
        name = account_name or self.account_name
        params = {
            "action": "search_biz",
            "begin": 0,
            "count": 5,
            "query": name,
            "token": self.token,
            "lang": "zh_CN",
            "f": "json",
            "ajax": 1,
        }
        try:
            resp = self.session.get(self.SEARCH_BIZ_URL, params=params, timeout=15)
            data = resp.json()
        except Exception as e:
            logger.error("搜索公众号失败：%s", e)
            return None, None

        if data.get("base_resp", {}).get("ret") != 0:
            logger.error("搜索公众号接口返回异常：%s", data.get("base_resp"))
            return None, None

        biz_list = data.get("list", []) or []
        for biz in biz_list:
            # 精确匹配名称，避免搜到同名近似号
            if biz.get("nickname") == name:
                return biz.get("fakeid"), biz.get("nickname")
        # 精确匹配失败则取第一条
        if biz_list:
            logger.warning("未精确匹配到「%s」，取第一个结果「%s」", name, biz_list[0].get("nickname"))
            return biz_list[0].get("fakeid"), biz_list[0].get("nickname")
        logger.warning("未搜到公众号「%s」", name)
        return None, None

    # ---------- 2. 列出最新 N 篇文章 ----------
    def get_latest_articles(self, fakeid, count):
        """通过 list_ex 接口翻页，拿到最新 count 篇文章的元信息。

        参考 main.py:264 的 EmsCnpl.run：每页 PAGE_SIZE 条，逐页累加。
        返回 list[dict]，每个 dict 含 title / url / create_time / update_time。
        """
        articles = []
        begin = 0
        page_size = config.PAGE_SIZE
        while len(articles) < count:
            params = {
                "action": "list_ex",
                "begin": begin,
                "count": page_size,
                "type": 9,           # 9 = 图文消息（参考原 main.py）
                "query": "",
                "fakeid": fakeid,
                "token": self.token,
                "lang": "zh_CN",
                "f": "json",
                "ajax": 1,
            }
            try:
                resp = self.session.get(self.APPMSG_LIST_URL, params=params, timeout=15)
                data = resp.json()
            except Exception as e:
                logger.error("获取文章列表失败（begin=%s）：%s", begin, e)
                break

            ret = data.get("base_resp", {}).get("ret")
            if ret != 0:
                logger.error("list_ex 接口返回异常：%s（可能是 cookie/token 过期）", data.get("base_resp"))
                break

            msg_list = data.get("app_msg_list", []) or []
            if not msg_list:
                logger.info("没有更多文章了。")
                break

            for item in msg_list:
                title = item.get("title", "").replace("<em>", "").replace("</em>", "")
                link = item.get("link", "")
                articles.append({
                    "title": title,
                    "url": link,
                    "create_time": _ts2str(item.get("create_time", 0)),
                    "update_time": _ts2str(item.get("update_time", 0)),
                })
                if len(articles) >= count:
                    break

            total = int(data.get("app_msg_cnt", 0))
            begin += page_size
            time.sleep(config.SLEEP_BETWEEN_REQ)
            # 已经翻到尾
            if begin >= total:
                break

        return articles[:count]

    # ---------- 3. 提取文章第一段作为摘要 ----------
    def fetch_summary(self, url):
        """打开文章页，提取正文「第一段」作为摘要。

        微信文章正文在 <div id="js_content"> 内，第一段通常是
        <p> 或 <section><p>。这里取第一个有实际文字的 <p>。
        """
        if not url:
            return ""
        for attempt in range(config.FETCH_RETRY + 1):
            try:
                # 文章页不需要后台 cookie，普通 UA 即可
                resp = self.session.get(url, timeout=20,
                                        headers={"User-Agent": config.USER_AGENT})
                soup = BeautifulSoup(resp.text, "html.parser")

                # 正文容器
                content = soup.find(id="js_content") or soup.find("div", id="page-content")
                if content is None:
                    # 退而求其次：找全文第一个 <p>
                    content = soup

                # 优先按 <p> 找第一段有文字的
                for p in content.find_all(["p", "section"]):
                    text = p.get_text(strip=True)
                    if text and len(text) > 2:        # 过滤空段/单字符段
                        return text

                # 兜底：取正文全部纯文本前 200 字
                full_text = content.get_text(strip=True)
                return full_text[:200] if full_text else ""
            except Exception as e:
                logger.warning("抓取摘要失败（第%d次）：%s", attempt + 1, e)
                time.sleep(1)
        return ""

    # ---------- 组合：一键采集 ----------
    def crawl(self, count):
        """完整采集流程：拿 fakeid → 列文章 → 抓摘要。

        返回 (articles, error)。error 为 None 表示成功。
        articles 每项含 title / url / create_time / update_time / summary。
        """
        fakeid, nickname = self.get_fakeid()
        if not fakeid:
            return [], f"未找到公众号「{self.account_name}」，请检查 cookie/token 是否有效。"

        logger.info("找到公众号「%s」(fakeid=%s)，开始获取最新 %d 篇文章...",
                    nickname, fakeid, count)
        articles = self.get_latest_articles(fakeid, count)
        logger.info("共获取到 %d 篇文章，开始抓取摘要...", len(articles))

        for i, art in enumerate(articles, 1):
            art["summary"] = self.fetch_summary(art.get("url", ""))
            logger.info("[%d/%d] %s", i, len(articles), art["title"])
            time.sleep(0.5)

        return articles, None


def _ts2str(ts):
    """时间戳 → 'YYYY-MM-DD HH:MM:SS'。"""
    if not ts:
        return ""
    try:
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(ts)))
    except Exception:
        return str(ts)


if __name__ == "__main__":
    # 命令行直接跑：python crawler.py 3
    import sys
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    crawler = WeChatCrawler()
    result, err = crawler.crawl(n)
    if err:
        print("采集失败：", err)
    else:
        for idx, art in enumerate(result, 1):
            print(f"\n===== {idx}. {art['title']} =====")
            print(f"时间：{art['create_time']}")
            print(f"链接：{art['url']}")
            print(f"摘要：{art['summary']}")
