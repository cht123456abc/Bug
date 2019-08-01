import os

import requests
import concurrent.futures as futures
import queue
import pandas as pd
import time
import random

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

# 条件过滤
def filter(excel):
    for row in excel.itertuples():
        if row[4].find("延期") >= 0 or row[4].find("延迟") >= 0:
            # print(row)
            excel = excel.drop(row[0])
    excel = excel.reset_index(drop=True)
    return excel


# 从文件里面获取ip代理地址
def get_ip(file_path):
    my_proxies = []
    proxy = {}
    with open(file_path, "r") as f:
        for ip in f.readlines():
            ip = ip.strip()
            proxy["http"] = "http://" + ip
            proxy["https"] = "https://" + ip
            my_proxies.append(proxy)
    return my_proxies


# 解析报告
def parse_report(df, folder_path):
    # 解析出文件名与url
    for i in range(0, len(df)):
        code = df["证券代码"][i]
        time = df["公告日期"][i]
        title = df["标题"][i]
        if title.count('*') > 0:
            title = title.replace('*', '星')
        url = str(df["下载"][i])
        file_path = folder_path + title + '_' + time + '.pdf'
        tasks_add.put((file_path, url))


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
            "Cookie": "searchGuide=sg; Hm_lvt_78c58f01938e4d85eaf619eae71b4ed1=1555233233,1556070733,1557209719; v=AulBqLFukcmt-a192Mr6L8EB-J5ntt36R6oBfIveZVAPUgPC0wbtuNf6EUgY"
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


if __name__ == "__main__":
    # 获取excel
    df = pd.read_excel('/Users/cht/Documents/files/700多只公告1.xlsx')

    # 清理NaN数据
    df = df.reset_index(drop=True)
    df = df.dropna()

    # 条件过滤
    df = filter(df)
    print(df)

    # 获取ip代理地址
    my_proxies = get_ip("/Users/cht/Documents/files/XCProxy.txt")

    # 文件夹路径
    folder_path = '/Users/cht/Documents/files/files/'

    # 初始化任务队列
    tasks_add = queue.Queue()
    parse_report(df, folder_path)

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
    print("下载总共用时:[{}]秒".format(end_time - start_time))
