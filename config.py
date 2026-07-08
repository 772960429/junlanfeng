# -*- coding: utf-8 -*-
"""配置文件。

微信公众号后台采集需要登录 mp.weixin.qq.com 后台（扫码登录），
拿到 cookie 和 token 之后填到这里。cookie / token 会过期，
过期后重新登录获取即可。后台页面也支持在网页上临时覆盖这些值。

所有关键配置都支持用环境变量覆盖（优先级高于这里的默认值），
方便 Docker 部署时通过 -e 注入，无需重新构建镜像：
    WECHAT_COOKIE       cookie 整段
    WECHAT_TOKEN        token
    WECHAT_ACCOUNT      公众号名称
    WECHAT_PAGE_SIZE    每页条数（默认 5）
    WECHAT_SLEEP        请求间隔秒数（默认 1.5）

登录后台后，浏览器地址栏里会带一个 token 参数，例如：
https://mp.weixin.qq.com/cgi-bin/home?t=home/index&lang=zh_CN&token=362558870
                                                       ^^^^^^^^^ 这就是 token
"""

import os


def _env(key, default):
    """从环境变量读取，没有则用默认值。"""
    val = os.environ.get(key)
    return val if val else default


# ====== 默认 cookie / token（来源：你当前登录后台抓取的值） ======
# 过期后重新登录 mp.weixin.qq.com 拿新的覆盖即可
_DEFAULT_COOKIE = (
    "RK=nANRKYg/Zj; ptcz=4548ddf6bd7179c6b0048c7d059b0bdea1b998a718c2ba838e4c68c26d89c67d; ua_id=mlFfDTVWadrFy5kLAAAAANTRl3bgHZuIczJB7V3A9gk=; wxuin=68286617300485; rewardsn=; wxtokenkey=777; _clck=tchj3o|1|g7k|0; mm_lang=zh_CN; uuid=6c5926c695e9d26aeb33eb5391e9c35c; rand_info=CAESIAaeo5WAOFr8rD18mbJLUpOSznUnngMIka5TjfmryHWs; slave_bizuin=3590805513; data_bizuin=3590805513; bizuin=3590805513; data_ticket=bkMkSjtVvlBpneihf3g0QnrWx7Ce0y0iSMwqGTv2pdJ1bah97NIYcQi/2JbflDhQ; slave_sid=N3RZcm5SV2JBd1V6dXozMTR4TkJ1WjRDNXZRcmRRUFlzSUNtMjc2SnViU0Uxa25mM0lsdGdEQl9ZUmpnOEdnNFFXM2piaU53Z2gxZURPcElEM2RGX1RaX0k2SW9uM1RMOTY0aUFnOWg2al82cmNKdmtlUEp2QlFwUm84eXczdXhFaWFySTV4bXhhb1ppQURu; slave_user=gh_ba294d69ee29; xid=e1ba4e7a9c529ec1367e511b98f5a60b; _clsk=12ofth|1783502770894|3|1|mp.weixin.qq.com/weheat-agent/payload/record"
)

COOKIE = _env("cookie", _DEFAULT_COOKIE)
TOKEN = _env("token", "922632755")

# User-Agent，建议和登录时浏览器的 UA 保持一致
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
)

# 要爬取的公众号名称（只爬这一个）
ACCOUNT_NAME = _env("WECHAT_ACCOUNT", "九天人工智能")

# 微信后台单次 list_ex 接口返回条数（微信限制最多 5 条/页）
PAGE_SIZE = int(_env("WECHAT_PAGE_SIZE", "5"))

# 请求间隔（秒），避免触发风控
SLEEP_BETWEEN_REQ = float(_env("WECHAT_SLEEP", "1.5"))

# 抓取文章正文时最多重试次数
FETCH_RETRY = 2
