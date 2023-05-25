from datetime import datetime
import time
import requests
from lxml import etree
import threading
import json
from retrying import retry
import csv
import re


# 获取代理
def get_ip():
    """请求api获取ip"""
    print('正在访问代理池')
    url = 'http://tiqu.pyhttp.taolop.com/getip?count=100&neek=31291&type=2&yys=0&port=2&sb=&mr=2&sep=0'
    resp_json = requests.get(url).text
    resp_dict = json.loads(resp_json).get('data')
    ip_list = []
    for i in resp_dict:
        ip_list.append({'https': f'{i.get("ip")}:{i.get("port")}'})
    if len(ip_list) == 100:
        print('代理池获取成功')
        return ip_list  # 返回ip列表
    if not resp_dict:
        print('代理池获取失败')
        return None


# 多线程爬取页面
@retry(stop_max_attempt_number=3)
def spider(page, ip):
    # print(f"正在爬取第{page['排名']}页，地址：{page['url']}，使用ip：{ip['https']}")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36'}
    global items, None_page
    try:
        html = requests.get(page['url'], headers=headers, proxies=ip, timeout=5).text
        element = etree.HTML(html)
        time = element.xpath('//span[@property="v:runtime"]/text()')
        if len(time) != 0:
            # print(
                # f"{threading.current_thread()}访问第{page['排名']}页成功\n页面地址： {page['url']}\n使用代理IP：{ip['https']},本页影片时长{time}\n,本页字长{len(html)}")
            items[page['排名'] - 1]['时长'] = re.findall(f'\d+',time[0])[0]

            None_page.remove(page)
        else:
            print(f"{threading.current_thread()}访问第{page['排名']}页数据不全\n页面地址： {page['url']}，待重新访问。\n使用ip：{ip['https']}\n")
    except Exception as e:
        print(f"{threading.current_thread()}访问第{page['排名']}页失败\n页面地址为： {page['url']}，\n错误代码：{e}\n使用ip：{ip['https']}\n")


def get_details_html():
    """获取前100电影url"""
    print('正在获取前100页url')
    global items
    homepage_urls = ['https://movie.douban.com/top250?start={}'.format(i) for i in range(0, 100, 25)]
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0'}
    for url in homepage_urls:
        # 获取前100电影url
        html = requests.get(url=url, headers=headers).text
        element = etree.HTML(html)
        for i in range(0, 25):
            details_url = element.xpath('//div[@class="hd"]/a/@href')[i]
            rank = element.xpath('//em/text()')[i]
            name = element.xpath('//*[@class="title"][1]/text()')[i]
            score = element.xpath('//*[@class="rating_num"]/text()')[i]
            bd = element.xpath('//div[@class="bd"]/p[1]/text()[last()]')[i].replace('\n','').strip(' ').split('/')
            data = re.findall(r'\d+',bd[0].strip(' '))[0]
            county = bd[::-1][1].strip(' ')
            item = {
                '排名': int(rank),
                '片名': name,
                '评分': float(score),
                '国家': county,
                '日期': datetime.strptime(data, '%Y').year,
                '时长': None,
                'url': details_url
            }
            items.append(item)


# 多线程函数
def multi_thread(None_page):
    print('正在建立线程')
    threads = []
    ip = get_ip()
    for page, i in zip(None_page, ip[:len(None_page)]):
        threads.append(threading.Thread(target=spider, args=(page, i)))
    for thread in threads:
        thread.name = f'线程{threads.index(thread)}'
        thread.start()
    for thread in threads:
        thread.join()


def writer_file():
    print('正在写入文件')
    headers = ['排名', '片名', '评分', '国家', '日期', '时长', 'url']
    with open('film_info.csv', 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, headers)
        writer.writerows(items)
    print('写入完成')


def main():
    # 获取详细信息
    global items, None_page
    get_details_html()
    for item in items:
        if item['时长'] is None:
            None_page.append({
                '排名': item['排名'],
                'url': item['url'],
            })
    i = 1
    while len(None_page) != 0:
        print('=' * 80, f'\n开始第{i}轮爬虫')
        print(f"本轮共需爬取{len(None_page)}个页面")
        multi_thread(None_page)
        print(f'第{i}轮爬取完成,共计{len(None_page)}页数据访问出错,待重新访问,错误页面有\n{None_page}')
        print('=' * 80)
        i += 1
        # time.sleep(2)
    print('所有数据爬取完毕')
    for item in items:
        print(item)
    writer_file()


items = []
None_page = []
main()