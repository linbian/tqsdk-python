#!/usr/bin/env python
#  -*- coding: utf-8 -*-
__author__ = 'linbian'

'''
策略模板
注: 该示例策略仅用于功能示范, 实盘时请根据自己的策略/经验进行修改
'''
from tqsdk import TqApi, TargetPosTask,TqBacktest
from tqsdk.tafunc import ma as IMA
from tqsdk.ta import BOLL
from tqsdk.ta import ATR
from tqsdk.ta import MACD
from datetime import date

inpPeriodMa = 260    # MA周期
inpPeriodBoll = 20
inpBollDev = 2
inpPeriodAtr = 14  	## 周期ATR
inpPeriodMacdFast=12
inpPeriodMacdSlow=26
inpPeriodMacdSignal=9
inpAtrRatio=3     ## atr倍数
inpMaxTimes=5       ## 最大加仓次数
inpLots=1
inpMaxLotsMultiple=2 ## inpLots的最大加仓倍数
inpLongAddStepRatio=7
inpShortAddStepRatio=4.0
inpTimeFrame = 15

SYMBOL = "SHFE.bu2006"   # 合约代码
SYMBOL = "KQ.i@SHFE.rb"  # 合约代码
SYMBOL = "KQ.m@SHFE.rb"  # 合约代码
SYMBOL = "SHFE.rb2005"

api = TqApi(backtest=TqBacktest(start_dt=date(2019, 5, 1), end_dt=date(2020, 3, 1)),web_gui=True)
print("策略开始运行")

data_length = inpPeriodMa + 2  # k线数据长度
# "duration_seconds=60"为一分钟线, 日线的duration_seconds参数为: 24*60*60
klines = api.get_kline_serial(SYMBOL, duration_seconds=60*inpTimeFrame, data_length=data_length)
target_pos = TargetPosTask(api, SYMBOL)
position = api.get_position(SYMBOL)

def indicatorCompute(klines,periodBoll,bollDev,periodMa,periodAtr,periodMacdFast,periodMacdSlow,periodMacdSignal):
    boll = BOLL(klines, periodBoll , bollDev)
    bollMid = boll["mid"]
    bollTop = boll["top"]
    bollTot = boll["bottom"]
    # print("策略运行，中轨：%.2f，上轨为:%.2f，下轨为:%.2f" % (bollMid.iloc[-1], bollTop.iloc[-1], bollTot.iloc[-1]))
    ma = IMA(klines["close"], periodMa)
    # print("策略运行，MA：%.2f" % (ma.iloc[-1]))
    atr = ATR(klines,periodAtr)
    atr=atr["atr"]
    # print("策略运行，ATR：%.2f" % (atr.iloc[-1]))
    macd = MACD(klines,periodMacdFast,periodMacdSlow,periodMacdSignal)
    macdDiff = macd["diff"]
    macdDea  = macd["dea"]
    macdBar  = macd["bar"]
    # print("策略运行，macdDiff=%.2f,macdDea=%.2f,macdBar=%.2f," % (macdDiff.iloc[-1],macdDea.iloc[-1],macdBar.iloc[-1]))
    return bollMid, bollTop, bollTot,ma,atr,macdDiff,macdDea,macdBar

bollMid, bollTop, bollTot,ma,atr,macdDiff,macdDea,macdBar = indicatorCompute(klines,inpPeriodBoll,inpBollDev,inpPeriodMa,inpPeriodAtr,
                                                                             inpPeriodMacdFast,inpPeriodMacdSlow,inpPeriodMacdSignal)
longOpenTimes = 0
longOpenMatitude = 0
longStopPrice = 0
longReduceSize = 0
shortOpenTimes = 0
shortOpenMatitude = 0
shortStopPrice = 0
shortReduceSize = 0
while True:
    api.wait_update()
    if api.is_changing(klines.iloc[-1], "datetime"):  # 产生新k线:重新计算各指标
        bollMid, bollTop, bollTot,ma,atr,macdDiff,macdDea,macdBar = indicatorCompute(klines,inpPeriodBoll,inpBollDev,inpPeriodMa,inpPeriodAtr,
                                                                                     inpPeriodMacdFast,inpPeriodMacdSlow,inpPeriodMacdSignal)

        ## 无仓位，开多仓
        conditionLongOpen1 = False
        conditionLongOpen2 = False
        conditionLongOpen3 = False
        if macdBar.iloc[-1]>0 and macdBar.iloc[-2]<0 and macdBar.iloc[-3]<0:
            for i in range(1,8):
                if klines["close"].iloc[-i]>ma.iloc[-i] and klines["close"].iloc[-i-1]>ma.iloc[-i-1]:
                    conditionLongOpen1=True
                    break

        if klines["close"].iloc[-1] > ma.iloc[-1] and  klines["close"].iloc[-2] < ma.iloc[-2]:
            for i in range(1,8):
                if macdBar.iloc[-i]> 0 and macdBar.iloc[-i-1] <0 and macdBar.iloc[-i-2]<0:
                    conditionLongOpen2=True
                    break

        if position.pos_long == 0 and position.pos_short == 0:
            if conditionLongOpen1==True or conditionLongOpen2==True or conditionLongOpen3==True:
                print("开多仓")
                target_pos.set_target_volume(inpLots)
                longOpenTimes = 1
                longOpenMatitude = inpAtrRatio * atr.iloc[-1]
                longStopPrice = klines["close"].iloc[-1] - longOpenMatitude
                longReduceSize = 0
                continue

        ## 有多仓，平多仓
        conditionLongClose1 = False
        conditionLongClose2 = False
        conditionLongCLose3 = False
        if klines["close"].iloc[-1] < ma.iloc[-1] - longOpenMatitude:
            conditionLongClose1 = True

        if klines["open"].iloc[-1] < klines["low"].iloc[-2] and klines["open"].iloc[-1] > klines["close"].iloc[-1]:
            conditionLongClose2=True

        if position.pos_long > 0 and (conditionLongClose1==True or conditionLongClose2==True or conditionLongCLose3==True):
            print("平多仓")
            target_pos.set_target_volume(0)
            longOpenTimes = 0
            longOpenMatitude = 0
            longStopPrice = 0
            longReduceSize = 0
            continue

        ## 有多仓，调多仓
        conditionLongModify1 = False
        conditionLongModify2 = False
        conditionLongModify3 = False
        if klines["close"].iloc[-3] > klines["close"].iloc[-2] and klines["close"].iloc[-1] > klines["close"].iloc[-2]:
            if klines["close"].iloc[-1] > longStopPrice + 3*longOpenTimes*inpLongAddStepRatio*longOpenMatitude:
                conditionLongModify1=True
        if position.pos_long > 0 and (conditionLongModify1 or conditionLongModify2 or conditionLongModify3):
            print("调多仓")
            target_size = position.pos_long + inpLots
            if longOpenTimes==1:
                target_size = position.pos_long + inpMaxLotsMultiple * inpLots
            target_pos.set_target_volume(target_size)
            longOpenTimes += 1
            longStopPrice = klines["close"].iloc[-1] - longOpenMatitude * inpLongAddStepRatio
            longReduceSize = 0
            continue

        ## 无仓位，开空仓
        conditionShortOpen1 = False
        conditionShortOpen2 = False
        conditionShortOpen3 = False
        if macdBar.iloc[-1]<0 and macdBar.iloc[-2]>0 and macdBar.iloc[-3]>0:
            for i in range(1,8):
                if klines["close"].iloc[-i]<ma.iloc[-i] and klines["close"].iloc[-i-1]<ma.iloc[-i-1]:
                    conditionShortOpen1=True
                    break

        if klines["close"].iloc[-1] < ma.iloc[-1] and  klines["close"].iloc[-2] > ma.iloc[-2]:
            for i in range(1,8):
                if macdBar.iloc[-i]< 0 and macdBar.iloc[-i-1] >0 and macdBar.iloc[-i-2]>0:
                    conditionShortOpen2=True
                    break
        if position.pos_long == 0 and position.pos_short == 0:
            if conditionShortOpen1 or conditionShortOpen2 or conditionShortOpen3:
                print("开空仓")
                target_pos.set_target_volume(-inpLots)
                shortOpenTimes = 1
                shortOpenMatitude = inpAtrRatio * atr.iloc[-1]
                shortStopPrice = klines["close"].iloc[-1] + shortOpenMatitude
                shortReduceSize = 0
                continue

        ## 有空仓，平空仓
        conditionShortClose1 = False
        conditionShortClose2 = False
        conditionShortClose3 = False
        if klines["close"].iloc[-1] > ma.iloc[-1] + shortOpenMatitude:
            conditionShortClose1 = True

        if klines["open"].iloc[-1] > klines["high"].iloc[-2] and klines["open"].iloc[-1] < klines["close"].iloc[-1]:
            conditionShortClose2=True
        if position.pos_short > 0 and (conditionShortClose1 or conditionShortClose2 or conditionShortClose3):
            print("平空仓")
            target_pos.set_target_volume(0)
            shortOpenTimes = 0
            shortOpenMatitude = 0
            shortStopPrice = 0
            shortReduceSize = 0
            continue

        ## 有空仓，调空仓
        conditionShortModify1 = False
        conditionShortModify2 = False
        conditionShortModify3 = False
        # print("position.position_long=",position.pos_long)
        # print("position.position_short=",position.pos_short)
        if klines["close"].iloc[-3] < klines["close"].iloc[-2] and klines["close"].iloc[-1] < klines["close"].iloc[-2]:
            if klines["close"].iloc[-1] <= shortStopPrice - 3*shortOpenTimes*inpShortAddStepRatio*shortOpenMatitude:
                conditionShortModify1=True
        if position.pos_short > 0 and (conditionShortModify1 or conditionShortModify2 or conditionShortModify3):
            print("调空仓")
            target_size = position.pos_short + inpLots
            if shortOpenTimes==1:
                target_size = position.pos_short + inpMaxLotsMultiple * inpLots
            target_pos.set_target_volume(-target_size)
            shortOpenTimes += 1
            shortStopPrice = klines["close"].iloc[-1] + shortOpenMatitude * inpShortAddStepRatio
            shortReduceSize = 0
            continue