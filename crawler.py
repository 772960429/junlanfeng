# -*- coding: utf-8 -*-
"""微信公众号文章采集核心模块。

流程（复用原 main.py 中 EmsCnpl 的思路）：
1. 用 searchbiz 接口按公众号名搜索，拿到该公众号的 fakeid。
2. 用 appmsg?action=list_ex 接口按 fakeid 翻页，拿到最新 N 篇文章的
   标题、链接、发布时间。
3. 逐篇打开文章页，提取正文「第一段」作为文章摘要。
4. 使用 AI 生成英文标题（通过 API 或本地规则）
"""

import time
import logging
import requests
from bs4 import BeautifulSoup
import re
import config
import requests
import json

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
        self.session.verify = False
 # ---------- 1. 获取公众号 fakeid ----------
    def get_fakeid(self, account_name=None):
        """按公众号名称搜索 fakeid。"""
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
            if biz.get("nickname") == name:
                return biz.get("fakeid"), biz.get("nickname")
        if biz_list:
            logger.warning("未精确匹配到「%s」，取第一个结果「%s」", name, biz_list[0].get("nickname"))
            return biz_list[0].get("fakeid"), biz_list[0].get("nickname")
        logger.warning("未搜到公众号「%s」", name)
        return None, None
  # ---------- 2. 列出最新 N 篇文章 ----------
    def get_latest_articles(self, fakeid, count, begin_offset=0):
        """通过 list_ex 接口翻页，拿到最新 count 篇文章的元信息。"""
        articles = []
        begin = begin_offset
        page_size = config.PAGE_SIZE
        while len(articles) < count:
            params = {
                "action": "list_ex",
                "begin": begin,
                "count": page_size,
                "type": 9,
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
                logger.error("list_ex 接口返回异常：%s", data.get("base_resp"))
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
                    "title_en": "",
                    "url": link,
                    "create_time": _ts2str(item.get("create_time", 0)),
                    "update_time": _ts2str(item.get("update_time", 0)),
                })
                if len(articles) >= count:
                    break

            total = int(data.get("app_msg_cnt", 0))
            begin += page_size
            time.sleep(config.SLEEP_BETWEEN_REQ)
            if begin >= total:
                break

        return articles[:count]
 # ---------- 3. 提取文章第一段作为摘要 ----------
    def fetch_summary(self, url):
        """打开文章页，提取正文「第一段」作为摘要。"""
        if not url:
            return ""
        for attempt in range(config.FETCH_RETRY + 1):
            try:
                resp = self.session.get(url, timeout=20,
                                        headers={"User-Agent": config.USER_AGENT})
                soup = BeautifulSoup(resp.text, "html.parser")

                content = soup.find(id="js_content") or soup.find("div", id="page-content")
                if content is None:
                    content = soup

                for p in content.find_all(["p", "section"]):
                    text = p.get_text(strip=True)
                    if text and len(text) > 2:
                        return text

                full_text = content.get_text(strip=True)
                return full_text[:200] if full_text else ""
            except Exception as e:
                logger.warning("抓取摘要失败（第%d次）：%s", attempt + 1, e)
                time.sleep(1)
        return ""
# ---------- 4. 生成英文标题 ----------
    def generate_english_title(self, title, summary=""):
        """根据中文标题和摘要生成英文标题。
        
        优先使用 AI API，如果不可用则使用规则生成。
        """
        # 方法1：尝试使用 AI API（如果配置了）
        if hasattr(config, 'AI_API_KEY') and config.AI_API_KEY:
            try:
                return self._generate_title_with_ai(title, summary)
            except Exception as e:
                logger.warning("AI 生成英文标题失败：%s，回退到规则生成", e)
                print("AI 生成英文标题失败：%s，回退到规则生成", e)
        
        # 方法2：回退到规则生成
        return self._generate_title_by_rules(title)

    def _generate_title_with_ai(self, title, summary=""):
        """使用 DeepSeek API 生成英文标题"""
        # DeepSeek API 配置
        api_key = getattr(config, 'DEEPSEEK_API_KEY', None)
        if not api_key:
            logger.warning("未配置 DEEPSEEK_API_KEY，回退到规则生成")
            return self._generate_title_by_rules(title)
        
        api_base = getattr(config, 'DEEPSEEK_API_BASE', 'https://api.deepseek.com/v1')
        model = getattr(config, 'DEEPSEEK_MODEL', 'deepseek-chat')
        
        # 构建 prompt
        system_prompt = """你是一位专业的学术翻译专家，擅长将中文论文标题、新闻标题翻译成地道、简洁、专业的英文标题。翻译要求：
    1. 保持学术严谨性
    2. 使用专业术语
    3. 语序符合英文习惯
    4. 直接输出英文标题，不要添加任何解释、引号或额外内容"""
        
        user_content = f"中文标题：{title}\n"
        if summary:
            user_content += f"文章摘要：{summary[:200]}\n"
        user_content += "请翻译为英文标题："
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            "temperature": 0.3,
            "max_tokens": 150,
            "top_p": 0.9
        }
        
        try:
            response = requests.post(
                f"{api_base}/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            english_title = result['choices'][0]['message']['content'].strip()
            
            # 清理可能的引号
            english_title = english_title.strip('"\'')
            
            return english_title if english_title else self._generate_title_by_rules(title)
            
        except requests.exceptions.Timeout:
            logger.warning("DeepSeek API 请求超时，回退到规则生成")
            return self._generate_title_by_rules(title)
        except requests.exceptions.RequestException as e:
            logger.warning("DeepSeek API 请求失败：%s，回退到规则生成", e)
            return self._generate_title_by_rules(title)
        except (KeyError, json.JSONDecodeError) as e:
            logger.warning("DeepSeek API 响应解析失败：%s，回退到规则生成", e)
            return self._generate_title_by_rules(title)

    def _generate_title_by_rules(self, title):
        """使用规则生成英文标题（回退方案）"""
        # 简单规则：提取关键词进行翻译
        # 这里提供基本的翻译映射，复杂的可以用字典或调用翻译API
        
        # 常见学术词汇映射
        translation_map = {
            '大模型': 'Large Model',
            '智能体': 'Agent',
            '安全': 'Safe',
            '可信': 'Trustworthy',
            '技术': 'Technology',
            '会议': 'Conference',
            '研讨会': 'Workshop',
            '专题': 'Special Session',
            '成功': 'Successfully',
            '举办': 'Host',
            '探索': 'Exploring',
            '路径': 'Path',
            '能力': 'Capability',
            '治理': 'Governance',
            '原生': 'Native',
            '边界': 'Boundary',
            '方向': 'Direction',
            '发展': 'Development',
            '应用': 'Application',
            '研究': 'Research',
            '创新': 'Innovation',
            '突破': 'Breakthrough',
            '实践': 'Practice',
            '体系': 'System',
            '框架': 'Framework',
            '方法': 'Method',
            '模型': 'Model',
            '网络': 'Network',
            '数据': 'Data',
            '算法': 'Algorithm',
            '平台': 'Platform',
            '服务': 'Service',
            '产业': 'Industry',
            '生态': 'Ecosystem',
        }
        
        # 如果标题太长，取前50个字符生成
        # 简单处理：提取关键词
        words = []
        for zh, en in translation_map.items():
            if zh in title:
                words.append(en)
        
        if words:
            # 组合成标题
            if len(words) > 1:
                return ' '.join(words[:3]) + ' Research'
            else:
                return title[:30] + ' Research'
        else:
            # 默认：取前30个字符 + 年月
            return title[:30].strip() + ' (' + time.strftime("%Y") + ')'

    # ---------- 组合：一键采集 ----------
    def crawl(self, count):
        """完整采集流程。"""
        fakeid, nickname = self.get_fakeid()
        if not fakeid:
            return [], f"未找到公众号「{self.account_name}」"

        logger.info("找到公众号「%s」(fakeid=%s)，开始获取最新 %d 篇文章...",
                    nickname, fakeid, count)
        articles = self.get_latest_articles(fakeid, count)
        logger.info("共获取到 %d 篇文章，开始抓取摘要并生成英文标题...", len(articles))

        for i, art in enumerate(articles, 1):
            art["summary"] = self.fetch_summary(art.get("url", ""))
            art["title_en"] = self.generate_english_title(art.get("title", ""), art.get("summary", ""))
            logger.info("[%d/%d] %s", i, len(articles), art["title"])
            time.sleep(0.5)

        return articles, None

    def crawl_fengjunlan(self, target=5, batch=20, max_total=100):
        """
        定向采集：滚动抓取并过滤，保证至少 target 篇冯俊兰相关文章。
        """
        fakeid, nickname = self.get_fakeid()
        if not fakeid:
            return [], f"未找到公众号「{self.account_name}」"

        all_filtered = []
        seen_urls = set()
        begin_offset = 0

        logger.info("开始定向采集冯俊兰相关文章，目标 %d 篇，每批 %d 篇，上限 %d 篇", 
                    target, batch, max_total)

        while len(all_filtered) < target and begin_offset < max_total:
            current_batch = min(batch, max_total - begin_offset)
            
            logger.info("第 %d 批抓取：offset=%d, count=%d", 
                        (begin_offset // batch) + 1, begin_offset, current_batch)
            
            batch_articles = self.get_latest_articles(fakeid, current_batch, begin_offset=begin_offset)
            if not batch_articles:
                logger.info("没有更多文章，停止抓取。")
                break

            new_articles = []
            for art in batch_articles:
                url = art.get('url', '')
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    new_articles.append(art)
            
            if not new_articles:
                break

            # 抓取摘要并生成英文标题
            for i, art in enumerate(new_articles, 1):
                art['summary'] = self.fetch_summary(art.get('url', ''))
                art['title_en'] = self.generate_english_title(art.get('title', ''), art.get('summary', ''))
                time.sleep(0.3 if i % 5 != 0 else 0.8)

            # 过滤冯俊兰相关
            filtered = filter_articles_by_fengjunlan(new_articles)
            all_filtered.extend(filtered)

            logger.info("本批结果：%d/%d 篇相关，累计 %d/%d 篇", 
                        len(filtered), len(new_articles), len(all_filtered), target)

            begin_offset += len(batch_articles)

            if len(batch_articles) < current_batch:
                break

            time.sleep(config.SLEEP_BETWEEN_REQ)

        if len(all_filtered) < target:
            logger.warning("公众号内仅找到 %d 篇冯俊兰相关文章（目标 %d 篇）", 
                          len(all_filtered), target)

        # ✅ 返回时只保留需要的字段，去掉 summary
        result = []
        for art in all_filtered[:target]:
            result.append({
                "title": art.get('title', ''),
                "title_en": art.get('title_en', ''),
                "url": art.get('url', ''),
                "create_time": art.get('create_time', ''),
                "update_time": art.get('update_time', '')
            })
        
        return result, None


def _ts2str(ts):
    """时间戳 → 'YYYY-MM-DD HH:MM:SS'。"""
    if not ts:
        return ""
    try:
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(ts)))
    except Exception:
        return str(ts)


def filter_articles_by_fengjunlan(articles):
    """
    从 articles 中过滤出与冯俊兰相关的文章。
    """
    if not articles:
        return []

    patterns = [
        r'冯俊兰',
        r'\bJunlan\b(?:\s+Feng\b)?',
        r'\bJ\b\s+\bFeng\b',
        r'\bFeng\b\s*,\s*\bJ\b',
        r'\bFeng\b\s{2,}\bJ\b',
    ]
    regex = re.compile('|'.join(patterns), re.IGNORECASE)

    filtered = []
    for art in articles:
        title = art.get('title', '') or ''
        summary = art.get('summary', '') or ''
        if regex.search(title) or regex.search(summary):
            filtered.append(art)
    return filtered


if __name__ == "__main__":
    import sys
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    crawler = WeChatCrawler()
    result, err = crawler.crawl(n)
    if err:
        print("采集失败：", err)
    else:
        for idx, art in enumerate(result, 1):
            print(f"\n===== {idx}. {art['title']} =====")
            print(f"英文：{art.get('title_en', '')}")
            print(f"时间：{art['create_time']}")
            print(f"链接：{art['url']}")