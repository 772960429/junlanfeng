import requests
import json
import os

# 从环境变量读取密钥（如果有）
token = os.environ.get('token', '')
cookie = os.environ.get('cookie', '')
url = 'https://api.github.com/repos/octocat/Hello-World/issues'
response = requests.get(url)
data = response.json()
with open('issues.json', 'w') as f:
    json.dump(data, f, indent=2)
print('Data saved to issues.json')
print(f'token is {token}, cookie is {cookie}')