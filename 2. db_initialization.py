import hashlib
from bitarray import bitarray
import sqlite3
import json

from BloomFilter import BloomFilter,hash_func_1, hash_func_2, hash_func_crc32
from black_list import get_blacklist_from_db, initialize_blacklist_and_bloom_filter

# 创建一个 Bloom Filter 实例
size_of_filter = 150  # Bloom Filter 的大小
num_hash_functions = 3  # 使用的哈希函数数量
bloom_filter = BloomFilter(size_of_filter, [hash_func_1, hash_func_2, hash_func_crc32])

initialize_blacklist_and_bloom_filter()

# 从数据库获取黑名单集合
blacklist = get_blacklist_from_db()

# 将黑名单中的邮件地址添加到 Bloom Filter 中
for item in blacklist:
    bloom_filter.add(item)

def Initialization():
    # 连接到 SQLite 数据库（如果数据库不存在会自动创建）
    conn = sqlite3.connect('emails.db')
    c = conn.cursor()

    # 创建表
    c.execute('''
    CREATE TABLE IF NOT EXISTS emails (
        id INTEGER,
        etag TEXT,
        email_id TEXT PRIMARY KEY,
        sent_date TEXT,
        subject TEXT,
        body_preview TEXT,
        importance TEXT,
        is_read BOOLEAN,
        sender_name TEXT,
        sender_address TEXT
    )
    ''')

    c.execute('''
    CREATE TABLE IF NOT EXISTS spam_emails (
        id INTEGER,
        etag TEXT,
        email_id TEXT PRIMARY KEY,
        sent_date TEXT,
        subject TEXT,
        body_preview TEXT,
        importance TEXT,
        is_read BOOLEAN,
        sender_name TEXT,
        sender_address TEXT
    )
    ''')


    # 从文件中读取邮件信息
    with open('outlook_email_updated.json', 'r') as f:
        data = f.read()

    # # 打印读取的数据以调试
    # print("读取的数据：")
    # print(data[:1500])  # 打印前1000个字符以检查格式

    # 尝试解析 JSON 数据
    try:
        emails = json.loads(data)
        emails = emails.get("value", [])
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        exit(1)

    spam_count = 0
    # 处理每个邮件信息
    for email_data in emails:
        try:
            new_email_address = email_data["sender"]["emailAddress"]["address"]

            # 使用布隆过滤器检查邮箱地址
            if bloom_filter.contains(new_email_address):
                print(f"New email {new_email_address} is spam")
                spam_count += 1
                c.execute('''
                    INSERT INTO spam_emails (
                        etag, email_id, sent_date, subject, body_preview, importance, is_read, sender_name, sender_address
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    email_data["@odata.etag"],
                    email_data["id"],
                    email_data["sentDateTime"],
                    email_data["subject"],
                    email_data["bodyPreview"],
                    email_data["importance"],
                    email_data["isRead"],
                    email_data["sender"]["emailAddress"]["name"],
                    new_email_address
                ))
            else:
                #print(f"New email {new_email_address} is not spam")
                c.execute('''
                    INSERT INTO emails (
                        etag, email_id, sent_date, subject, body_preview, importance, is_read, sender_name, sender_address
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    email_data["@odata.etag"],
                    email_data["id"],
                    email_data["sentDateTime"],
                    email_data["subject"],
                    email_data["bodyPreview"],
                    email_data["importance"],
                    email_data["isRead"],
                    email_data["sender"]["emailAddress"]["name"],
                    new_email_address
                ))
        except KeyError as e:
            print(email_data)
            print(f"Missing key in email data: {e}")
            continue
        except TypeError as e:
            print(f"Type error in email data: {e}")
            continue

    print(f"Number of Bits of Bloom Filter set to 1：{bloom_filter.count_bits()}")
    print(f"Number of spam emails：{spam_count}")
    print(f"False Positive：{spam_count - 30}")
    # 提交事务并关闭连接
    conn.commit()
    conn.close()

Initialization()
