# -*- coding: utf-8 -*-
"""
Created on Sun Aug 16 11:56:46 2020

@author: 97vin
"""

import numpy as np
import pandas as pd
import copy
from alpha_vantage.timeseries import TimeSeries

# strategy 
def ATR(DF,n=20):
    temp = DF.copy()
    temp["H-L"] = abs(temp["High"] - temp["Low"]) 
    temp["H-PC"] = abs(temp["High"] - temp["Close"].shift(1)) # high - previous day close
    temp["L-PC"] = abs(temp["Low"] - temp["Close"].shift(1))
    temp["TR"] = temp[["H-L", "H-PC", "L-PC"]].max(axis=1, skipna = False)
    temp["ATR"] = temp["TR"].rolling(n).mean()
    
    return_val = temp.drop(["H-L","H-PC","L-PC"], axis=1)
    return return_val

# KPIs
def CAGR(DF):
    temp = DF.copy()
    temp["Cumulative Return"] = (1+temp["Return"]).cumprod()
    
    CAGR = (temp["Cumulative Return"][-1])**(1/(len(temp)/252*78)) - 1
    return CAGR

def volatility(DF):
    temp = DF.copy()
    return temp["Return"].pct_change().std()*(np.sqrt(252*78))

def sharpe(DF,rf): #risk-free rate changes depends on the market
    temp = DF.copy()
    return (CAGR(temp) - rf)/volatility(temp)

def max_drawdown(DF):
    temp = DF.copy()
    temp["Cumulative Return"] = (1+temp["Return"]).cumprod()
    
    temp["Cumulative Return Max"] = temp["Cumulative Return"].cummax()
    temp["Range"] = (temp["Cumulative Return Max"] - temp["Cumulative Return"])/temp["Cumulative Return Max"]
    drawdown = temp["Range"].max()    
    return drawdown

def calmar(DF):
    return CAGR(DF)/max_drawdown(DF)


## high vol, high cap intraday data
tickers = ["MSFT", "AAPL", "FB", "AMZN", "INTC", "LYFT", "QCOM", "IBM"]
ts = TimeSeries(key="K1I429GVVREGYUWT", output_format = "pandas")
ohlc_dict = {}

for ticker in tickers[4:]:
    try:
        ohlc_dict[ticker] = ts.get_intraday(ticker, interval = "5min", outputsize="full")[0]
        ohlc_dict[ticker].columns = ["Open", "High", "Low", "Close", "Volume"]
    except:
        print("AlphaVantage Request Limit")
        continue
    
tickers = ohlc_dict.keys()

# ATR and rolling max price
ohlc_intraday = copy.deepcopy(ohlc_dict)
tickers_signal = {}
tickers_ret = {}
ticker=tickers[0]
for ticker in tickers:
    ohlc_intraday[ticker]["ATR"] = ATR(ohlc_intraday[ticker])["ATR"]
    ohlc_intraday[ticker]["Rolling Max CP"] = ohlc_intraday[ticker]["High"].rolling(20).max()
    ohlc_intraday[ticker]["Rolling Min CP"] = ohlc_intraday[ticker]["Low"].rolling(20).min()
    ohlc_intraday[ticker]["Rolling Max Vol"] = ohlc_intraday[ticker]["Volume"].rolling(20).max()
    ohlc_intraday[ticker].dropna(inplace = True)
    tickers_signal[ticker] = ""
    tickers_ret[ticker] = []
    

# signals
for ticker in tickers:
    print("calculating returns for ",ticker)
    for i in range(len(ohlc_intraday[ticker])):
        if tickers_signal[ticker] == "":
            tickers_ret[ticker].append(0)
            if ohlc_intraday[ticker]["High"][i] >= ohlc_intraday[ticker]["Rolling Max CP"][i] and ohlc_intraday[ticker]["Volume"][i] > 1.5*ohlc_intraday[ticker]["Rolling Max CP"][i-1]:
                tickers_signal[ticker] = "Buy"
            elif ohlc_intraday[ticker]["High"][i] <= ohlc_intraday[ticker]["Rolling Max CP"][i] and ohlc_intraday[ticker]["Volume"][i] < 1.5*ohlc_intraday[ticker]["Rolling Max CP"][i-1]:
                tickers_signal[ticker] = "Sell"
        
        elif tickers_signal[ticker] == "Buy":
            if ohlc_intraday[ticker]["Close"][i] < ohlc_intraday[ticker]["Close"][i-1] - ohlc_intraday[ticker]["ATR"][i-1]:
                tickers_signal[ticker] = ""
                tickers_ret[ticker].append(((ohlc_intraday[ticker]["Close"][i-1] - ohlc_intraday[ticker]["ATR"][i-1]) / ohlc_intraday[ticker]["Close"][i-1])-1)
            elif ohlc_intraday[ticker]["Low"][i] <= ohlc_intraday[ticker]["Rolling Min CP"][i] and ohlc_intraday[ticker]["Volume"][i] > 1.5*ohlc_intraday[ticker]["Rolling Max Vol"][i-1]:
                tickers_signal[ticker] = "Sell"
                tickers_ret[ticker].append(((ohlc_intraday[ticker]["Close"][i-1] - ohlc_intraday[ticker]["ATR"][i-1])/ohlc_intraday[ticker]["Close"][i-1])-1)
            else:
                tickers_ret[ticker].append((ohlc_intraday[ticker]["Close"][i]/ohlc_intraday[ticker]["Close"][i-1]) - 1)
        
        elif tickers_signal[ticker] == "Sell":
            if ohlc_intraday[ticker]["Close"][i] > ohlc_intraday[ticker]["Close"][i-1] + ohlc_intraday[ticker]["ATR"][i-1]:
                tickers_signal[ticker] = ""
                tickers_ret[ticker].append((ohlc_intraday[ticker]["Close"][i-1]/(ohlc_intraday[ticker]["Close"][i-1] + ohlc_intraday[ticker]["ATR"][i-1]))-1)
            elif ohlc_intraday[ticker]["High"][i]>=ohlc_intraday[ticker]["Rolling Max CP"][i] and ohlc_intraday[ticker]["Volume"][i] > 1.5*ohlc_intraday[ticker]["Rolling Max Vol"][i-1]:
                tickers_signal[ticker] = "Buy"
                tickers_ret[ticker].append((ohlc_intraday[ticker]["Close"][i-1]/(ohlc_intraday[ticker]["Close"][i-1] + ohlc_intraday[ticker]["ATR"][i-1]))-1)
            else:
                tickers_ret[ticker].append((ohlc_intraday[ticker]["Close"][i-1]/ohlc_intraday[ticker]["Close"][i])-1)
    print(ticker)
    print(len(tickers_ret[ticker]))
    ohlc_intraday[ticker]["Return"] = np.array(tickers_ret[ticker])








    

