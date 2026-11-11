# run_all.py
import subprocess
import sys
import os
import logging
import smtplib
from datetime import datetime
from pathlib import Path
from email.mime.text import MIMEText
from email.header import Header

# ============ 解决 Windows 控制台乱码 ============
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
# ================================================

# ============ 配置区 ============
PROJECT_ROOT = Path(r"D:\工作资料\专家个人主页\junlanfeng-main\junlanfeng-main")

SCRIPTS_TO_RUN = [
    "update_excel.py",
    "scripts/build_pat_json.py",
    "scripts/build_pub_json.py",
]

FILES_TO_PUSH = [
    "update_data/scholar_articles.json",
    "data/pub.xlsx",
    "data/publications.json",
    "data/patents.json",
    "publications.html",
    "patents.html"
]

GITHUB_REPO_URL = "https://github.com/772960429/junlanfeng.git"
GIT_BRANCH = "main"
LOG_FILE = PROJECT_ROOT / "automation_run.log"

# ============ 邮件配置区 ============
RECEIVER_EMAIL = "772960429@qq.com"
SMTP_SERVER = "smtp.qq.com"
SMTP_PORT = 465
SENDER_EMAIL = "772960429@qq.com"    
SENDER_PASSWORD = "zfwtyjdhxaktbbib" # 务必替换为你的授权码！
# ================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def send_failure_email(error_msg: str):
    """发送报错邮件"""
    logger.info("正在尝试发送报错邮件...")
    subject = "❌ 自动化任务执行失败通知"
    
    body = f"""
自动化任务在执行过程中发生了错误。

时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
错误信息: {error_msg}

请登录服务器或查看本地日志文件获取详细信息：
{LOG_FILE}
    """
    
    message = MIMEText(body, 'plain', 'utf-8')
    # 修复了邮件头部编码报错的问题
    message['From'] = f"AutoMonitor <{SENDER_EMAIL}>" 
    message['To'] = RECEIVER_EMAIL
    message['Subject'] = Header(subject, 'utf-8')

    try:
        server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, [RECEIVER_EMAIL], message.as_string())
        server.quit()
        logger.info("报错邮件发送成功！")
    except Exception as e:
        logger.error(f"发送邮件失败，请检查邮箱配置和网络: {e}")


def run_script(script_path: str, step_name: str) -> bool:
    full_path = PROJECT_ROOT / script_path
    if not full_path.exists():
        logger.error(f"[{step_name}] 脚本不存在: {full_path}")
        return False

    logger.info(f"[{step_name}] 开始执行: {script_path}")
    try:
        # 修复了子进程输出编码导致的崩溃问题
        result = subprocess.run(
            [sys.executable, str(full_path)],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",  # <--- 核心修复：遇到无法解码的字节直接替换，防止崩溃
            timeout=600
        )
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
    try:
        result = subprocess.run(
            ["git"] + args,
            cwd=cwd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace", # <--- 此处也加上，防止 git 报错时出现乱码导致崩溃
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


def push_to_github() -> bool:
    logger.info("=" * 50)
    logger.info("开始推送文件到 GitHub...")

    if not (PROJECT_ROOT / ".git").exists():
        logger.error(f"错误：{PROJECT_ROOT} 不是一个 Git 仓库。")
        return False

    logger.info(f"添加文件到暂存区: {FILES_TO_PUSH}")
    if not run_git_command(["add"] + FILES_TO_PUSH, PROJECT_ROOT):
        logger.error("添加文件失败，中止推送。")
        return False

    commit_msg = f"Auto-update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    logger.info(f"提交更改，信息: {commit_msg}")
    if not run_git_command(["commit", "-m", commit_msg, "--allow-empty"], PROJECT_ROOT):
        logger.warning("提交失败或没有变更需要提交，继续尝试推送...")

    logger.info(f"推送到 {GITHUB_REPO_URL} ({GIT_BRANCH})...")
    if run_git_command(["push", "origin", GIT_BRANCH], PROJECT_ROOT):
        logger.info("推送成功！")
        return True
    else:
        logger.error("推送失败！请检查网络或 GitHub 认证配置。")
        return False


def main():
    logger.info("=" * 60)
    logger.info("自动化任务链开始执行")
    logger.info("=" * 60)

    os.chdir(PROJECT_ROOT)

    all_success = True
    failed_script = ""
    
    for script in SCRIPTS_TO_RUN:
        if not run_script(script, step_name=script):
            logger.error(f"脚本 {script} 执行失败，后续任务中止。")
            all_success = False
            failed_script = script
            break 

    if all_success:
        logger.info("所有数据生成脚本执行成功。")
        if not push_to_github():
            send_failure_email("数据脚本执行成功，但推送到 GitHub 失败！请检查网络或认证配置。")
    else:
        logger.error("由于前置脚本执行失败，跳过 GitHub 推送步骤。")
        send_failure_email(f"前置数据生成脚本执行失败！\n失败的脚本是: {failed_script}\n请查看日志文件排查原因。")

    logger.info("=" * 60)
    logger.info("自动化任务链执行结束")
    logger.info("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.exception("自动化主脚本发生未捕获的异常！")
        send_failure_email(f"主脚本发生未捕获异常，程序被迫中止。\n错误信息: {str(e)}")
        sys.exit(1)