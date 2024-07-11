import hashlib
from bitarray import bitarray
import sqlite3
import json
import matplotlib.pyplot as plt

from BloomFilter import BloomFilter,hash_func_1, hash_func_2, hash_func_crc32, hash_func_sha1

# 创建一个 Bloom Filter 实例
# size_of_filter = 100  # Bloom Filter 的大小
# num_hash_functions = 2  # 使用的哈希函数数量

# 测试的 Bloom Filter 大小范围
sizes = range(10, 201, 10)
num_hash_funcs = range(1, 6, 2)  # 哈希函数数量从 1 到 5
hash_functions = [hash_func_1, hash_func_2, hash_func_crc32, hash_func_sha1]
false_positive_rates = []
# 字典来存储每种情况的误判率
false_positive_rates = {size: {} for size in sizes}

# 假设 blacklist 是一个包含邮件地址的集合
blacklist = set([
    "microsoft-noreply@microsoft.com",
    "Azure@promomail.microsoft.com",
    "no-reply@zoom.us",
    "teamzoom@e.zoom.us",
    "no-reply@piazza.com",
    "support=bagevent.com@email.bagevent.com",
    "support@bagevent.com",
    "quarantine@messaging.microsoft.com"
])
# bloom_filter = BloomFilter(size_of_filter, [hash_func_1, hash_func_2])
# # 将黑名单中的邮件地址添加到 Bloom Filter 中
# for item in blacklist:
#     bloom_filter.add(item)

# 连接到 SQLite 数据库（如果数据库不存在会自动创建）
conn = sqlite3.connect('emails_draw.db')
c = conn.cursor()

# 创建表
c.execute('''
CREATE TABLE IF NOT EXISTS emails (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    etag TEXT,
    email_id TEXT,
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
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    etag TEXT,
    email_id TEXT,
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

# 打印读取的数据以调试
print("读取的数据：")
print(data[:1500])  # 打印前1000个字符以检查格式

# 尝试解析 JSON 数据
try:
    emails = json.loads(data)
    emails = emails.get("value", [])
except json.JSONDecodeError as e:
    print(f"Error decoding JSON: {e}")
    exit(1)

for size in sizes:
    for num_funcs in num_hash_funcs:
        selected_funcs = hash_functions[:num_funcs]  # 选择前 num_funcs 个哈希函数
        bloom_filter = BloomFilter(size, selected_funcs)

        spam_count = 0
        # 将黑名单中的邮件地址添加到 Bloom Filter 中
        for item in blacklist:
            bloom_filter.add(item)

        # 处理每个邮件信息
        # 检查每封邮件是否被误判为垃圾邮件
        false_positives = 0
        for email_data in emails:

            try:
                new_email_address = email_data["sender"]["emailAddress"]["address"]
                # 使用布隆过滤器检查邮箱地址
                if bloom_filter.contains(new_email_address):
                    # print(f"New email {new_email_address} is spam")
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
                    if new_email_address not in blacklist:
                        false_positives += 1

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
                print(f"Missing key in email data: {e}")
                continue
            except TypeError as e:
                print(f"Type error in email data: {e}")
                continue

        print(f"Bloom Filter 中设置为 1 的位的数量：{bloom_filter.count_bits()}")
        print(f"垃圾邮件数量：{spam_count}")
        print(f"误判数量：{spam_count - 43}")

        total_emails = len(emails)
        false_positive_rate = false_positives / total_emails if total_emails > 0 else 0
        false_positive_rates[size][num_funcs] = false_positive_rate

# 提交事务并关闭连接
conn.commit()
conn.close()

# 绘制结果
for num_funcs in num_hash_funcs:
    rates = [false_positive_rates[size][num_funcs] for size in sizes]
    plt.plot(sizes, rates, marker='o',  label=f'{num_funcs} hash functions', markersize = 5)

plt.title('Bloom Filter False Positive Rate by Size and Hash Functions')
plt.xlabel('Size of Bloom Filter')
plt.ylabel('False Positive Rate')
plt.legend()
plt.grid(True)
plt.show()