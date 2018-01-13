# encoding:utf-8
import sys

# verion1: get all companies data from tushare and store them in Mongodb
import datetime
import tushare as ts
import time
import json
import pandas as pd
from collections import OrderedDict
import pytz
import types
import requests
from io import BytesIO, StringIO
import os
import click
import re
from os import listdir
from os.path import isfile, join
from os import walk

from pandas import DataFrame

DONWLOAD_URL = "http://yield.chinabond.com.cn/cbweb-mn/yc/downYearBzqx?year=%s&&wrjxCBFlag=0&&zblx=txy&ycDefId=%s"
YIELD_MAIN_URL = 'http://yield.chinabond.com.cn/cbweb-mn/yield_main'


def get_data():
    cur_year = datetime.datetime.now().year
    in_package_data = range(2002, cur_year + 1)

    # download new data
    to_downloads = in_package_data
    # frist, get ycDefIds params
    response = requests.get(YIELD_MAIN_URL)

    matchs = re.search(r'\?ycDefIds=(.*?)\&', response.text)
    ycdefids = matchs.group(1)
    assert (ycdefids is not None)

    fetched_data = []
    for year in to_downloads:
        print('Downloading from ' + DONWLOAD_URL % (year, ycdefids))
        response = requests.get(DONWLOAD_URL % (year, ycdefids))
        print ("response:", response)
        fetched_data.append(BytesIO(response.content))

    # combine all data

    dfs = []

    # basedir = os.path.join(os.path.dirname(__file__), "xlsx")
    '''
    basedir = os.path.join("D:\\Anaconda2\\Lib\\site-packages\\cn_treasury_curve", "xlsx")
    print "basedir :",basedir
    for i in in_package_data:
        print os.path.join(basedir, "%d.xlsx" % i)
        dfs.append(pd.read_excel(os.path.join(basedir, "%d.xlsx" % i)))
    '''
    for memfile in fetched_data:
        dfs.append(pd.read_excel(memfile))

    df = pd.concat(dfs)

    return df


def get_pivot_data():
    df = get_data()
    return df.pivot(index=u'日期', columns=u'标准期限(年)', values=u'收益率(%)')


def insert_zipline_treasure_format():
    pivot_data = get_pivot_data()
    frame = pivot_data[[0.08, 0.25, 0.5, 1, 2, 3, 5, 7, 10, 20, 30]]
    frame.index.name = 'Time Period'
    frame.columns = ['1month', '3month', '6month', '1year', '2year', '3year', '5year', '7year', '10year', '20year',
                     '30year']

    return frame
