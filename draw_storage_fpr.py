import time
import json
from pympler import asizeof
from BloomFilter import BloomFilter, hash_func_1, hash_func_2, hash_func_crc32, hash_func_sha1, hash_func_murmur
import matplotlib.pyplot as plt
import math

# 加载邮件数据
json_file_path = "random_emails.json"
with open(json_file_path, 'r', encoding='utf-8') as f:
    original_data = json.load(f)

test_json_file_path = "outlook_email.json"
with open(test_json_file_path, 'r', encoding='utf-8') as f:
    test_data = json.load(f)


def deduplicate_with_dict(emails):
    seen = {}
    for email in emails['value']:
        email_id = email['id']
        if email_id not in seen:
            seen[email_id] = email
    memory_usage = asizeof.asizeof(seen)
    return len(seen), memory_usage

def deduplicate_with_bloom_filter(size, emails):
    bloom_filter = BloomFilter(size, [hash_func_1, hash_func_2, hash_func_crc32, hash_func_sha1, hash_func_murmur])
    unique_count = 0

    for email in emails['value']:
        email_id = email['id']
        if not bloom_filter.contains(email_id):
            bloom_filter.add(email_id)
            unique_count += 1  # 只计数，不存储邮件详情

    memory_usage = asizeof.asizeof(bloom_filter)
    return unique_count, memory_usage


def deduplicate_with_bloom_filter_test(size, emails, test_emails):
    bloom_filter = BloomFilter(size, [hash_func_1, hash_func_2, hash_func_crc32, hash_func_sha1, hash_func_murmur])
    unique_count = 0

    # 添加阶段
    for email in emails['value']:
        email_id = email['id']
        bloom_filter.add(email_id)

    # 测试阶段
    false_positive_count = 0
    for test_email in test_emails['value']:
        test_id = test_email['id']
        if bloom_filter.contains(test_id):
            false_positive_count += 1

    memory_usage = asizeof.asizeof(bloom_filter)
    fpr = false_positive_count / len(test_emails['value'])  # 计算误报率
    return unique_count, memory_usage, fpr

sizes = range(2000000, 3500001, 300000)
def collect_data(emails, test_emails):
    results = {
        "bloom_memory": [],
        "bloom_test_fprs": [],
        "fprs": []
    }
    dict_count, dict_memory = deduplicate_with_dict(emails)

    for size in sizes:
        count, bloom_memory= deduplicate_with_bloom_filter(size, emails)

        count_test, bloom_memory_test, fpr_test = deduplicate_with_bloom_filter_test(size, emails, test_emails)
        fpr = (dict_count - count) / dict_count
        results["bloom_memory"].append(bloom_memory)
        results["fprs"].append(fpr * 100)
        results['bloom_test_fprs'].append(fpr_test)

    print(results["bloom_memory"])
    # print(results['fprs'])

    return sizes, results

sizes, results = collect_data(original_data, test_data)

k = 5
n = 140000

times = []
for m in sizes:
    times.append(m/n)

# 计算理论误报率
theoretical_fprs = []
for m in sizes:
    fpr = (1 - math.exp(-k * n / m)) ** k
    theoretical_fprs.append(fpr)

def bloom_filter_false_positive_rate(n, m, k):
    p = (1 - 1/m)**(k*n)
    return (1 - p)**k

# fpr_results = []
# # Loop through each size m to simulate and plot
# for m in sizes:
#     false_positive_rates = [bloom_filter_false_positive_rate(i, m, k) for i in range(1, n + 1)]
#     fpr_results.append(sum(false_positive_rates) / len(false_positive_rates))


# 绘图
plt.figure(figsize=(8, 6))
plt.plot(times, results["fprs"], label='Actual FPR (during insertion)', marker='o')
plt.plot(times, results["bloom_test_fprs"], label='Actual FPR (with test set)', marker='o')
plt.plot(times, theoretical_fprs, label='Theoretical FPR', marker='o', linestyle='--')
# plt.plot(times, fpr_results, label='Theorectical FPR (during insertion)', marker='--')

plt.title("False Positive Rate vs Theoretical")
plt.xlabel("Bloom Filter Size (as multiples of element count n)")
plt.ylabel("False Positive Rate (%)")
plt.legend(fontsize='large')
plt.grid(True)

plt.show()