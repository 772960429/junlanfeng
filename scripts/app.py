#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""独立的微信公众号文章采集脚本（非 Web 应用）。

通过 WeWe RSS 接口获取文章，并筛选冯俊兰相关文章，结果保存为 issues.json。
支持增量追加，并保持最多30条（删除最旧）。
"""

import json
import logging
import sys
from pathlib import Path
from crawler_wewerss import WeWeRssCrawler
import config
import time
from datetime import datetime
# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("wewerss_crawler_script")

MAX_ARTICLES = 30
DATA_FILE = Path("data/issues.json")


def load_existing_articles() -> list:
    """加载现有的文章列表（如果文件存在且有效）。"""
    if not DATA_FILE.exists():
        return []
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            else:
                logger.warning("issues.json 格式不是列表，将重新创建")
                return []
    except Exception as e:
        logger.warning("读取现有 issues.json 失败：%s，将重新创建", e)
        return []


def save_articles(articles: list):
    """保存文章列表到文件，确保目录存在。"""
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(articles, f, indent=2, ensure_ascii=False)


def merge_and_limit(existing: list, new_articles: list) -> list:
    """
    合并现有文章和新文章，去重（基于title），并按日期排序（最新的在前），
    保留最多 MAX_ARTICLES 条。
    """
    # 用字典按 title 去重，保留最新的一条（如果有重复）
    title_map = {}
    # 先加入现有文章，再加入新文章（新文章覆盖同title旧文章）
    for art in existing:
        title = art.get('title')
        if title:
            title_map[title] = art
    for art in new_articles:
        title = art.get('title')
        if title:
            title_map[title] = art
    # 转为列表
    merged = list(title_map.values())
    # 按日期排序（update_time字段），如果没有日期则放最后
    # def get_date(art):
    #     return art.get('update_time', '')
    # merged.sort(key=get_date, reverse=True)  # 最新的在前
    merged.sort(
    key=lambda x: time.mktime(datetime.strptime(x.get('update_time', ''), '%Y-%m-%d %H:%M:%S').timetuple()),
    reverse=True)
    # 截取前 MAX_ARTICLES 条
    return merged[:MAX_ARTICLES]


def main():
    """主流程：采集文章并增量保存到 issues.json"""
    count = getattr(config, 'COUNT', 20)
    feed_url = getattr(config, 'FEED_URL', 
                       f'http://120.53.251.205:4000/feeds/MP_WXS_3690269372.json?limit={count}')

    
    print(f"开始采集，目标数量 {count} 篇，Feed 地址：{feed_url}")

    # 初始化爬虫
    crawler = WeWeRssCrawler(feed_url=feed_url)

    # 采集并筛选冯俊兰相关文章
    new_articles = crawler.crawl()

    if not new_articles:
        print("本次未找到新的冯俊兰相关文章，不更新文件")
        return

    # 加载现有文章
    existing = load_existing_articles()
    # 合并、去重、排序、截断
    merged = merge_and_limit(existing, new_articles)
    # 保存
    save_articles(merged)

    print(f"采集完成，新增 {len(new_articles)} 篇，合并后共 {len(merged)} 篇，已保存到 {DATA_FILE}")


if __name__ == "__main__":
    main()