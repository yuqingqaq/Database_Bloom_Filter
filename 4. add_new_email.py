import hashlib
from bitarray import bitarray
import sqlite3
import json
import sys

from black_list import process_email_input

# 从文件中读取邮件信息
with open('new_email.json', 'r') as f:
    data = f.read()

# 尝试解析 JSON 数据
try:
    emails = json.loads(data)
    emails = emails.get("value", [])
except json.JSONDecodeError as e:
    print(f"Error decoding JSON: {e}")
    exit(1)

spam_count = 0
for email_data in emails:
    try:
        new_email_address = email_data["sender"]["emailAddress"]["address"]
        # 调用处理函数
        process_email_input(email_data)

    except KeyError as e:
        print(email_data)
        print(f"Missing key in email data: {e}")
        continue
    except TypeError as e:
        print(f"Type error in email data: {e}")
        continue


