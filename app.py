# -*- coding: utf-8 -*-
"""微信公众号文章采集后台。

启动后访问 http://127.0.0.1:5000 即可使用：
- 输入要采集的「文章数量」
- 可选：粘贴最新的 cookie / token（cookie 会过期，过期就在网页里覆盖）
- 点击「开始采集」，后台调用 WeChatCrawler 抓取「九天人工智能」最新文章
- 结果展示标题、发布时间、摘要、原文链接

依赖：Flask、requests、beautifulsoup4
"""

import logging
from flask import Flask, request, jsonify, render_template

import config
from crawler import WeChatCrawler
import json
import requests
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("wechat_backend")

app = Flask(__name__)


@app.route("/")
def index():
    """主页：采集界面。"""
    return render_template("index.html",
                           account_name=config.ACCOUNT_NAME,
                           default_token=config.TOKEN)


# @app.route("/api/crawl", methods=["POST"])
def api_crawl(data):
    """采集接口。

    请求体 JSON：
        {
            "count": 5,                 # 必填：要采集的文章数量
            "cookie": "可选覆盖",        # 选填：覆盖 config 里的 cookie
            "token":  "可选覆盖",        # 选填：覆盖 config 里的 token
            "account_name": "可选覆盖"   # 选填：覆盖默认公众号名
        }
    响应 JSON：
        { "ok": true,  "articles": [...] }      # 成功
        { "ok": false, "error": "..." }         # 失败
    """
    # data = request.get_json(silent=True) or {}
    count = data.get("count")
    cookie = (data.get("cookie") or "").strip() or None
    token = (data.get("token") or "").strip() or None
    account_name = (data.get("account") or "").strip() or None

    # 校验数量
    try:
        count = int(count)
    except (TypeError, ValueError):
        return jsonify(ok=False, error="请输入有效的文章数量（正整数）。")
    if count <= 0:
        return jsonify(ok=False, error="文章数量必须大于 0。")
    if count > 100:
        return jsonify(ok=False, error="单次采集不超过 100 篇，避免触发风控。")

    logger.info("开始采集：公众号=%s 数量=%d", account_name or config.ACCOUNT_NAME, count)
    print("开始采集：公众号=%s 数量=%d", account_name or config.ACCOUNT_NAME, count)
    crawler = WeChatCrawler(cookie=cookie, token=token, account_name=account_name)
    articles, err = crawler.crawl(count)

    if err:
        logger.error("采集失败：%s", err)
        print("采集失败：%s", err)
        return jsonify(ok=False, error=err)
    with open('issues.json', 'w') as f:
        json.dump(articles, f, indent=2)
    logger.info("采集完成，共 %d 篇。", len(articles))
    print("采集完成，共 %d 篇。", len(articles))
    return jsonify(ok=True, count=len(articles), articles=articles)


# @app.route("/api/test", methods=["GET"])
# def api_test():
#     """连通性自检：检查 cookie/token 是否还有效（试着搜一次公众号）。"""
#     cookie = (request.args.get("cookie") or "").strip() or None
#     token = (request.args.get("token") or "").strip() or None
#     crawler = WeChatCrawler(cookie=cookie, token=token)
#     fakeid, nickname = crawler.get_fakeid()
#     if fakeid:
#         return jsonify(ok=True, fakeid=fakeid, nickname=nickname,
#                        msg=f"cookie/token 有效，找到公众号「{nickname}」。")
#     return jsonify(ok=False, msg="cookie/token 可能已失效，请重新登录 mp.weixin.qq.com 获取。")

api_crawl({"count": 5})

# if __name__ == "__main__":
#     # 关闭 requests 的 SSL 警告（crawler 里用了 verify=False）
#     import os
#     import urllib3
#     urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

#     host = os.environ.get("HOST", "0.0.0.0")
#     port = int(os.environ.get("PORT", "5000"))
#     debug = os.environ.get("FLASK_DEBUG", "0") == "1"
#     app.run(host=host, port=port, debug=debug)
