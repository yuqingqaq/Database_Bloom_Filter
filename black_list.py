import hashlib
import pickle
import sqlite3
import json
import sys

from BloomFilter import BloomFilter, hash_func_1, hash_func_2, hash_func_crc32

# 创建一个 Bloom Filter 实例
size_of_filter = 150  # Bloom Filter 的大小
num_hash_functions = 3  # 使用的哈希函数数量
# 假设 blacklist 是一个包含邮件地址的集合
blacklist = set([
    "microsoft-noreply@microsoft.com",
    "no-reply@zoom.us",
    "teamzoom@e.zoom.us",
    "no-reply@piazza.com",
    "support=bagevent.com@email.bagevent.com",
    "support@bagevent.com",
    "quarantine@messaging.microsoft.com"
])

def save_bloom_filter(bloom_filter, conn):
    # 序列化布隆过滤器
    bf_data = pickle.dumps(bloom_filter)
    c = conn.cursor()
    # 存储序列化后的布隆过滤器到数据库
    c.execute('REPLACE INTO bloom_filter (id, data) VALUES (1, ?)', (bf_data,))
    print("Bloomfilter updated")
    conn.commit()

def load_bloom_filter(conn):
    c = conn.cursor()
    c.execute('SELECT data FROM bloom_filter WHERE id = 1')
    result = c.fetchone()
    if result:
        # 反序列化布隆过滤器
        return pickle.loads(result[0])
    else:
        # 返回 None 如果没有找到
        return None

def initialize_blacklist_and_bloom_filter():
    conn = sqlite3.connect('emails.db')
    c = conn.cursor()
    # 创建黑名单表和布隆过滤器表
    c.execute('CREATE TABLE IF NOT EXISTS blacklist (email TEXT UNIQUE)')
    c.execute('CREATE TABLE IF NOT EXISTS bloom_filter (id INTEGER PRIMARY KEY, data BLOB)')

    bloom_filter = BloomFilter(size_of_filter, [hash_func_1, hash_func_2, hash_func_crc32])
    for email in blacklist:
        c.execute('INSERT INTO blacklist (email) VALUES (?) ON CONFLICT(email) DO NOTHING', (email,))
        bloom_filter.add(email)

    # 保存布隆过滤器到数据库
    save_bloom_filter(bloom_filter, conn)
    conn.close()

def get_blacklist_from_db():
    conn = sqlite3.connect('emails.db')
    c = conn.cursor()
    try:
        c.execute('SELECT email FROM blacklist')
        blacklist_emails = c.fetchall()  # 获取所有行
        return {email[0] for email in blacklist_emails}  # 使用集合推导式来创建一个邮件地址集合
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        return set()
    finally:
        conn.close()

def process_email_input(email_data):
    # 连接到 SQLite 数据库（如果数据库不存在会自动创建）
    conn = sqlite3.connect('emails.db')
    c = conn.cursor()

    # 确保表存在
    c.execute('''CREATE TABLE IF NOT EXISTS spam_emails (email TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS emails (email TEXT)''')

    # 获取发件人地址
    new_email_address = email_data["sender"]["emailAddress"]["address"]

    bloom_filter = load_bloom_filter(conn)
    # 使用布隆过滤器检查邮箱地址
    if bloom_filter.contains(new_email_address):
        print(f"New email {new_email_address} is spam")
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
        print(f"New email {new_email_address} is not spam")
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

    # 提交事务并关闭连接
    conn.commit()
    conn.close()

def add_to_blacklist(email):
    conn = sqlite3.connect('emails.db')
    c = conn.cursor()
    bloom_filter = load_bloom_filter(conn)

    c.execute('''INSERT INTO blacklist (email) VALUES (?) ON CONFLICT(email) DO NOTHING''', (email,))
    # 检查是否真的添加了新邮箱（如果邮箱已存在，则不添加到布隆过滤器）
    if c.rowcount > 0:
        bloom_filter.add(email)
        # 保存更新后的布隆过滤器到数据库
        save_bloom_filter(bloom_filter, conn)
        refresh_emails(conn)  # 重新分类邮件

    conn.commit()
    conn.close()

def refresh_emails(conn):
    # conn = sqlite3.connect('emails.db')
    c = conn.cursor()

    # 读取普通邮件表中的所有邮件
    c.execute('SELECT * FROM emails')
    emails = c.fetchall()

    bloom_filter = load_bloom_filter(conn)
    move_count = 0

    # 准备 SQL 语句
    check_spam_email = 'SELECT COUNT(*) FROM spam_emails WHERE email_id = ?'
    move_to_spam = '''
    INSERT INTO spam_emails
    SELECT * FROM emails
    WHERE email_id = ? AND NOT EXISTS (
        SELECT 1 FROM spam_emails WHERE email_id = ?
    )
    '''
    delete_from_emails = 'DELETE FROM emails WHERE email_id = ?'

    for email in emails:
        email_id = email[2]  # 假设 id 在第三个位置
        email_address = email[9]  # 假设 sender_address 在第十个位置

        if bloom_filter.contains(email_address):
            c.execute(check_spam_email, (email_id,))
            if c.fetchone()[0] == 0:
                c.execute(move_to_spam, (email_id, email_id))
                c.execute(delete_from_emails, (email_id,))
                move_count += 1
            else:
                print(f"Email {email_id} already in spam.")

    print(f"{move_count} emails moved.")
    print()
    conn.commit()
