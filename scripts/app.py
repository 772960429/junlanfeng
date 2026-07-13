#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""独立的微信公众号文章采集脚本（非 Web 应用）。

直接运行即可抓取指定公众号的最新文章，结果保存为 issues.json。
依赖：requests, beautifulsoup4 (以及 config.py, crawler.py)
"""

import json
import logging
import sys
from crawler import WeChatCrawler
import config
from crawler import filter_articles_by_fengjunlan
# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("wechat_crawler_script")


def main():
    """主流程：采集文章并保存到 issues.json"""
    # 可配置参数（建议从环境变量读取，方便在 Actions 中调整）
    count = 5
    account_name = getattr(config, 'ACCOUNT_NAME', '九天人工智能')
    cookie = getattr(config, 'COOKIE', None)
    token = getattr(config, 'TOKEN', None)

    # 参数校验（恢复被注释的逻辑）
    try:
        count = int(count)
    except (TypeError, ValueError):
        print("文章数量必须是正整数")
        sys.exit(1)
    if count <= 0:
        print("文章数量必须大于 0")
        sys.exit(1)
    if count > 100:
        print("单次采集不超过 100 篇，避免触发风控")
        sys.exit(1)

    print("开始采集：公众号=%s 数量=%d", account_name, count)

    # 初始化爬虫
    crawler = WeChatCrawler(
        cookie=cookie,
        token=token,
        account_name=account_name
    )

    # 使用滚动采集，保证 5 篇（或尽力而为）
    articles, err = crawler.crawl_fengjunlan(target=count, batch=20, max_total=100)
    if err:
        print("采集失败：%s", err)
        sys.exit(1)

    # 保存为 JSON 文件（指定 utf-8 编码）
    with open('issues.json', 'w', encoding='utf-8') as f:
        json.dump(articles, f, indent=2, ensure_ascii=False)

    print("采集完成，共 %d 篇，已保存到 issues.json", len(articles))


if __name__ == "__main__":
    main()
