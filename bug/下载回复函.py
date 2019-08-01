import random
import requests
import concurrent.futures as futures
import queue
import pandas as pd
import time
import os

# 全局变量
# 文件夹路径
# folder_path = 'E:/files/files/'
folder_path = 'E:/files/剩余回复函/'
# url
url = 'http://reportdocs.static.szse.cn/UpFiles/fxklwxhj/'
# 加载文档
# df = pd.read_excel(r'E:\files\主板.xlsx', dtype='object')
df = pd.read_excel(r'E:\files\创业板下载.xlsx', dtype='object')
# 初始化任务队列
tasks_add = queue.Queue()
# headers
my_headers = [
    "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:30.0) Gecko/20100101 Firefox/30.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/537.75.14",
    "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Win64; x64; Trident/6.0)",
    'Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11',
    'Opera/9.25 (Windows NT 5.1; U; en)',
    'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)',
    'Mozilla/5.0 (compatible; Konqueror/3.5; Linux) KHTML/3.5.5 (like Gecko) (Kubuntu)',
    'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.0.12) Gecko/20070731 Ubuntu/dapper-security Firefox/1.5.0.12',
    'Lynx/2.8.5rel.1 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/1.2.9',
    "Mozilla/5.0 (X11; Linux i686) AppleWebKit/535.7 (KHTML, like Gecko) Ubuntu/11.04 Chromium/16.0.912.77 Chrome/16.0.912.77 Safari/535.7",
    "Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:10.0) Gecko/20100101 Firefox/10.0 "
]

# 代理
my_proxies = [
    {
        "http": "http://120.83.111.145:9999",
        "https": "https://120.83.111.145:9999"

    },
    {
        "http": "http://60.182.197.241:61234",
        "https": "https://60.182.197.241:61234"
    }
]


# 解析报告
def parse_report(url):
    # 循环处理每一条年报
    for i in range(0, len(df)):
        cl_type = df['函件类别'][i]
        code = df['公司代码'][i]
        name = df['公司简称'][i]
        url1 = df['公司回复'][i]
        time = df['发函日期'][i]

        file_name = str(cl_type) + '_' + str(time) + '_' + str(code) + '_' + str(name) + '_' + url1

        if file_name.count('*') > 0:
            file_name = file_name.replace('*', '星')
        file_path = folder_path + file_name
        url_ = url + url1
        tasks_add.put((file_path, url_))


# 下载文件
def download_file(file_path, url):
    # 下载前判断文件是否存在该路径下
    if os.path.exists(file_path):
        print("文件[{}]已存在\n".format(file_path))
        return
    # 安全地保存文件
    print("开始链接[{}\n".format(url))
    try:
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
            "Connection": "keep-alive",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
            # "Cookie": "searchGuide=sg; Hm_lvt_78c58f01938e4d85eaf619eae71b4ed1=1555233233,1556070733,1557209719; v=AulBqLFukcmt-a192Mr6L8EB-J5ntt36R6oBfIveZVAPUgPC0wbtuNf6EUgY"
        }
        headers["User-Agent"] = random.choice(my_headers)
        # 使用代理
        # response = requests.get(url, stream=True, timeout=60, headers=headers, proxies=random.choice(my_proxies))
        # 不使用代理
        response = requests.get(url, stream=True, timeout=60, headers=headers)
        if response.status_code == 200:
            print("开始下载[{}\n".format(file_path))
            with open(file_path, 'wb') as fd:
                for chunk in response.iter_content(128):
                    fd.write(chunk)
                print(file_path, '完成下载\n')
        else:
            # 连接出错，重新将该文件加入到任务队列
            print("连接出错:[{}],重新将该文件加入到任务队\n".format(str(response.status_code)))
            tasks_add.put((file_path, url))
    except Exception as exc:
        # 连接超时，重新将该文件加入到任务队列
        print(exc + '\n')
        # print("连接超时:[{}]，重新将该文件加入到任务队列".format(file_path))
        tasks_add.put((file_path, url))
    finally:
        response.close()


# 初始化
def init():
    # 解析报告
    parse_report(url)

    # 下载任务列表
    tasks_download = []

    # 初始化下载任务线程池
    start_time = time.time()
    with futures.ThreadPoolExecutor(4) as pool_download:
        # 开始下载任务
        while not tasks_add.empty():
            item = tasks_add.get()
            tasks_download.append(pool_download.submit(download_file, item[0], item[1]))

    # 等待线程池完成
    futures.wait(tasks_download, return_when=futures.ALL_COMPLETED)
    end_time = time.time()
    print("下载总共用时:", end_time - start_time)


# 遍历
def traverse():
    for row in df.iterrows():
        print(row[0], row[1][0], row[1][1])


if __name__ == "__main__":
    # 去掉回复函为空的行
    df = df.dropna(subset=["公司回复"])
    df = df.reset_index(drop=True)

    # 填充NaN值为上一行对应的数据
    df = df.fillna(method="pad")

    # 运行
    init()
