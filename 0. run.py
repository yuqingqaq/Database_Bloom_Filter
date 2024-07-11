import subprocess

# 定义要运行的脚本列表
scripts = [
      # 数据获取 - 使用Graph API 获取json数据 存入 outlook_email.json
      # 类定义 - BloomFilter add(), contains(), count_bit()

    '1. data_deduplicate.py',         # 数据预处理 - 根据标题subject去重（bloomfilter） 输出为outlook_email_update.json
                                      #          - compare_with_dict.py - 与字典比较空间和时间效率
                                      #          - 使用generate_random 生成140000封unique邮件 - random_emails.json

      # 对比实验 - draw_deduplicate_performance.py - 测试FPR、Time、Bits Set 与 size 的关系
      #         - draw_storage_fpr.py - 测试FPR与n的关系（与Theorectical对比）

      # spam 黑名单
      # 方法定义 - black_list 预定义黑名单set和blacklist_bloomfilter
      #         - a. 黑名单blacklist表和blacklist_bloomfilter init/get/add , 不可删除
      #                 - add  new blacklist address : refresh 表emails -> spam_emails
      #         - b. 添加新邮件时执行process_email_input : 判定放入哪个表
    '2. db_initialization.py',        # 数据库初始化 - 根据sender过滤spams（blacklist_bloomfilter）表emails/spam_emails
                                      #           - draw_init_fpr_size_hash.py - FPR与Bloom的位数、哈希函数数量k的关系 (m = 7)
    '3. add_email_to_blacklist.py',   # 添加邮箱到黑名单 -  同时对emails表进行同步
    '4. add_new_email.py',            # 添加部分新邮件到数据库中 - process_email_input

      # 拓展内容 - 可能对哪些邮件更感兴趣
    '5. filter_interested_emails.py'  # 对邮件正文进行分词
                                      # 根据关键词筛选出可能感兴趣的邮件并使用isRead字段校验 （interested_words_bloomfilter）
                                      # 使用filter_interested_emails.py中的test_keywords可测试哪些words影响更大
]

# 依次执行每个脚本
# 如果报错，删除emails.db
for script in scripts:
    subprocess.run(['python', script])

