import hashlib
import time
import copy
import zlib
import json
import mmh3
import matplotlib.pyplot as plt
from BloomFilter import BloomFilter, hash_func_1, hash_func_2, hash_func_crc32, hash_func_sha1, hash_func_fnv1a, \
    hash_func_murmur

json_file_path = "outlook_email.json"
with open(json_file_path, 'r', encoding='utf-8') as f:
    original_data = json.load(f)

sizes_of_filter = [1000, 2000, 4000, 7000, 10000, 15000]
num_hash_functions_opts = [1, 2, 3, 4, 5]  # 可选的哈希函数数量

# 用于存储结果的字典
results = {}

for num_hash_functions in num_hash_functions_opts:
    hash_functions = [hash_func_1, hash_func_2, hash_func_sha1, hash_func_crc32, hash_func_fnv1a, hash_func_murmur][:num_hash_functions]
    processing_times = []
    duplicate_counts = []
    false_deletions = []
    bits_set = []

    for size in sizes_of_filter:
        start_time = time.time()
        bloom_filter = BloomFilter(size, hash_functions)
        latest_emails = {}
        duplicate_count = 0

        for email in original_data['value']:
            email_subject = email['subject']
            if bloom_filter.contains(email_subject):
                if email_subject in latest_emails:
                    if email['sentDateTime'] > latest_emails[email_subject]['sentDateTime']:
                        latest_emails[email_subject] = email
                duplicate_count += 1
            else:
                bloom_filter.add(email_subject)
                latest_emails[email_subject] = email

        end_time = time.time()
        processing_times.append(end_time - start_time)
        duplicate_counts.append(duplicate_count)
        false_deletions.append(duplicate_count - 186)
        bits_set.append(bloom_filter.count_bits())

    results[num_hash_functions] = {
        'sizes': sizes_of_filter,
        'processing_times': processing_times,
        'duplicate_counts': duplicate_counts,
        'false_deletions': false_deletions,
        'bits_set': bits_set
    }

fig, axs = plt.subplots(1, 3, figsize=(16, 4))  # 总体布局宽高比调整为4:3的比例
for num_hash_functions, data in results.items():
    axs[0].plot(data['sizes'], data['false_deletions'], label=f"Hash Func: {num_hash_functions}", marker='o')
    axs[1].plot(data['sizes'], data['processing_times'], label=f"Hash Func: {num_hash_functions}", marker='o')
    axs[2].plot(data['sizes'], data['bits_set'], label=f"Hash Func: {num_hash_functions}", marker='o')

for ax in axs:
    ax.set(xscale='log', yscale='log', xlabel='Size of Bloom Filter')
    ax.legend()

axs[0].set(title="False Deletions", ylabel="Count")
axs[1].set(title="Processing Time", ylabel="Time (s)")
axs[2].set(title="Bits Set", ylabel="Count", xscale='linear', yscale='linear')  # Bits Set 使用常规Y轴

plt.tight_layout()
plt.show()
