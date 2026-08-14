# -*- coding: utf-8 -*-
"""基于 WeWe RSS 的微信公众号文章采集模块（纯文本筛选）。

流程：
1. 从 WeWe RSS 的 JSON Feed 接口获取文章列表（可指定数量）。
2. 将文章内容（可能为 HTML）转换为纯文本。
3. 去除“推荐阅读”及之后的内容。
4. 从标题、纯文本内容和链接中筛选出与“冯俊兰”相关的文章。
5. 返回包含标题、英文标题、链接、更新时间等信息的列表。
"""

import config
import time
import logging
import re
import requests
import json
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
from datetime import datetime
from collections import OrderedDict

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("wewerss_crawler")



class Crawler:
    """基于 WeWe RSS 的采集器（自动提取纯文本并去除推荐阅读）。"""

    def __init__(self, feed_url: str = None, timeout: int = 30):
        self.feed_url = feed_url
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        })
        # 预编译正则表达式，提高性能
        self._fengjunlan_pattern = re.compile(
            r'冯俊兰|'
            r'\bJunlan\b(?:\s+Feng\b)?|'
            r'\bJ\b\s+\bFeng\b|'
            r'\bFeng\b\s*,\s*\bJ\b|'
            r'\bFeng\b\s{2,}\bJ\b',
            re.IGNORECASE
        )
        self._trans_cache = OrderedDict()   # 有序字典，保持插入顺序
        self._cache_max_size = 20
    # ---------- 缓存管理 ----------
    def _add_to_cache(self, key: str, value: str):
        """添加或更新缓存，超过上限则淘汰最旧的条目（LRU策略）。"""
        if key in self._trans_cache:
            # 如果已存在，删除旧条目，后面重新插入，使其移到末尾
            del self._trans_cache[key]
        elif len(self._trans_cache) >= self._cache_max_size:
            # 淘汰最早的一个（第一个）
            self._trans_cache.popitem(last=False)
        self._trans_cache[key] = value

    def generate_english_title(self, title):
        # 1. 检查缓存
        cached = self._trans_cache.get(title)
        if cached is not None:
            logger.info("翻译命中缓存: %s -> %s", title, cached)
            # 将该键移到末尾，表示最近使用
            self._trans_cache.move_to_end(title)
            return cached

        # 2. 未命中，调用 AI 或规则生成
        if hasattr(config, 'DEEPSEEK_API_KEY') and config.DEEPSEEK_API_KEY:
            try:
                en_title = self._generate_title_with_ai(title)
            except Exception as e:
                logger.warning("AI 生成英文标题失败：%s，回退到规则生成", e)
                en_title = self._generate_title_by_rules(title)
        else:
            en_title = title

        # 3. 加入缓存
        self._add_to_cache(title, en_title)
        return en_title

    # 可选：缓存大小可配置
    def set_cache_max_size(self, size: int):
        self._cache_max_size = size
        # 如果当前缓存超过新大小，删除最旧的条目
        while len(self._trans_cache) > size:
            self._trans_cache.popitem(last=False)

    def _generate_title_with_ai(self, title):
        api_key = getattr(config, 'DEEPSEEK_API_KEY', None)
        print(f"Using DeepSeek API to generate English title for: {api_key}")
        if not api_key:
            logger.warning("未配置 DEEPSEEK_API_KEY，回退到规则生成")
            print("未配置 DEEPSEEK_API_KEY，回退到规则生成")
            return self._generate_title_by_rules(title)
        api_base = getattr(config, 'DEEPSEEK_API_BASE', 'https://api.deepseek.com/v1')
        model = getattr(config, 'DEEPSEEK_MODEL', 'deepseek-chat')
        print(f"api_base: {api_base}, model: {model}, title: {title}")
        system_prompt = """你是一位专业的学术翻译专家，擅长将中文论文标题、新闻标题翻译成地道、简洁、专业的英文标题。翻译要求：
    1. 保持学术严谨性
    2. 使用专业术语
    3. 语序符合英文习惯
    4. 直接输出英文标题，不要添加任何解释、引号或额外内容"""
        user_content = f"中文标题：{title}\n"
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
            response = requests.post(f"{api_base}/chat/completions", headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            result = response.json()
            english_title = result['choices'][0]['message']['content'].strip().strip('"\'')
            return english_title if english_title else self._generate_title_by_rules(title)
        except Exception as e:
            logger.warning("DeepSeek API 失败：%s，回退到规则生成", e)
            print(f"DeepSeek API 失败：{e}，回退到规则生成")
            return self._generate_title_by_rules(title)



    # ---------- 采集接口 ----------
    def fetch_articles(self, limit: int = 50) -> List[Dict]:
        """拉取文章列表，并将内容转换为纯文本并去除推荐阅读。"""
        url = self.feed_url
        if "?limit=" not in url:
            url = f"{url}?limit={limit}" if "?" not in url else f"{url}&limit={limit}"
        print(f"Fetching articles : {url}")
        try:
            resp = self.session.get(url, timeout=self.timeout)
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            logger.error("获取 WeWe RSS 数据失败：%s", e)
            return []

        items = data.get("data", {}).get("rows", []) or []
        articles = []
        for item in items:
            title = item.get("title", "").strip()
            content = item.get("contentText", "")
            date_modified = item.get("publishTime", "")
            url = item.get("links", "")

            articles.append({
                "title": title,
                "url": url,
                "content": content,
                "date_modified": date_modified,
            })

        logger.info("从 zlzchat 获取到 %d 篇文章（已清理）", len(articles))
        print(f"从 zlzchat 获取到 {len(articles)} 篇文章（已清理）")
        return articles

    # ---------- 筛选冯俊兰 ----------
    def filter_articles_by_fengjunlan(self, articles: List[Dict]) -> List[Dict]:
        if not articles:
            return []
        regex = self._fengjunlan_pattern
        filtered = []
        for art in articles:
            title = art.get('title', '')
            content = art.get('content', '')
            if (title and regex.search(title)) or (content and regex.search(content)):
                filtered.append(art)
        logger.info("筛选出 %d 篇冯俊兰相关文章", len(filtered))
        print(f"筛选出 {len(filtered)} 篇冯俊兰相关文章")
        return filtered

    # ---------- 完整流程 ----------
    def crawl(self, limit: int = 50) -> List[Dict]:
        all_articles = self.fetch_articles(limit)
        if not all_articles:
            return []
        filtered = self.filter_articles_by_fengjunlan(all_articles)

        result = []
        for art in filtered:
            result.append({
                "title": art.get("title", ""),
                "title_en": self.generate_english_title(art.get("title", "")),
                "url": art.get("url", ""),
                "update_time": art.get("date_modified", ""),
            })
        return result


def filter_articles_by_fengjunlan(articles):
    crawler = Crawler()
    return crawler.filter_articles_by_fengjunlan(articles)


def trigger_update_feed_all():
    """调用更新 Feed 接口，触发 zlzchat 的全量更新任务。

    接口返回格式: {"msg":"任务提交成功","code":0}
    成功条件: code == 0
    """
    url = "http://120.53.251.205:10082/updateFeedAll?key=zlzchat"
    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        if data.get("code") == 0:
            logger.info("更新任务提交成功：%s", data.get("msg"))
            print(f"更新任务提交成功：{data.get('msg')}")
            return True, data
        else:
            logger.warning("更新任务提交失败：%s", data)
            print(f"更新任务提交失败：{data}")
            return False, data
    except Exception as e:
        logger.error("调用更新 Feed 接口异常：%s", e)
        print(f"调用更新 Feed 接口异常：{e}")
        return False, None


if __name__ == "__main__":
    import sys
   #  limit = int(sys.argv[1]) if len(sys.argv) > 1 else 50
    crawler = Crawler()
   #  results = crawler.crawl(17)
    title_en = crawler.generate_english_title("WAIC 2026丨中国移动承办企业人工智能高质量发展论坛")
    print(title_en)
   #  print(f"共找到 {len(results)} 篇冯俊兰相关文章：")
   #  for idx, art in enumerate(results, 1):
   #      print(f"\n===== {idx}. {art['title']} =====")
   #      print(f"英文标题：{art.get('title_en', '')}")
   #      print(f"时间：{art.get('update_time', '')}")
   #      print(f"链接：{art['url']}")