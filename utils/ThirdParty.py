#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import json
from datetime import date
import time

def douban_book_content(bookid='4050758'):
    """
    抽取豆瓣读上某本书的前50条短评内容并计算评分的平均值。
    """
    count = 0
    i = 0
    sum, count_s = 0, 0
    while(count < 50):
        try:
            r = requests.get('https://book.douban.com/subject/{}/comments/hot?p={}'.format(bookid, i+1))
        except Exception as err:
            print(err)
            break
        soup = BeautifulSoup(r.text, 'lxml')
        comments = soup.find_all('p', 'comment-content')
        for item in comments:
            count = count + 1
            print(count, item.string)
            if count == 50:
                break  
        pattern = re.compile('<span class="user-stars allstar(.*?) rating"')
        p = re.findall(pattern, r.text)
        for star in p:
            count_s = count_s + 1
            sum += int(star)
        time.sleep(5)    # delay request from douban's robots.txt
        i += 1
    if count == 50:
        print(sum / count_s)

def retrieve_quotes_historical(stock_code='AAPL'):
    quotes = []
    url = 'https://finance.yahoo.com/quote/%s/history?p=%s' % (stock_code, stock_code)
    r = requests.get(url)
    m = re.findall('"HistoricalPriceStore":{"prices":(.*?),"isPending"', r.text)
    if m:
        quotes = json.loads(m[0])
        quotes = quotes[::-1]
    return  [item for item in quotes if not 'type' in item]

def retrieve_dji_list():
    """
    在“http://money.cnn.com/data/dow30/”上抓取道指成分股数据并将30家公司的代码、公司名称和最近一次成交价放到一个列表中输出
    """
    r = requests.get('http://money.cnn.com/data/dow30/')
    search_pattern = re.compile('class="wsod_symbol">(.*?)<\/a>.*?<span.*?">(.*?)<\/span>.*?\n.*?class="wsod_stream">(.*?)<\/span>')
    dji_list_in_text = re.findall(search_pattern, r.text)
    # return dji_list_in_text
    dji_list = [[item[0], item[1], float(item[2])] for item in dji_list_in_text] 
    return dji_list

def create_aveg_open(stock_code):
    quotes = retrieve_quotes_historical(stock_code)
    list1 = []
    for i in range(len(quotes)):
        x = date.fromtimestamp(quotes[i]['date'])
        y = date.strftime(x,'%Y-%m-%d')   
        list1.append(y)
    quotesdf_ori = pd.DataFrame(quotes, index = list1)
    listtemp = []
    for i in range(len(quotesdf_ori)):
        temp = time.strptime(quotesdf_ori.index[i],"%Y-%m-%d")
        listtemp.append(temp.tm_mon)
    tempdf = quotesdf_ori.copy()
    tempdf['month'] = listtemp
    meanopen = tempdf.groupby('month').open.mean()
    return meanopen

