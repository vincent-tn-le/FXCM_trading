# -*- coding: utf-8 -*-
"""
Created on Thu Aug 13 12:37:11 2020

@author: 97vin
"""

import pandas_datareader as pdr
import datetime as dt
import numpy as np

from stocktrends import Renko

ticker = "AAPL"
start_date = dt.date.today() - dt.timedelta(365)
end_date = dt.date.today()

original_data = pdr.get_data_yahoo(ticker, start_date, end_date, interval = "d")
df = original_data.copy()

def ATR(DF,n=20):
    temp = DF.copy()
    temp["H-L"] = abs(temp["High"] - temp["Low"]) 
    temp["H-PC"] = abs(temp["High"] - temp["Adj Close"].shift(1)) # high - previous day close
    temp["L-PC"] = abs(temp["Low"] - temp["Adj Close"].shift(1))
    temp["TR"] = temp[["H-L", "H-PC", "L-PC"]].max(axis=1, skipna = False)
    temp["ATR"] = temp["TR"].rolling(n).mean()
    
    return_val = temp.drop(["H-L","H-PC","L-PC"], axis=1)
    return return_val

df.reset_index(inplace = True)
df = df.drop(["Close"], axis=1)
df.columns = ["date", "high", "low", "open", "volume", "close"]

renko_df = Renko(df)
renko_df.brick_size = 10
renko_df.chart_type = Renko.PERIOD_CLOSE

df2 = renko_df.get_ohlc_data()
df2.set_index("date", inplace = True)

def renko_DF(DF):
    df = DF.copy()
    df.reset_index(inplace=True)
    df = df.iloc[:,[0,1,2,3,4,5]]
    df.columns = ["date", "low", "high", "open", "close", "volume"]

    df2 = Renko(df)
    df2.brick_size = max(0.5, round(ATR(DF,120)["ATR"][-1],0))