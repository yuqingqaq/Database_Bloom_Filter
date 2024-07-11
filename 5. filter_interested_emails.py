import time

import jieba
import re
import sqlite3
import time


from BloomFilter import BloomFilter, hash_func_1, hash_func_2, hash_func_crc32,hash_func_murmur

size_of_filter = 1000  # Bloom Filter 的大小
num_hash_functions = 4  # 使用的哈希函数数量
bloom_filter = BloomFilter(size_of_filter, [hash_func_1, hash_func_2, hash_func_crc32, hash_func_murmur])
# 感兴趣的关键词
interest_keywords = ['人工智能', 'AI', 'database', 'machine learning', 'NLP', 'AR', 'college'
                     '数据分析', '数据科学', '程序设计', 'coding', '信息技术',
                     '麦当劳', '食堂', '校车', '奖学金', '留学', '课程安排', '学院'
                     '实习机会', 'job opportunities', '企业参访', '招新'
                     '电影放映', '景点', '游泳比赛', '音乐会', 'concert', '音乐节', '体育',
                     '心理健康', 'mental health', '心理咨询']

# interest_keywords = [
#                     "人工智能", "机器学习", "深度学习", "神经网络", "算法", "AI", "machine learning",
#                     "大数据", "数据分析", "数据科学", "big data", "data analysis", "data science",
#                     "编程", "软件开发", "程序设计", "coding", "software development", "programming",
#                     "自然语言处理", "NLP", "natural language processing", "机器人技术", "robotics",
#                     "虚拟现实", "VR", "virtual reality", "增强现实", "AR", "augmented reality",
#                     "操作系统", "operating system", "网络安全", "cyber security",
#                     "信息技术", "information technology", "学术研究", "academic research",
#                     "科研项目", "scientific project", "学术会议", "academic conference",
#                     "实习机会", "internship opportunities", "就业信息", "job opportunities",
#                     "奖学金", "scholarship", "留学", "study abroad", "课程安排", "course schedule",
#                     "电子游戏", "video games", "电影放映", "movie screening", "音乐会", "concert",
#                     "游泳比赛", "swimming competition", "合唱节", "choral festival", "心理咨询", "psychological counseling"
# ]
for keyword in interest_keywords:
    bloom_filter.add(keyword)

def initialize_interested_emails_db():
    conn = sqlite3.connect('emails.db')
    cursor = conn.cursor()
    cursor.execute('DROP TABLE IF EXISTS interested_emails')
    cursor.execute('''
    CREATE TABLE interested_emails (
        email_id TEXT PRIMARY KEY,
        subject TEXT,
        body_preview TEXT,
        sent_date TEXT,
        is_read BOOLEAN
    )
    ''')
    conn.commit()
    conn.close()

# def contains_interesting_content(content, interest_keywords):
#     return any(keyword in content for keyword in interest_keywords)

# 检查一篇文章是否包含感兴趣的内容
def contains_interesting_content(content):
    # 使用 jieba 分词
    words = jieba.cut(content)
    # 使用正则表达式进一步分割英文和数字
    processed_words = []
    for word in words:
        processed_words.extend(re.split(r'(\d+|\s+)', word))  # 分割数字和空格
    # 清理分词结果
    clean_words = [word.strip().lower() for word in processed_words if word.strip()]
    for word in clean_words:
        if bloom_filter.contains(word):
            return True
    return False

def filter_emails_and_insert():
    conn = sqlite3.connect('emails.db')
    cursor = conn.cursor()
    cursor.execute('SELECT email_id, subject, body_preview, sent_date, is_read FROM emails')
    emails = cursor.fetchall()

    for email in emails:
        email_id, subject, body_preview, sent_date, is_read = email
        if contains_interesting_content(body_preview):
            cursor.execute('''
                INSERT OR IGNORE INTO interested_emails (email_id, subject, body_preview, sent_date, is_read)
                VALUES (?, ?, ?, ?, ?)
            ''', (email_id, subject, body_preview, sent_date, is_read))
    conn.commit()
    conn.close()


def calculate_read_percentage():
    conn = sqlite3.connect('emails.db')
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM interested_emails')
    total_emails = cursor.fetchone()[0]
    cursor.execute('SELECT COUNT(*) FROM interested_emails WHERE is_read = 1')
    read_emails = cursor.fetchone()[0]
    read_percentage = (read_emails / total_emails) * 100 if total_emails > 0 else 0
    conn.close()
    return read_percentage


# 初始化数据库和邮件筛选
initialize_interested_emails_db()

start_time = time.time()
filter_emails_and_insert()

# # 进行关键词测试
# remaining_keywords = test_keywords(interest_keywords)
# print("Remaining keywords after testing:", remaining_keywords)
#
# # 初始化数据库和邮件筛选
# initialize_interested_emails_db()
# filter_emails_and_insert(remaining_keywords)

end_time = time.time()
print(f"time : {end_time - start_time}")
read_percentage = calculate_read_percentage()
print(f"The percentage of read emails in 'interested_emails' is: {read_percentage:.2f}%")


# def test_keywords(interest_keywords):
#     original_percentage = calculate_read_percentage()
#
#     test_keywords = interest_keywords[:]
#     for keyword in interest_keywords:
#         new_keywords = [k for k in test_keywords if k != keyword]
#         initialize_interested_emails_db()
#         filter_emails_and_insert(new_keywords)
#         new_percentage = calculate_read_percentage()
#         percentage_change = original_percentage - new_percentage
#         print(keyword, percentage_change)
#
#         if abs(percentage_change) <= 0.1:
#             test_keywords.remove(keyword)
#             print(f"Keyword '{keyword}' removed permanently.")
#         else :
#             print(f"Restoring keyword '{keyword}' due to significant impact: {percentage_change:.2f}% decrease.")
#
#
#     return test_keywords
