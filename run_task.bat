@echo off
chcp 65001
cd /d "D:\工作资料\专家个人主页\github_repo\junlanfeng"

echo ======================================== >> task_log.txt
echo Start at: %date% %time% >> task_log.txt

:: 执行 Python 脚本，并把所有的正常输出和报错（2>&1）都追加写到 task_log.txt 里
"C:\Users\H\AppData\Local\Programs\Python\Python312\python.exe" run_all.py >> task_log.txt 2>&1

echo Finished at: %date% %time% >> task_log.txt