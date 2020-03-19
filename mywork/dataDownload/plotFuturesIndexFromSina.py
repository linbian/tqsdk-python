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


def testFunc():
    code_index ="rb"
    code_set = ["rb","ag","au"]
    colorList = ['b','r','g']
    fig, ax = plt.subplots(facecolor=(0, 0.3, 0.5),figsize=(37,37))
    plt.title('Future Index ATR')  #标题
    plt.ylabel('atr * contractSize')
    pos = 0
    for code_index in code_set:
        atr = get_candles_data(url_sina_daily.format(dc.SYMBOL_JSON[code_index]["sylbom"]),float(dc.SYMBOL_JSON[code_index]["contractSize"]))
        length = len(atr)
        print(length)
        plt.plot(range(0,length), atr, color=colorList[pos],label=dc.SYMBOL_JSON[code_index]["name"])
        plt.legend()
        pos+=1
    plt.savefig('../img/futures-index-atr.png')

def plotIndexAvgRatio(atrRatioDict):
    colorList = ['b','r','lightslategray','y','lime','seagreen','navy','orange','m','coral','sienna','chocalate','skyblue']
    fig, ax = plt.subplots(figsize=(14,14))
    plt.title('Future Index ATR')  #标题
    plt.ylabel('atr * contractSize')
    pos = 0
    for index_code in atrRatioDict.keys():
        atrRatio = atrRatioDict[index_code]["avgAtrRatio"]
        index_name = atrRatioDict[index_code]["index_name"]
        length = len(atrRatio)
        print(length)
        plt.plot(range(0,length), atrRatio, color=colorList[pos],label=index_name+"_"+index_code+"_"+colorList[pos])
        plt.legend()
        pos+=1
    plt.savefig('../img/futures-index-atr.png')

def computeIndexAvgAtrRatio(index_content):
    index_atr_dict = {}
    listLength = 0
    for symbol_code in index_content.keys():
        tmp_atr = []
        tmp_atr = get_candles_data(url_sina_daily.format(dc.SYMBOL_JSON[symbol_code]["sylbom"]),float(dc.SYMBOL_JSON[symbol_code]["contractSize"]))
        # print(symbol_code,".tmp_atr length = ",len(tmp_atr))
        listLength = len(tmp_atr)
        index_atr_dict[symbol_code] = tmp_atr
    data_df = DataFrame(index_atr_dict)
    print(data_df)
    new_zero_array = np.zeros((listLength,1))
    data_df["total"] = new_zero_array
    for symbol_code in index_content.keys():
        data_df["total"] = data_df["total"] + data_df[symbol_code]
    print(data_df)
    columnsCount = len(index_content.keys())
    data_df["avg"] = data_df["total"]/columnsCount
    return data_df["avg"]

if __name__ == '__main__':
    url_sina_daily   ="http://stock2.finance.sina.com.cn/futures/api/json.php/IndexService.getInnerFuturesDailyKLine?symbol={}"

    atrRatioDict = {}
    for index_code in dc.INDEX_JSON.keys():
        index_name = dc.INDEX_JSON[index_code]["name"]
        index_content = dc.INDEX_JSON[index_code]["content"]
        atrRatioDict[index_code]={"index_name":index_name,"avgAtrRatio":[]}
        avgAtrRatio = computeIndexAvgAtrRatio(index_content)
        atrRatioDict[index_code]["avgAtrRatio"] = avgAtrRatio
    plotIndexAvgRatio(atrRatioDict)