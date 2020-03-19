#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import date, time

__author__ = "Ringo"

from tqsdk import TqApi,TargetPosTask,TqBacktest
from tqsdk.ta import ATR
from tqsdk.ta import BOLL
from tqsdk.ta import RSI

# ART计算使用天数
ART_DAY_LENGTH = 20
# 合约代码
SYMBOL_JSON = {
    "rb":{"symbol":"KQ.i@SHFE.rb","contractSize":10},   ## 上期所-螺纹钢
    "au":{"symbol":"KQ.i@SHFE.au","contractSize":1000}, ## 上期所-沪金
    "wr":{"symbol":"KQ.i@SHFE.wr","contractSize":10},   ## 上期所-线材
}
# SYMBOL = "SHFE.au1912"
code_index = "wr"
SYMBOL = SYMBOL_JSON[code_index]["symbol"]       ## 合约代码
VALUE  = SYMBOL_JSON[code_index]["contractSize"] ## 合约乘数

api = TqApi(web_gui=True,backtest=TqBacktest(start_dt=date(2000, 5, 1), end_dt=date(2019, 12, 31)))
# klines = api.get_kline_serial(SYMBOL, 60*5) ## 60*5=50分钟
klines = api.get_kline_serial(SYMBOL, 60*60*24) ## 60*60*24=日线
print("datetime","open","high","low","close","volume","tmpvol_hl","maxvol_hl","tmpvol_oc","maxvol_oc","minvol_oc","ma","atr","bollmatitude","rsi","atr/ma","atrMoney")
maxvol_hl = 0
maxvol_oc = 0
minvol_oc = 0
while True:
    # 通过wait_update刷新数据
    api.wait_update()
    atr = ATR(klines,14)
    boll = BOLL(klines, 14 , 2)
    rsi = RSI(klines,14)
    lastKline = klines.iloc[-1]
    tmpvol_hl=lastKline.high-lastKline.low
    tmpvol_oc=lastKline.close-lastKline.open
    maxvol_oc = max(maxvol_oc,lastKline.close-lastKline.open)
    minvol_oc = min(minvol_oc,lastKline.close-lastKline.open)
    maxvol_hl = max(maxvol_hl,lastKline.high-lastKline.low)
    midline = boll["mid"].iloc[-1]
    topline = boll["top"].iloc[-1]
    bottomline = boll["bottom"].iloc[-1]
    bollmatitude = topline-bottomline
    atr_ma = 0
    if(midline>0):
        atr_ma = atr.atr.iloc[-1] / midline
    atrMoney=0
    if(atr.atr.iloc[-1]>0):
        atrMoney = atr.atr.iloc[-1] * VALUE
    print(str(lastKline.datetime),lastKline.open,lastKline.high,lastKline.low,lastKline.close,lastKline.volume,tmpvol_hl,maxvol_hl,tmpvol_oc,maxvol_oc,minvol_oc,midline,atr.atr.iloc[-1],bollmatitude,rsi.rsi.iloc[-1],atr_ma,atrMoney)