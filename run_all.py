# run_all.py
import subprocess
import sys
import os
import logging
from datetime import datetime
from pathlib import Path
import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

# ============ 配置区 ============
# 项目根目录（请根据你的实际情况修改）
PROJECT_ROOT = Path(r"D:\工作资料\专家个人主页\github_repo\junlanfeng")

# 三个待执行的 Python 脚本
SCRIPTS_TO_RUN = [
    "update_excel.py",
    "scripts/build_pat_json.py",
    "scripts/build_pub_json.py"
]

# 需要上传到 GitHub 的文件（相对于 PROJECT_ROOT）
FILES_TO_PUSH = [
    "update_data/scholar_articles.json",
    "data/pub.xlsx",
    "data/publications.json",
    "data/patents.json",
    "publications.html",
    "patents.html"
]

# GitHub 仓库信息
GITHUB_REPO_URL = "https://github.com/772960429/junlanfeng.git"
GIT_BRANCH = "main"  # 或 master

# 日志文件路径
LOG_FILE = PROJECT_ROOT / "automation_run.log"
# ================================

# 设置日志：同时输出到控制台和文件
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"), # 写入文件
        logging.StreamHandler(sys.stdout)                # 输出到控制台
    ]
)
logger = logging.getLogger(__name__)


def run_script(script_path: str, step_name: str) -> bool:
    """运行一个 Python 脚本，成功返回 True，失败返回 False。"""
    full_path = PROJECT_ROOT / script_path
    if not full_path.exists():
        logger.error(f"[{step_name}] 脚本不存在: {full_path}")
        return False

    logger.info(f"[{step_name}] 开始执行: {script_path}")
    try:
        # 使用 sys.executable 确保使用当前环境的 Python 解释器
        result = subprocess.run(
            [sys.executable, str(full_path)],
            cwd=PROJECT_ROOT,  # 设置工作目录，确保脚本内的相对路径正确
            capture_output=True,
            text=True,
            encoding="gbk",        # 改用 gbk 解码
            errors="replace",      # 遇到无法解码的字符直接替换掉，绝不崩溃
            timeout=600  # 设置超时，防止卡死
        )
        # 将子脚本的输出也记录到日志
        if result.stdout:
            logger.info(f"[{step_name}] stdout:\n{result.stdout}")
        if result.stderr:
            logger.warning(f"[{step_name}] stderr:\n{result.stderr}")

        if result.returncode == 0:
            logger.info(f"[{step_name}] 执行成功。")
            return True
        else:
            logger.error(f"[{step_name}] 执行失败，返回码: {result.returncode}")
            return False

    except subprocess.TimeoutExpired:
        logger.error(f"[{step_name}] 执行超时（600秒）。")
        return False
    except Exception as e:
        logger.error(f"[{step_name}] 执行时发生异常: {e}")
        return False


def run_git_command(args: list, cwd: Path) -> bool:
    """运行 Git 命令，成功返回 True。"""
    try:
        result = subprocess.run(
            ["git"] + args,
            cwd=cwd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=120
        )
        if result.stdout:
            logger.info(f"Git stdout:\n{result.stdout}")
        if result.stderr:
            logger.warning(f"Git stderr:\n{result.stderr}")

        if result.returncode == 0:
            return True
        else:
            logger.error(f"Git 命令失败，返回码: {result.returncode}")
            return False
    except Exception as e:
        logger.error(f"运行 Git 命令时发生异常: {e}")
        return False


def push_to_github():
    """将指定文件提交并推送到 GitHub。"""
    logger.info("=" * 50)
    logger.info("开始推送文件到 GitHub...")

    # 1. 确保在 Git 仓库根目录
    if not (PROJECT_ROOT / ".git").exists():
        logger.error(f"错误：{PROJECT_ROOT} 不是一个 Git 仓库。")
        return

    # 2. 检查远程仓库配置（可选，但推荐）
    #    如果尚未配置 remote，可以取消下面几行的注释来自动设置
    # logger.info("检查/设置远程仓库...")
    # run_git_command(["remote", "remove", "origin"], PROJECT_ROOT) # 忽略错误
    # run_git_command(["remote", "add", "origin", GITHUB_REPO_URL], PROJECT_ROOT)

    # 3. 添加指定文件到暂存区
    logger.info(f"添加文件到暂存区: {FILES_TO_PUSH}")
    if not run_git_command(["add"] + FILES_TO_PUSH, PROJECT_ROOT):
        logger.error("添加文件失败，中止推送。")
        return

    # 4. 提交更改
    commit_msg = f"Auto-update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    logger.info(f"提交更改，信息: {commit_msg}")
    # 使用 --allow-empty 允许在没有实际变化时也产生提交记录，方便确认任务运行
    if not run_git_command(["commit", "-m", commit_msg, "--allow-empty"], PROJECT_ROOT):
        # 即使提交失败（比如没有变化），也继续尝试推送，因为可能有之前未推送的提交
        logger.warning("提交失败或没有变更需要提交，继续尝试推送...")

    # ================= 新增这一步 =================
    # 5. 推送前先拉取远程最新代码并变基（防止冲突）
    logger.info("拉取远程最新代码 (git pull --rebase)...")
    run_git_command(["pull", "origin", GIT_BRANCH, "--rebase"], PROJECT_ROOT)
    # ==============================================

    # 6. 推送
    logger.info(f"推送到 {GITHUB_REPO_URL} ({GIT_BRANCH})...")
    if run_git_command(["push", "origin", GIT_BRANCH], PROJECT_ROOT):
        logger.info("推送成功！")
    else:
        logger.error("推送失败！请检查网络或 GitHub 认证配置。")


def main():
    logger.info("=" * 60)
    logger.info("自动化任务链开始执行")
    logger.info("=" * 60)

    # 确保在项目根目录下运行
    os.chdir(PROJECT_ROOT)

    # 按顺序执行三个脚本
    all_success = True
    for script in SCRIPTS_TO_RUN:
        if not run_script(script, step_name=script):
            logger.error(f"脚本 {script} 执行失败，后续任务中止。")
            all_success = False
            break  # 一旦某个脚本失败，就停止后续步骤

    if all_success:
        logger.info("所有数据生成脚本执行成功。")
        push_to_github()
    else:
        logger.error("由于前置脚本执行失败，跳过 GitHub 推送步骤。")

    logger.info("=" * 60)
    logger.info("自动化任务链执行结束")
    logger.info("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.exception("自动化主脚本发生未捕获的异常！")
        sys.exit(1)