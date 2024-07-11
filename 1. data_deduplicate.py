import hashlib
import time
import copy
import zlib
from bitarray import bitarray
import json
import matplotlib.pyplot as plt

from BloomFilter import BloomFilter, hash_func_1, hash_func_2, hash_func_crc32, hash_func_sha1

# 假设从 JSON 文件中读取邮件数据
json_file_path = "outlook_email.json"

with open(json_file_path, 'r', encoding='utf-8') as f:
    original_data = json.load(f)

data_processed = copy.deepcopy(original_data)
sizes_of_filter = [1500, 2500, 5000, 7500, 10000, 12500, 20000]

# 创建一个 Bloom Filter 实例
# size_of_filter = 10000  # Bloom Filter 的大小
# num_hash_functions = 5  # 使用的哈希函数数量

# 提取并去重邮件标题
processing_times = []
duplicate_counts = []
false_deletions = []
total_emails_after = []
bits_set = []

for size in sizes_of_filter:
    start_time = time.time()
    bloom_filter = BloomFilter(size, [hash_func_1, hash_func_2, hash_func_crc32, hash_func_sha1])

    print(f"删除前总邮件数量：{len(original_data['value'])}")
    # 用于存储最新邮件的字典，键为邮件标题，值为最新邮件的信息
    latest_emails = {}
    filtered_emails = []
    duplicate_count = 0

    for email in original_data['value']:
        email_subject = email['subject']

        # 使用 Bloom Filter 进行去重
        if bloom_filter.contains(email_subject):
            # 如果标题已经存在，判断是否更新为更新的邮件
            if email_subject in latest_emails:
                # 比较发送时间，保留更新的邮件
                if email['sentDateTime'] >= latest_emails[email_subject]['sentDateTime']:
                    # 更新最新的邮件信息
                    latest_emails[email_subject] = {
                        'id': email['id'],
                        'subject': email['subject'],
                        'sentDateTime': email['sentDateTime']
                    }
            else:
                # 第一次遇到该标题，直接添加
                latest_emails[email_subject] = {
                    'id': email['id'],
                    'subject': email['subject'],
                    'sentDateTime': email['sentDateTime']
                }
            # print(f"删除重复邮件：{email['subject']}")
            duplicate_count += 1
        else:
            # 如果标题不存在，添加到 Bloom Filter 中
            bloom_filter.add(email_subject)
            # 同时将该邮件添加到最新邮件字典中
            latest_emails[email_subject] = {
                'id': email['id'],
                'subject': email['subject'],
                'sentDateTime': email['sentDateTime']
            }
            # 将不重复的邮件添加到输出列表
            filtered_emails.append(email)

    end_time = time.time()
    total_time = end_time - start_time

    processing_times.append(total_time)
    duplicate_counts.append(duplicate_count)
    false_deletions.append(duplicate_count - 188)
    total_emails_after.append(len(filtered_emails))
    bits_set.append(bloom_filter.count_bits())

    # 更新原始 JSON 数据，只保留最新的邮件
    data_processed['value'] = filtered_emails

    print(f"处理时间：{total_time}秒")
    print(f"删除的重复邮件数量：{duplicate_count}")
    print(f"Bloom Filter 中设置为 1 的位的数量：{bloom_filter.count_bits()}")
    print(f"误删数量：{duplicate_count - 186}")
    print(f"删除后总邮件数量：{len(data_processed['value'])}")
    print()


# 定义新文件的路径
new_json_file_path = json_file_path.replace('.json', '_updated.json')

# 将更新后的 JSON 数据写入新文件
with open(new_json_file_path, 'w', encoding='utf-8') as f:
    json.dump(data_processed, f, ensure_ascii=False, indent=4)

# print(f"已在文件 {json_file_path} 中删除早期的重复邮件条目并保存最新数据。")

# 绘制图表
plt.figure(figsize=(12, 6))

plt.subplot(2, 2, 1)
plt.plot(sizes_of_filter, false_deletions, label="MisDeleted Count", marker='o')
plt.title("MisDeleted Count")
plt.xlabel("Size of Bloom Filter ")
plt.ylabel("Count")
plt.xscale('log')  # 设置x轴为对数尺度
plt.yscale('log')  # 设置y轴为对数尺度

plt.subplot(2, 2, 2)
plt.plot(sizes_of_filter, total_emails_after, label="Total Number after Deletion", marker='o')
plt.title("Total Number after Deletion")
plt.xlabel("Size of Bloom Filter ")
plt.ylabel("Count")
plt.xscale('log')  # 设置x轴为对数尺度
plt.yscale('log')  # 设置y轴为对数尺度

plt.subplot(2, 2, 3)
plt.plot(sizes_of_filter, processing_times, label="Time Used", marker='o')
plt.title("Time Used")
plt.xlabel("Size of Bloom Filter ")
plt.ylabel("Time(s)")
plt.xscale('log')  # 设置x轴为对数尺度
plt.yscale('log')  # 设置y轴为对数尺度

plt.subplot(2, 2, 4)
plt.plot(sizes_of_filter, bits_set, label="Number of bits set to 1", marker='o')
plt.title("Number of bits set to 1")
plt.xlabel("Size of Bloom Filter ")
plt.ylabel("Bit")
plt.xscale('log')  # 设置x轴为对数尺度
plt.yscale('log')  # 设置y轴为对数尺度

plt.tight_layout()
plt.show()