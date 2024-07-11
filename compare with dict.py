import time
import json
import sys
from pympler import asizeof
from BloomFilter import BloomFilter, hash_func_1, hash_func_2, hash_func_crc32, hash_func_sha1, hash_func_murmur

# 假设从 JSON 文件中读取邮件数据
json_file_path = "random_emails.json"
# json_file_path = "random_emails.json"
with open(json_file_path, 'r', encoding='utf-8') as f:
    original_data = json.load(f)

size = 1500000
# 使用 Bloom Filter 进行去重
def deduplicate_with_bloom_filter(emails):
    bloom_filter = BloomFilter(size, [hash_func_1, hash_func_2, hash_func_crc32, hash_func_sha1, hash_func_murmur])
    unique_count = 0
    start_time = time.time()

    for email in emails['value']:
        email_id = email['id']
        if not bloom_filter.contains(email_id):
            bloom_filter.add(email_id)
            unique_count += 1  # 只计数，不存储邮件详情

    end_time = time.time()
    memory_usage = asizeof.asizeof(bloom_filter)
    return unique_count, end_time - start_time, memory_usage

# 使用字典进行去重
def deduplicate_with_dict(emails):
    seen = {}
    start_time = time.time()
    for email in emails['value']:
        email_id = email['id']
        if email_id not in seen:
            seen[email_id] = email
    end_time = time.time()
    memory_usage = asizeof.asizeof(seen)
    return seen, end_time - start_time, memory_usage

# 进行去重并测量效率和内存使用
count, time_bloom, mem_bloom = deduplicate_with_bloom_filter(original_data)
latest_emails_dict, time_dict, mem_dict = deduplicate_with_dict(original_data)

count_dict = len(latest_emails_dict)
fpr = (count_dict - count)/ count_dict
memory_ratio = mem_dict / mem_bloom if mem_bloom != 0 else float('inf')
print(f"Size of Bloom Filter: {size} ")
print(f"Bloom Filter: {count} unique emails, Time taken: {time_bloom:.4f} seconds, Memory used: {mem_bloom} bytes")
print(f"Dictionary: {count_dict} unique emails, Time taken: {time_dict:.4f} seconds, Memory used: {mem_dict} bytes")
print(f"Dictionary memory usage is {memory_ratio:.2f} times the memory used by Bloom Filter.")
print(f"False Positive Rate: {fpr* 100:.4f}%")