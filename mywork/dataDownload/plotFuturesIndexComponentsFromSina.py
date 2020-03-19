from datetime import datetime, timedelta
import time
import requests
import json
from matplotlib.pylab import date2num
from matplotlib import pyplot as plt
import mpl_finance as mpf
from pandas import DataFrame
import talib as ta
import numpy as np

import sys
sys.path.append('..')
import DictCode as dc

plt.rcParams['font.family'] = 'sans-serif' #用来正常显示中文
plt.rcParams['font.sans-serif']=['SimHei'] #用来正常显示负号
def get_candles_data(url,contractSize):
    print(url)
    response = requests.get(url)
    data_arr = response.text.replace("[[",'').replace("]]",'').replace("\"","").split("],[")
    close = []
    high = []
    low = []
    tradeTime = []
    for item_str in reversed(data_arr):
        item = item_str.split(",")
        sdatetime_num = date2num(datetime.strptime(item[0].replace("T",' ').replace('.000Z',''),'%Y-%m-%d'))
        # datas = (sdatetime_num,float(item[1]),float(item[2]),float(item[3]),float(item[4])) # 按照 candlestick_ohlc 要求的数据结构准备数据
        # quotes.append(datas)
        tradeTime.append(sdatetime_num)
        high.append(float(item[2])*contractSize)
        low.append(float(item[3])*contractSize)
        close.append(float(item[4])*contractSize)
    dt_dict = {'tradeTime':tradeTime,
               'high':high,
               'low':low,
               'close':close}
    data_df = DataFrame(dt_dict)
    atr = ta.ATR(data_df['high'],data_df['low'],data_df['close'],timeperiod=14)
    data_df["atr"]=atr
    data_df["atrRatio"]=data_df["atr"]/data_df['close']
    atrRatio = data_df["atrRatio"]
    if len(data_df["atrRatio"])>300:
        atrRatio = data_df["atrRatio"][len(data_df["atrRatio"])-300:len(data_df["atrRatio"])-1]
    # print(atrRatio)
    return list(atrRatio)

def plotIndexComponentsAtrRatio(atrRatioDf,indexCode,indexName,timeframe):
    print(atrRatioDf)
    colorList = ['b','r','lightslategray','y','lime','seagreen','navy','orange','m','coral','sienna','chocalate','skyblue']
    fig, ax = plt.subplots(figsize=(14,14))
    plt.title('Future Index '+indexName+"["+indexCode+']['+timeframe+'] ATR-Ratio')  #标题
    plt.ylabel('atr * contractSize')
    pos = 0
    for column in atrRatioDf:
        plt.plot(atrRatioDf.index, atrRatioDf[column].tolist(), color=colorList[pos],label=dc.SYMBOL_JSON[column]["name"]+"_"+column+"_"+colorList[pos])
        plt.legend()
        pos+=1
    plt.savefig('../img/futures-index-'+indexName+'['+indexCode+']'+'-components['+timeframe+']-atr.png')

def computeIndexComponentsAtrRatio(index_content):
    index_atr_dict = {}
    listLength = 0
    for symbol_code in index_content.keys():
        tmp_atr = []
        tmp_atr = get_candles_data(url_sina_daily.format(dc.SYMBOL_JSON[symbol_code]["sylbom"]),float(dc.SYMBOL_JSON[symbol_code]["contractSize"]))
        listLength = len(tmp_atr)
        index_atr_dict[symbol_code] = tmp_atr
    data_df = DataFrame(index_atr_dict)
    # for column in data_df:
    #     print(column)
    # print(data_df.columns.values.tolist())
    return data_df


if __name__ == '__main__':
    url_sina_daily   ="http://stock2.finance.sina.com.cn/futures/api/json.php/IndexService.getInnerFuturesDailyKLine?symbol={}"
    # index_code = "AGRI-CANDY"
    for index_code in dc.INDEX_JSON.keys():
        index_name = dc.INDEX_JSON[index_code]["name"]
        index_content = dc.INDEX_JSON[index_code]["content"]
        index_components_atr_ratio = computeIndexComponentsAtrRatio(index_content)
        plotIndexComponentsAtrRatio(index_components_atr_ratio,index_code,index_name,"daily")