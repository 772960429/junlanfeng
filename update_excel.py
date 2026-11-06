# -*- coding: utf-8 -*-
"""
一体化脚本：抓取 Scholar 引用数 + 更新 Excel + 拷贝到 data/pub.xlsx + 输出核查报告。

【运行流程】
  1) 调用 SerpApi 抓取 Google Scholar 作者页的论文标题与引用数，
     写入 update_data/scholar_articles.json
  2) 读取该 JSON，按 strict/loose/fuzzy 三级匹配更新 Excel 的"引用次数"列，
     另存为 update_data/合并发表物清单-..._更新引用_时间戳.xlsx
  3) 把新表格拷贝一份到 data/pub.xlsx
  4) 输出匹配核查报告到 update_data/引用匹配核查报告_时间戳.csv

【统一写回规则】
  只有当"新引用数 > 原引用数"时才写回；否则保持原值。

【匹配策略】
  1) strict : 去首尾空格 + 去尾部英文句点 后精确匹配
  2) loose  : 再统一小写 + 去掉所有非字母数字字符 后精确匹配
  3) fuzzy  : difflib 相似度 > 0.9 且 APPLY_FUZZY=True 且新值 > 原值时写回

依赖：pip install serpapi openpyxl
"""

import json
import re
import csv
import time
import shutil
from pathlib import Path
from difflib import SequenceMatcher
from datetime import datetime

import openpyxl
from serpapi import GoogleSearch

# ============ 配置区 ============
# —— SerpApi 配置 ——
API_KEY       = "693ac7dcc267c85def4e3ca70f3d0e02f960e57c9c3a571db8330814f37e7b1b"
AUTHOR_ID     = "rBjPtmQAAAAJ"
NUM_PER_PAGE  = 100        # SerpApi 单次最大 100
MAX_REQUESTS  = 5          # 防止无限循环 / 浪费额度
REQUEST_DELAY = 1.0        # 每次请求间延时（秒）

# —— 时间戳 ——
RUN_DATE = datetime.now().strftime("%Y%m%d_%H%M%S")

# —— 目录与文件 ——
UPDATE_DATA_DIR = Path("update_data")          # 所有产出集中放这里
DATA_DIR        = Path("data")                 # 下游固定读取目录

SRC_XLSX      = Path("合并发表物清单-0624-2-仅新增法律状态(3).xlsx")
SCHOLAR_JSON  = UPDATE_DATA_DIR / "scholar_articles.json"
DST_XLSX      = UPDATE_DATA_DIR / f"合并发表物清单-0624-2-仅新增法律状态(3)_更新引用_{RUN_DATE}.xlsx"
REPORT_CSV    = UPDATE_DATA_DIR / f"引用匹配核查报告_{RUN_DATE}.csv"
PUB_XLSX      = DATA_DIR / "pub.xlsx"

# —— 匹配开关 ——
APPLY_FUZZY            = True
FUZZY_THRESHOLD        = 0.90
FUZZY_APPLY_THRESHOLD  = 0.90
# ================================


# ---------- 归一化与引用数解析 ----------
def norm_strict(s) -> str:
    """去首尾空格，去掉尾部英文句点（可能连续多个），再去一次空格。"""
    if s is None:
        return ""
    return str(s).strip().rstrip(".").strip()


def norm_loose(s) -> str:
    """在 strict 基础上：统一小写，去掉所有非字母/数字/中文字符。"""
    return re.sub(r"[^0-9a-z\u4e00-\u9fff]+", "", norm_strict(s).lower())


def parse_citation_value(v) -> int:
    """把单元格原值解析为整数；无法解析一律视为 0。"""
    if v is None:
        return 0
    if isinstance(v, bool):
        return int(v)
    if isinstance(v, (int, float)):
        try:
            return int(v)
        except (ValueError, OverflowError):
            return 0
    s = str(v).strip().replace(",", "").replace("，", "")
    if not s:
        return 0
    m = re.search(r"-?\d+", s)
    return int(m.group()) if m else 0


def should_update(old_val, new_val) -> bool:
    """新值必须是有效非负整数，且严格大于原值。"""
    if new_val is None:
        return False
    try:
        new_int = int(new_val)
    except (TypeError, ValueError):
        return False
    if new_int < 0:
        return False
    return new_int > parse_citation_value(old_val)


# ---------- 第一阶段：抓取 Scholar ----------
def fetch_scholar_articles(api_key: str, author_id: str,
                           num_per_page: int = 100,
                           max_requests: int = 5,
                           delay: float = 1.0):
    """调用 SerpApi 抓取作者论文列表，返回 [{title, citations}, ...]。"""
    all_articles = []
    seen_titles = set()
    start = 0
    request_count = 0

    while request_count < max_requests:
        params = {
            "api_key":   api_key,
            "engine":    "google_scholar_author",
            "author_id": author_id,
            "hl":        "en",
            "num":       num_per_page,
            "start":     start,
        }
        search = GoogleSearch(params)
        results = search.get_dict()

        if "error" in results:
            print(f"[抓取] start={start} 请求失败: {results['error']}")
            break

        articles = results.get("articles", [])
        request_count += 1

        if not articles:
            print(f"[抓取] start={start} 返回空列表，已到末尾。")
            break

        new_count = 0
        for art in articles:
            title = (art.get("title") or "").strip()
            if not title or title in seen_titles:
                continue
            seen_titles.add(title)
            cited_by = art.get("cited_by", {}).get("value", 0) or 0
            all_articles.append({
                "title":     title,
                "citations": int(cited_by),
            })
            new_count += 1

        print(f"[抓取] start={start:>4} 返回 {len(articles):>3} 条，"
              f"新增 {new_count:>3} 条，累计 {len(all_articles)} 条。")

        if len(articles) < num_per_page:
            print("[抓取] 本页不足 {} 条，已到最后一页。".format(num_per_page))
            break

        start += num_per_page
        time.sleep(delay)

    return all_articles


# ---------- 第二阶段：索引与匹配 ----------
def load_scholar_index(json_path: Path):
    """读取 JSON，构建 strict / loose 两级索引。重复标题取引用数最大值。"""
    if not json_path.exists():
        raise FileNotFoundError(f"找不到文件：{json_path}")

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    articles = data.get("articles", []) if isinstance(data, dict) else data

    strict_idx = {}
    loose_idx  = {}

    for a in articles:
        if not isinstance(a, dict):
            continue
        title = a.get("title") or ""
        try:
            cite = int(a.get("citations") or 0)
        except (TypeError, ValueError):
            cite = 0

        ks, kl = norm_strict(title), norm_loose(title)
        if not ks:
            continue

        if ks not in strict_idx or cite > strict_idx[ks]:
            strict_idx[ks] = cite
        if kl not in loose_idx or cite > loose_idx[kl][1]:
            loose_idx[kl] = (title.strip(), cite)

    print(f"[索引] JSON 共 {len(articles)} 条，strict 索引 {len(strict_idx)} 条，"
          f"loose 索引 {len(loose_idx)} 条。")
    return strict_idx, loose_idx


def find_columns(ws):
    """在第一行表头中查找：标题列 与 引用次数列。"""
    title_col = cite_col = None
    title_name = cite_name = ""

    for cell in ws[1]:
        v = "" if cell.value is None else str(cell.value).strip()
        if title_col is None and "英文题目" in v:
            title_col, title_name = cell.column, v
        if cite_col is None and "引用次数" in v:
            cite_col, cite_name = cell.column, v

    if title_col is None:
        for cell in ws[1]:
            v = "" if cell.value is None else str(cell.value).strip()
            if v == "题目":
                title_col, title_name = cell.column, v
                break

    return title_col, cite_col, title_name, cite_name


def best_fuzzy(kl: str, loose_idx: dict):
    """在 loose 索引中找最相似的候选。"""
    best_key, best_score = None, 0.0
    for k in loose_idx:
        score = SequenceMatcher(None, kl, k).ratio()
        if score > best_score:
            best_key, best_score = k, score
    if best_key is None:
        return None, 0.0, None, 0
    orig_title, cite = loose_idx[best_key]
    return best_key, best_score, orig_title, cite


# ---------- 主流程 ----------
def main():
    # 0. 准备工作目录
    UPDATE_DATA_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # 1. 抓取 Scholar 并写入 JSON
    print("=" * 60)
    print("[阶段 1] 抓取 Google Scholar 作者论文与引用数")
    print("=" * 60)

    articles = fetch_scholar_articles(
        api_key=API_KEY,
        author_id=AUTHOR_ID,
        num_per_page=NUM_PER_PAGE,
        max_requests=MAX_REQUESTS,
        delay=REQUEST_DELAY,
    )

    if articles:
        with open(SCHOLAR_JSON, "w", encoding="utf-8") as f:
            json.dump(articles, f, ensure_ascii=False, indent=2)
        print(f"\n[抓取] 共获取 {len(articles)} 篇，已写入：{SCHOLAR_JSON}")
    else:
        # 抓取失败或返回 0 条时，回退到旧文件
        if SCHOLAR_JSON.exists():
            print(f"\n[警告] 本次抓取未获得任何论文，回退使用旧文件：{SCHOLAR_JSON}")
        else:
            print(f"\n[错误] 抓取未获得任何论文，且 {SCHOLAR_JSON} 不存在，无法继续。")
            return

    # 2. 读取 JSON，更新 Excel
    print("\n" + "=" * 60)
    print("[阶段 2] 匹配标题、更新 Excel 引用次数")
    print("=" * 60)

    strict_idx, loose_idx = load_scholar_index(SCHOLAR_JSON)

    if not SRC_XLSX.exists():
        raise FileNotFoundError(f"找不到源 Excel：{SRC_XLSX}")

    wb = openpyxl.load_workbook(SRC_XLSX)
    report_rows = []

    for ws in wb.worksheets:
        title_col, cite_col, tname, cname = find_columns(ws)
        if title_col is None or cite_col is None:
            print(f"[跳过] sheet='{ws.title}'：未找到标题列或引用次数列"
                  f"（标题列={tname or '无'}，引用列={cname or '无'}）")
            continue

        print(f"\n[处理] sheet='{ws.title}'  标题列={tname}(第{title_col}列)  "
              f"引用列={cname}(第{cite_col}列)  行数≈{ws.max_row - 1}")

        n_strict = n_loose = n_fuzzy_apply = n_fuzzy_hold = n_none = 0
        n_written = n_skipped_by_size = 0

        for r in range(2, ws.max_row + 1):
            tcell = ws.cell(row=r, column=title_col)
            ccell = ws.cell(row=r, column=cite_col)

            if not hasattr(tcell, "value") or not hasattr(ccell, "value"):
                continue  # MergedCell 只读，跳过

            raw_title = tcell.value
            if raw_title is None or str(raw_title).strip() == "":
                continue

            ks, kl = norm_strict(raw_title), norm_loose(raw_title)
            new_cite, method, note = None, "none", ""

            # 一级：strict
            if ks in strict_idx:
                new_cite, method = strict_idx[ks], "strict"
                n_strict += 1

            # 二级：loose
            elif kl in loose_idx:
                new_cite, method = loose_idx[kl][1], "loose"
                n_loose += 1

            # 三级：fuzzy
            else:
                k, score, orig, cite = best_fuzzy(kl, loose_idx)
                if score > FUZZY_THRESHOLD:
                    method = f"fuzzy({score:.3f})"
                    cond_apply = APPLY_FUZZY
                    cond_score = score > FUZZY_APPLY_THRESHOLD

                    if cond_apply and cond_score:
                        new_cite = cite
                        note = f"候选：{orig}；满足写回条件（相似度>{FUZZY_APPLY_THRESHOLD}）"
                        n_fuzzy_apply += 1
                    else:
                        n_fuzzy_hold += 1
                        reasons = []
                        if not cond_apply:
                            reasons.append("APPLY_FUZZY=False")
                        if not cond_score:
                            reasons.append(f"score≤{FUZZY_APPLY_THRESHOLD}")
                        note = f"候选：{orig}；不写回（" + "，".join(reasons) + "）"
                else:
                    n_none += 1
                    if k:
                        note = f"最佳候选相似度 {score:.3f}：{orig}"

            # 统一写回判断：新值必须严格大于原值
            old_cite = ccell.value
            written = False

            if new_cite is not None:
                if should_update(old_cite, new_cite):
                    ccell.value = new_cite
                    written = True
                    n_written += 1
                else:
                    n_skipped_by_size += 1
                    extra = (f"新值 {new_cite} 不大于原值 "
                             f"{parse_citation_value(old_cite)}，不更新")
                    note = (note + "；" + extra) if note else extra

            report_rows.append({
                "sheet":        ws.title,
                "行号":         r,
                "Excel标题":    str(raw_title).strip(),
                "匹配方式":     method,
                "候选引用数":   new_cite if new_cite is not None else "",
                "原引用次数":   old_cite,
                "当前引用次数": ccell.value,
                "是否写回":     "是" if written else "否",
                "备注":         note,
            })

        print(f"  strict={n_strict}  loose={n_loose}  "
              f"fuzzy写回={n_fuzzy_apply}  fuzzy仅候选={n_fuzzy_hold}  "
              f"未匹配={n_none}  实际写入={n_written}  "
              f"因新值不更大跳过={n_skipped_by_size}")

    # 3. 保存 Excel 到 update_data/
    wb.save(DST_XLSX)
    print(f"\n[完成] 已保存新表格：{DST_XLSX}")

    # 4. 拷贝到 data/pub.xlsx
    try:
        shutil.copy2(DST_XLSX, PUB_XLSX)
        print(f"[完成] 已拷贝并重命名：{PUB_XLSX}")
    except Exception as e:
        print(f"[警告] 拷贝到 {PUB_XLSX} 失败：{e}")

    # 5. 输出核查报告
    with open(REPORT_CSV, "w", encoding="utf-8-sig", newline="") as f:
        if report_rows:
            writer = csv.DictWriter(f, fieldnames=list(report_rows[0].keys()))
            writer.writeheader()
            writer.writerows(report_rows)
    print(f"[完成] 已输出匹配核查报告：{REPORT_CSV}")

    # 6. 汇总提示
    unmatched = [x for x in report_rows if x["匹配方式"] == "none"]
    if unmatched:
        print(f"\n[提示] {len(unmatched)} 条未匹配，见 {REPORT_CSV}")
        for x in unmatched[:20]:
            print(f"  - [{x['sheet']} 第{x['行号']}行] {x['Excel标题']}")
        if len(unmatched) > 20:
            print(f"  ... 其余 {len(unmatched) - 20} 条见报告文件")

    fuzzy_hold = [x for x in report_rows
                  if x["匹配方式"].startswith("fuzzy") and x["是否写回"] == "否"]
    if fuzzy_hold:
        print(f"\n[提示] {len(fuzzy_hold)} 条 fuzzy 候选未写回，"
              f"原因多为 APPLY_FUZZY=False 或 新值不大于原值，详见报告。")

    # 7. 最终产物路径
    print("\n" + "=" * 60)
    print("本次产出：")
    print(f"  - {SCHOLAR_JSON}")
    print(f"  - {DST_XLSX}")
    print(f"  - {REPORT_CSV}")
    print(f"  - {PUB_XLSX}")
    print("=" * 60)


if __name__ == "__main__":
    main()