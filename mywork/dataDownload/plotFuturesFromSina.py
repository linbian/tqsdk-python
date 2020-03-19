from datetime import datetime, timedelta
import time
import requests
import json
from matplotlib.pylab import date2num
from matplotlib import pyplot as plt
import mpl_finance as mpf
from pandas import DataFrame
import talib as ta

import sys
sys.path.append('..')
import DictCode as dc

plt.rcParams['font.family'] = 'sans-serif' #用来正常显示中文
plt.rcParams['font.sans-serif']=['SimHei'] #用来正常显示负号
def get_candles_data(url):
    print(url)
    response = requests.get(url)
    data_arr = response.text.replace("[[",'').replace("]]",'').replace("\"","").split("],[")
    quotes = []
    for item_str in reversed(data_arr):
        item = item_str.split(",")
        sdatetime_num = date2num(datetime.strptime(item[0].replace("T",' ').replace('.000Z',''),'%Y-%m-%d'))
        datas = (sdatetime_num,float(item[1]),float(item[2]),float(item[3]),float(item[4])) # 按照 candlestick_ohlc 要求的数据结构准备数据
        quotes.append(datas)
    return quotes

def get_candles_data_minutes(url):
    print(url)
    response = requests.get(url)
    data_arr = response.text.replace("[[",'').replace("]]",'').replace("\"","").split("],[")
    quotes = []
    for item_str in reversed(data_arr):
        item = item_str.split(",")
        sdatetime_num = date2num(datetime.strptime(item[0].replace("T",' ').replace('.000Z',''),'%Y-%m-%d %H:%M:%S'))
        datas = (sdatetime_num,float(item[1]),float(item[2]),float(item[3]),float(item[4])) # 按照 candlestick_ohlc 要求的数据结构准备数据
        quotes.append(datas)
    return quotes

def plot_candles(datas,title,tradePair,width):
    close = []
    high = []
    low = []
    tradeTime = []
    for item in datas:
        tradeTime.append(item[0])
        high.append(item[2])
        low.append(item[3])
        close.append(item[4])
    merge_dt_dict = {'tradeTime':tradeTime,
                     'high':high,
                     'low':low,
                     'close':close}
    data_df = DataFrame(merge_dt_dict)

    # fig, ax = plt.subplots(facecolor=(0, 0.3, 0.5),figsize=(37,37))

    ax1 = plt.subplot2grid(((6,4)), (1,0), rowspan=4, colspan=4)
    # fig.subplots_adjust(bottom=0.1)
    ax1.xaxis_date()

    # plt.xlabel('time')
    plt.ylabel('price')
    mpf.candlestick_ohlc(ax1,datas,width=width,colorup='r',colordown='green') # 上涨为红色K线，下跌为绿色，K线宽度为0.7
    # upper,middle,lower=ta.BBANDS(data_df['close'], matype=ta.MA_Type.T3,timeperiod=20)
    upper,middle,lower=ta.BBANDS(data_df['close'], timeperiod=20)
    ax1.plot(data_df['tradeTime'],middle, 'blue',label='middle')
    ax1.plot(data_df['tradeTime'],upper, 'y',label='upper')
    ax1.plot(data_df['tradeTime'],lower, 'y',label='lower')

    ## 在顶部绘制ATR
    ax0 = plt.subplot2grid(((6,4)), (0,0), sharex=ax1, rowspan=1, colspan=4,)
    plt.title(tradePair+'['+title+']')
    # rsi = ta.RSI(data_df['close'],timeperiod=14)
    atr = ta.ATR(data_df['high'],data_df['low'],data_df['close'],timeperiod=14)
    atrCol = 'blue'
    posCol = '#386d13'
    negCol = '#8f2020'
    ax0.plot(data_df['tradeTime'], atr, atrCol, linewidth=1)
    # ax0.fill_between(data_df['tradeTime'], atr, 70, where=(atr>=70), facecolor=negCol, edgecolor=negCol)
    # ax0.fill_between(data_df['tradeTime'], atr, 30, where=(atr<=30), facecolor=posCol, edgecolor=posCol)
    # ax0.set_yticks([30,70])
    plt.ylabel('ATR')

    ### 在底部绘制MACD
    ax2 = plt.subplot2grid(((6,4)), (5,0), sharex=ax1, rowspan=1, colspan=4,)
    fillcolor = '#00ffe8'
    macd, macdsignal, macdhist = ta.MACD(data_df['close'],fastperiod=6, slowperiod=12, signalperiod=9)
    # emaslow, emafast, macd
    ax2.plot(data_df['tradeTime'], macd, color='y', lw=1)
    ax2.plot(data_df['tradeTime'], macdsignal, color='b', lw=1)
    # ax2.fill_between(data_df['tradeTime'], macdhist, 0, where=(macdhist>0), facecolor="r", edgecolor=fillcolor)
    ax2.fill_between(data_df['tradeTime'], macdhist, 0, where=(macdhist>0), facecolor="r")
    ax2.fill_between(data_df['tradeTime'], macdhist, 0, where=(macdhist<0), facecolor="g")
    # ax2.fill_between(data_df['tradeTime'], macdhist, 0, where=(macdhist<0), facecolor="g", edgecolor=fillcolor)
    plt.grid(True)
    plt.setp(ax0.get_xticklabels(), visible=False)
    plt.setp(ax1.get_xticklabels(), visible=False)
    plt.xticks(rotation=45) #日期显示的旋转角度
    plt.savefig('../img/futures-'+tradePair+'-'+title+'.png')

if __name__ == '__main__':

    url_sina_minutes ="http://stock2.finance.sina.com.cn/futures/api/json.php/IndexService.getInnerFuturesMiniKLine{}m?symbol={}"
    url_sina_daily   ="http://stock2.finance.sina.com.cn/futures/api/json.php/IndexService.getInnerFuturesDailyKLine?symbol={}"

    code_index ="rb"
    for code_index in dc.SYMBOL_JSON.keys():
        data_candles_days = get_candles_data(url_sina_daily.format(dc.SYMBOL_JSON[code_index]["sylbom"]))
        plot_candles(data_candles_days,"days",dc.SYMBOL_JSON[code_index]["name"],0.7)
        time.sleep(1)
        data_candles_60m = get_candles_data_minutes(url_sina_minutes.format(60,dc.SYMBOL_JSON[code_index]["sylbom"]))
        plot_candles(data_candles_60m,"60m",dc.SYMBOL_JSON[code_index]["name"],0.7)
        time.sleep(1)
        # data_candles_15m = get_candles_data_minutes(url_sina_minutes.format(15,dc.SYMBOL_JSON[code_index]["sylbom"]))
        # plot_candles(data_candles_15m,"15m",dc.SYMBOL_JSON[code_index]["name"],0.7)
        # time.sleep(1)
        # data_candles_5m = get_candles_data_minutes(url_sina_minutes.format(5,dc.SYMBOL_JSON[code_index]["sylbom"]))
        # plot_candles(data_candles_5m,"5m",dc.SYMBOL_JSON[code_index]["name"],0.7)
        # time.sleep(1)