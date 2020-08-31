# -*- coding: utf-8 -*-
"""
Created on Mon Aug 17 09:17:20 2020

@author: 97vin
"""

import pandas as pd
from stocktrends import Renko
import statsmodels.api as sm
from alpha_vantage.timeseries import TimeSeries
import copy
import numpy as np

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

def OBV(DF):
    temp = DF.copy()
    
    temp["Delta"] = temp["Close"] - temp["Close"].shift(1)
    temp["Direction"] = np.where(temp["Delta"] > 0, 1, -1)
    temp["Direction"] = np.where(temp["Delta"] == 0, 0, temp["Direction"])
    temp["OBV"] = (temp["Direction"] * temp["Volume"]).cumsum()
    
    temp.drop(["Delta", "Direction"], axis=1, inplace=True)
    return temp

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


#getting original data
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

# merging renko data with original
ohlc_renko = {}
df = copy.deepcopy(ohlc_dict)
tickers_signal = {}
tickers_ret = {}
for ticker in tickers:
    renko = renko_DF(df[ticker])
   # df[ticker]["date"] = df[ticker].index
    ohlc_renko[ticker] = df[ticker].merge(renko.loc[:,["date", "bar_num"]], how = "outer", on="date")
    ohlc_renko[ticker]["bar_num"].fillna(method="ffill", inplace = True)
    ohlc_renko[ticker]["obv"] = OBV(ohlc_renko[ticker])["OBV"]
    ohlc_renko[ticker]["obv_slope"] = slope(ohlc_renko[ticker]["obv"])
    tickers_signal[ticker] = ""
    tickers_ret[ticker] = []
    
for ticker in tickers:
    for i in range(len(ohlc_dict[ticker])):
        if tickers_signal[ticker] == "":
            tickers_ret[ticker].append(0)
            if ohlc_renko[ticker]["bar_num"][i] >= 2 and ohlc_renko[ticker]["obv_slope"][i]>30:
                tickers_signal[ticker] = "Buy"
            elif ohlc_renko[ticker]["bar_num"][i] <= 2 and ohlc_renko[ticker]["obv_slope"][i] < -30:
                tickers_signal[ticker] = "Sell"
                
        elif tickers_signal[ticker] == "Buy":
            tickers_ret[ticker].append((ohlc_renko[ticker]["Close"][i]/ohlc_renko[ticker]["Close"][i-1]) - 1)
            if ohlc_renko[ticker]["bar_num"][i] <= 2 and ohlc_renko[ticker]["obv_slope"][i] < -30:    
                tickers_signal[ticker] = "Sell"
            elif ohlc_renko[ticker]["bar_num"][i] < 2:
                tickers_signal[ticker] = ""
                
        elif tickers_signal[ticker] == "Sell":
            tickers_ret[ticker].append((ohlc_renko[ticker]["Close"][i-1]/ohlc_renko[ticker]["Close"][i]) - 1)
            if ohlc_renko[ticker]["bar_num"][i] >= 2 and ohlc_renko[ticker]["obv_slope"][i] > 30:    
                tickers_signal[ticker] = "Buy"
            elif ohlc_renko[ticker]["bar_num"][i] > -2:
                tickers_signal[ticker] = ""
    ohlc_renko[ticker]["Return"] = np.array(tickers_ret[ticker])