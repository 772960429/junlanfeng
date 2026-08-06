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

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("wewerss_crawler")


def format_iso_to_common(iso_str: str) -> str:
    """
    将 "2026-07-23T10:01:54.000Z" 转换为 "2026-07-23 10:01:54"
    """
    if iso_str.endswith('Z'):
        iso_str = iso_str[:-1] + '+00:00'
    dt = datetime.fromisoformat(iso_str)
    return dt.strftime('%Y-%m-%d %H:%M:%S')


class WeWeRssCrawler:
    """基于 WeWe RSS 的采集器（自动提取纯文本并去除推荐阅读）。"""

    def __init__(self, feed_url: str = None, timeout: int = 30):
        self.feed_url = feed_url or "http://120.53.251.205:4000/feeds/MP_WXS_3690269372.json?limit=50"
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

    # ---------- 英文标题生成（已有功能） ----------
    def generate_english_title(self, title):
        if hasattr(config, 'DEEPSEEK_API_KEY') and config.DEEPSEEK_API_KEY:
            try:
                return self._generate_title_with_ai(title)
            except Exception as e:
                logger.warning("AI 生成英文标题失败：%s，回退到规则生成", e)
                print(f"AI 生成英文标题失败：{e}，回退到规则生成")
        return title

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

    # ---------- 纯文本提取与清理 ----------
    @staticmethod
    def _extract_plain_text(html_content: str) -> str:
        """从 HTML 中提取纯文本，去除 script/style 等标签。"""
        if not html_content:
            return ""
        soup = BeautifulSoup(html_content, "html.parser")
        for tag in soup(["script", "style", "noscript", "meta", "link"]):
            tag.decompose()
        text = soup.get_text(separator="\n", strip=True)
        text = re.sub(r'\n\s*\n', '\n\n', text)
        return text.strip()

    @staticmethod
    def _remove_recommendation(text: str) -> str:
        """
        去除“推荐阅读”及之后的内容。
        匹配常见关键词：推荐阅读、猜你喜欢、相关推荐等。
        """
        if not text:
            return ""
        # 按行分割，更容易定位
        lines = text.split('\n')
        result_lines = []
        for line in lines:
            # 如果当前行包含这些关键词，则停止添加
            if re.search(r'(推荐阅读|猜你喜欢|相关推荐|更多推荐|往期精选)', line):
                break
            result_lines.append(line)
        return '\n'.join(result_lines).strip()

    # ---------- 采集接口 ----------
    def fetch_articles(self, limit: int = 50) -> List[Dict]:
        """拉取文章列表，并将内容转换为纯文本并去除推荐阅读。"""
        url = self.feed_url
        if "?limit=" not in url:
            url = f"{url}?limit={limit}" if "?" not in url else f"{url}&limit={limit}"
        print(f"Fetching articles from WeWe RSS: {url}")
        try:
            resp = self.session.get(url, timeout=self.timeout)
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            logger.error("获取 WeWe RSS 数据失败：%s", e)
            return []

        items = data.get("items", []) or []
        articles = []
        for item in items:
            title = item.get("title", "").strip()
            content_raw = item.get("content_text", "") or item.get("content_html", "")
            if content_raw and content_raw.strip().startswith("<"):
                content = self._extract_plain_text(content_raw)
            else:
                content = content_raw.strip()
            # ✅ 去除推荐阅读部分
            content = self._remove_recommendation(content)

            date_modified = format_iso_to_common(item.get("date_modified", ""))
            url = item.get("url", "")
            article_id = item.get("id", "")

            articles.append({
                "id": article_id,
                "title": title,
                "url": url,
                "content": content,
                "date_modified": date_modified,
            })

        logger.info("从 WeWe RSS 获取到 %d 篇文章（已清理）", len(articles))
        print(f"从 WeWe RSS 获取到 {len(articles)} 篇文章（已清理）")
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
            url = art.get('url', '')
            if regex.search(title) or regex.search(content) or regex.search(url):
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
    crawler = WeWeRssCrawler()
    return crawler.filter_articles_by_fengjunlan(articles)


if __name__ == "__main__":
    import sys
   #  limit = int(sys.argv[1]) if len(sys.argv) > 1 else 50
    crawler = WeWeRssCrawler()
   #  results = crawler.crawl(17)
    title_en = crawler.generate_english_title("2026 WAIC｜九天安全可信多模态大模型JT4.1与MoMA多模型服务引擎2.0重磅发布，驱动AI赋能致远行稳")
    print(title_en)
   #  print(f"共找到 {len(results)} 篇冯俊兰相关文章：")
   #  for idx, art in enumerate(results, 1):
   #      print(f"\n===== {idx}. {art['title']} =====")
   #      print(f"英文标题：{art.get('title_en', '')}")
   #      print(f"时间：{art.get('update_time', '')}")
   #      print(f"链接：{art['url']}")