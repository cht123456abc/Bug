import json

import requests  # 注意需要在运行前做好 pip install requests
from contextlib import closing
import concurrent.futures as futures
import queue
import pandas as pd
import time


# 解析报告
def parse_report(url):
    # response = requests.get(url, headers=headers)
    with requests.get(url, headers=headers) as response:
        if response.status_code == 200:
            json_str = response.text[19:-1]
            data = json.loads(json_str)
            for report in data['result']:
                # 整理出下载地址与文件名
                download_url = 'http://' + report['docURL']
                file_name = report['extWTFL'] + '_' + report['createTime'][:11] + '_' + report['stockcode'] + '_' + \
                            report[
                                'docTitle'] + '.pdf'
                if file_name.count('*') > 0:  # 如果文件名里面含有'*'号会发生错误
                    file_name = file_name.replace('*', '#')

                file_path = folder_path + file_name
                tasks_add.put((file_path, download_url))

        else:
            print("连接出错:", response.status_code)



# 下载文件
def download_file(file_path, url):
    # 安全地保存文件
    # print(">>>开始连接:",url)
    with closing(requests.get(url, stream=True)) as response:
        if response.status_code == 200:
            # print(">>>>开始下载:",file_path)
            with open(file_path, 'wb') as fd:
                for chunk in response.iter_content(128):
                    fd.write(chunk)
                print(file_path, '完成下载')
        else:
            print(">>>>连接出错," + str(response.status_code))


if __name__ == "__main__":
    # df = pd.read_excel(r'C:\Users\菲哥哥\导师 科研\毕业论文\问询函处理\深证\问询函合集.xlsx')
    folder_path = 'E:/files/files/'
    url = 'http://query.sse.com.cn/commonSoaQuery.do?jsonCallBack=jsonpCallback39639&siteId=28&sqlId=BS_GGLL&extGGLX=&stockcode=&channelId=10743%2C10744%2C10012&extGGDL=&order=createTime%7Cdesc%2Cstockcode%7Casc&isPagination=true&pageHelp.pageSize=15&pageHelp.pageNo='
    url1 = '&pageHelp.beginPage=1&pageHelp.cacheSize=1&pageHelp.endPage=5&_=1545971992685'
    headers = {'Accept': '*/*',
               'Accept-Encoding': 'gzip, deflate',
               'Accept-Language': 'zh-CN,zh;q=0.9',
               'Connection': 'keep-alive',
               'Cookie': 'yfx_c_g_u_id_10000042=_ck18122812392810979079850594013; VISITED_MENU=%5B%2210011%22%5D; yfx_f_l_v_t_10000042=f_t_1545971968077__r_t_1545971968077__v_t_1545973349169__r_c_0',
               'Host': 'query.sse.com.cn',
               'Referer': 'http://www.sse.com.cn/disclosure/credibility/supervision/inquiries/',
               'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'}

    # 初始化任务队列
    tasks_add = queue.Queue()
    # 初始化任务添加线程池
    with futures.ThreadPoolExecutor(5) as pool_add:
        # 添加任务队列
        for i in range(104):  # 104页数据
            i += 1
            url_ = url + str(i) + url1
            pool_add.submit(parse_report, url_)

    # 下载任务列表
    tasks_download = []
    # 初始化下载任务线程池
    start_time = time.time()
    with futures.ThreadPoolExecutor(10) as pool_download:
        # 开始下载任务
        while not tasks_add.empty():
            item = tasks_add.get()
            tasks_download.append(pool_download.submit(download_file, item[0], item[1]))

    # 等待线程池完成
    futures.wait(tasks_download, return_when=futures.ALL_COMPLETED)
    end_time = time.time()
    print("下载总共用时:", end_time - start_time)
