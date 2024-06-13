import requests
import time
import logging

# 设置日志记录
logging.basicConfig(filename='springer_api_errors.log', level=logging.ERROR, format='%(asctime)s %(message)s')

# 替换为您的 Springer Nature API Key
API_KEY = "997a61ef5128a7bf36fcbd854ab9691e"

# Springer Nature API 端点
BASE_URL = "http://api.springernature.com/meta/v2/json"

def search_springer(query, start, batch_size):
    # 定义查询参数，包括查询词、起始位置、每批次的记录数和日期范围
    params = {
        "q": query,
        "s": start,
        "p": batch_size,
        "date-facet-end": "2010-01-01",  # 限制文献日期在2010年以后
        "api_key": API_KEY  # 确保API密钥在参数中传递
    }
    response = requests.get(BASE_URL, params=params, timeout=30)  # 设置请求超时时间
    response.raise_for_status()  # 检查请求是否成功
    return response.json()

def fetch_and_save_abstracts(query, max_results, batch_size, save_path, max_retries=5):
    record_count = 0
    with open(save_path, 'w', encoding='utf-8') as f:
        for start in range(1, max_results + 1, batch_size):
            retry_count = 0
            while retry_count < max_retries:
                try:
                    data = search_springer(query, start, batch_size)
                    for record in data.get('records', []):
                        record_count += 1
                        abstract = record.get('abstract', 'No abstract available')
                        f.write(f"Record {record_count}:\n")
                        f.write(abstract + "\n\n")
                    print(f"Fetched {len(data['records'])} records from start {start}.")
                    time.sleep(1)  # 避免过于频繁的请求
                    break  # 成功获取数据，退出重试循环
                except requests.exceptions.HTTPError as e:
                    logging.error(f"Failed to retrieve data from Springer API: {e} (start: {start})")
                    retry_count += 1
                    if retry_count < max_retries:
                        print(f"Waiting for 60 seconds before retrying... (Attempt {retry_count}/{max_retries})")
                        time.sleep(60)  # 如果请求失败，等待一段时间后继续
                    else:
                        print(f"Failed after {max_retries} attempts. Moving to the next batch.")
                        break  # 超过最大重试次数，退出重试循环
                except requests.exceptions.RequestException as e:
                    logging.error(f"Request failed: {e} (start: {start})")
                    print(f"Request failed: {e}")
                    retry_count += 1
                    if retry_count < max_retries:
                        print(f"Waiting for 60 seconds before retrying... (Attempt {retry_count}/{max_retries})")
                        time.sleep(60)  # 如果请求失败，等待一段时间后继续
                    else:
                        print(f"Failed after {max_retries} attempts. Moving to the next batch.")
                        break  # 超过最大重试次数，退出重试循环
    print(f"Saved {record_count} records to {save_path}.")

# 设置查询参数
QUERY = "catalysis"
MAX_RESULTS = 1000000  # 您想要获取的最大结果数量
BATCH_SIZE = 10000  # 每批次请求的记录数
SAVE_PATH = "springer_abstracts.txt"  # 保存结果的路径

# 获取并保存摘要
fetch_and_save_abstracts(QUERY, MAX_RESULTS, BATCH_SIZE, SAVE_PATH)
