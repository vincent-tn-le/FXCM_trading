# -*- coding: utf-8 -*-
"""
Created on Wed Aug 19 09:48:55 2020

@author: 97vin
"""

import pandas as pd
from stocktrends import Renko
import statsmodels.api as sm
from alpha_vantage.timeseries import TimeSeries
import copy
import numpy as np

def MACD(df, a=12, b=26, c=9):
    temp = df.copy()
    temp["MA_fast"] = temp["Close"].ewm(span=a, min_periods=a).mean()
    temp["MA_slow"] = temp["Close"].ewm(span=b, min_periods=b).mean()
    temp["MACD"] = temp["MA_fast"] - temp["MA_slow"]
    temp["Signal"] = temp["MACD"].ewm(span=c, min_periods=c).mean()
    temp.dropna(axis=0, inplace=True)
    return (temp["MACD"], temp["Signal"])

def ATR(DF,n=20):
    temp = DF.copy()
    temp["H-L"] = abs(temp["High"] - temp["Low"]) 
    temp["H-PC"] = abs(temp["High"] - temp["Close"].shift(1)) # high - previous day close
    temp["L-PC"] = abs(temp["Low"] - temp["Close"].shift(1))
    temp["TR"] = temp[["H-L", "H-PC", "L-PC"]].max(axis=1, skipna = False)
    temp["ATR"] = temp["TR"].rolling(n).mean()
    
    return_val = temp.drop(["H-L","H-PC","L-PC"], axis=1)
    return return_val

def slope(ser, n=5):
    slopes = [i*0 for i in range(n-1)]
    for i in range(n,len(ser)+1):
        y = ser[i-n:i]
        x = np.array(range(n))
        y_scaled = (y-y.min())/(y.max() - y.min())
        x_scaled = (x-x.min())/(x.max() - x.min())
        x_scaled = sm.add_constant(x_scaled)
        model = sm.OLS(y_scaled, x_scaled)
        results = model.fit()
        slopes.append(results.params[-1])
    slope_angle = (np.rad2deg(np.arctan(np.array(slopes))))
    return np.array(slope_angle)

def renko_DF(DF):
    df = DF.copy()
    df.reset_index(inplace=True)
    print("reseting date")
    df = df.iloc[:,[0,1,2,3,4,5]]
    df.columns = ["date", "low", "high", "open", "close", "volume"]

    df2 = Renko(df)
    df2.brick_size = max(0.5, round(ATR(DF,120)["ATR"][-1],0))
    renko_df = df2.get_ohlc_data()
    renko_df["bar_num"] = np.where(renko_df["uptrend"] == True, 1, np.where(renko_df["uptrend"] == False, -1, 0))
    for i in range(1, len(renko_df["bar_num"])):
        if renko_df["bar_num"][i]>0 and renko_df["bar_num"][i-1] >0:
            renko_df["bar_num"].iloc[i] += renko_df["bar_num"][i-1]
        elif renko_df["bar_num"][i]<0 and renko_df["bar_num"][i-1] <0:
            renko_df["bar_num"].iloc[i] += renko_df["bar_num"][i-1]
    renko_df.drop_duplicates(subset="date", keep="last", inplace=True)
    return renko_df


tickers = ["MSFT", "AMZN", "AAPL", "FB", "CSCO"]
ts = TimeSeries(key="K1I429GVVREGYUWT", output_format = "pandas")
ohlc_dict = {}
for ticker in tickers:
    try:
        ohlc_dict[ticker] = ts.get_intraday(ticker, interval = "5min", outputsize="full")[0]
        print("got data")
        ohlc_dict[ticker] = ohlc_dict[ticker][::-1]
        print("reversed date")
        ohlc_dict[ticker].columns = ["Open", "High", "Low", "Close", "Volume"]
        print("renamed columns")
    except:
        print("AlphaVantage API Request Limit")
        continue
    
tickers = ohlc_dict.keys()

ohlc_renko = {}
df = copy.deepcopy(ohlc_dict)
tickers_signal = {}
tickers_ret = {}
for ticker in tickers:
    renko = renko_DF(df[ticker])
   # df[ticker]["date"] = df[ticker].index
    ohlc_renko[ticker] = df[ticker].merge(renko.loc[:,["date", "bar_num"]], how = "outer", on = "date")
    ohlc_renko[ticker]["bar_num"].fillna(method="ffill", inplace = True)
    ohlc_renko[ticker]["MACD"] = MACD(ohlc_renko[ticker])[0]
    ohlc_renko[ticker]["Signal"] = MACD(ohlc_renko[ticker])[1]
    ohlc_renko[ticker]["MACD_Slope"] = slope(ohlc_renko[ticker]["MACD"])
    ohlc_renko[ticker]["Signal_Slope"] = slope(ohlc_renko[ticker]["Signal"])
    tickers_signal[ticker] = ""
    tickers_ret[ticker] = []
    
    
for ticker in tickers:
    for i in range(len(ohlc_dict[ticker])):
        if tickers_signal[ticker] == "":
            tickers_ret[ticker].append(0)
            if i > 0:
                if ohlc_renko[ticker]["bar_num"][i] >= 2 and ohlc_renko[ticker]["MACD"][i] > ohlc_renko[ticker]["Signal"][i] and ohlc_renko[ticker]["MACD_Slope"][i] > ohlc_renko[ticker]["Signal_Slope"][i]:
                    tickers_signal[ticker] = "Buy"
                elif ohlc_renko[ticker]["bar_num"][i] <= -2 and ohlc_renko[ticker]["MACD"][i] < ohlc_renko[ticker]["Signal"][i] and ohlc_renko[ticker]["MACD_Slope"][i] < ohlc_renko[ticker]["Signal_Slope"][i]:
                    tickers_signal[ticker] = "Sell"
                    
        elif tickers_signal[ticker] == "Buy":
            tickers_ret[ticker].append((ohlc_renko[ticker]["Close"][i]/ohlc_renko[ticker]["Close"][i-1])-1)
            if i > 0:
                if ohlc_renko[ticker]["bar_num"][i] <= -2 and ohlc_renko[ticker]["MACD"][i] < ohlc_renko[ticker]["Signal"][i] and ohlc_renko[ticker]["MACD_Slope"][i] < ohlc_renko[ticker]["Signal_Slope"][i]:
                    tickers_signal[ticker] == "Sell"
                elif ohlc_renko[ticker]["MACD"][i] < ohlc_renko[ticker]["Signal"][i] and ohlc_renko[ticker]["MACD_Slope"][i] < ohlc_renko[ticker]["Signal_Slope"][i]:
                    tickers_signal[ticker] == ""
                    
        elif tickers_signal[ticker] == "Sell":
            tickers_ret[ticker].append((ohlc_renko[ticker]["Close"][i-1]/ohlc_renko[ticker]["Close"][i])-1)
            if i > 0:
                if ohlc_renko[ticker]["bar_num"][i] >= 2 and ohlc_renko[ticker]["MACD"][i] > ohlc_renko[ticker]["Signal"][i] and ohlc_renko[ticker]["MACD_Slope"][i] > ohlc_renko[ticker]["Signal_Slope"][i]:
                    tickers_signal[ticker] == "Buy"
                elif ohlc_renko[ticker]["MACD"][i] > ohlc_renko[ticker]["Signal"][i] and ohlc_renko[ticker]["MACD_Slope"][i] > ohlc_renko[ticker]["Signal_Slope"][i]:
                    tickers_signal[ticker] == ""
                    
    ohlc_renko[ticker]["Return"] = np.array(tickers_ret[ticker])
                           