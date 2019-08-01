import requests
import re
from bs4 import BeautifulSoup
import time
import random
import telnetlib

keys = [
    'Mozilla/5.0 (Linux; Android 4.1.1; Nexus 7 Build/JRO03D) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.166 Safari/535.19',
    'Mozilla/5.0 (Linux; U; Android 4.0.4; en-gb; GT-I9300 Build/IMM76D) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30',
    'Mozilla/5.0 (Linux; U; Android 2.2; en-gb; GT-P1000 Build/FROYO) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1',
    'Mozilla/5.0 (Windows NT 6.2; WOW64; rv:21.0) Gecko/20100101 Firefox/21.0',
    'Mozilla/5.0 (Android; Mobile; rv:14.0) Gecko/14.0 Firefox/14.0',
    'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.94 Safari/537.36',
    'Mozilla/5.0 (Linux; Android 4.0.4; Galaxy Nexus Build/IMM76B) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.133 Mobile Safari/535.19',
    'Mozilla/5.0 (iPad; CPU OS 5_0 like Mac OS X) AppleWebKit/534.46 (KHTML, like Gecko) Version/5.1 Mobile/9A334 Safari/7534.48.3',
    'Mozilla/5.0 (iPod; U; CPU like Mac OS X; en) AppleWebKit/420.1 (KHTML, like Gecko) Version/3.0 Mobile/3A101a Safari/419.3'
]


def get_proxies(max_page_number):
    '''
    爬取目标页面
    :param max_page_number:  最大页数
    :return:
    '''
    for i in range(1, max_page_number + 1):
        header = {'User-Agent': keys[random.randint(0, len(keys))]}
        page_number = i
        init_url = 'https://www.xicidaili.com/nn/' + str(i)
        req = requests.get(url=init_url, headers=header)

        # print(req.text)
        # 正则表达式获取代理IP
        agency_ip_re = re.compile(
            r'\b(?:(?:25[0-5)|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b', re.S)
        agency_ip = agency_ip_re.findall(req.text)
        # print(agency_ip)
        # 正则表达式获取代理端口
        agency_port_re = re.compile('<td>([0-9]{2,5})</td>', re.S)
        agency_port = agency_port_re.findall(req.text)
        # print(agency_port)
        ip_number = len(agency_ip)
        # print('正在获取第 %d 页代理' % page_number)

        for i in range(ip_number):
            total_ip = agency_ip[i] + ':' + agency_port[i]
            # print(total_ip)
            Test_IP(agency_ip[i], agency_port[i])

            time.sleep(0.1)

        print('第 %d 页获取完毕' % page_number)
        print('-----------------------------------')
        time.sleep(1)


def Test_IP(ip_to_test, port_to_test):
    # 使用telnet测试代理是否可用
    try:
        telnetlib.Telnet(ip_to_test, port_to_test, timeout=3)
    except:
        print('该代理失效:', ip_to_test, port_to_test)
        print('----------------------')
    else:
        print('该代理IP可用', ip_to_test, port_to_test)
        print('----------------------')
        available_ip = ip_to_test + ':' + port_to_test
        saveProxyIP(available_ip)


def saveProxyIP(available_ip):
    # 保存可用IP
    with open(r'E:\files\XCProxy.txt', 'a') as f:
        f.write(available_ip + '\n')


if __name__ == '__main__':
    get_proxies(2)
