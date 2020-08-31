# -*- coding: utf-8 -*-
"""
Created on Tue Aug 11 14:59:48 2020

@author: 97vin
"""

import pandas_datareader as pdr
import datetime as dt
import matplotlib.pyplot as plt


ticker = "MSFT"
start_date = dt.date.today() - dt.timedelta(365)
end_date = dt.date.today()

original_data = pdr.get_data_yahoo(ticker, start_date, end_date, interval = "d")

df = original_data.copy()
df["MA_fast"] = df["Adj Close"].ewm(span=12, min_periods=12).mean()
df["MA_slow"] = df["Adj Close"].ewm(span = 26, min_periods=26).mean()
df["MACD"] = df["MA_fast"] - df["MA_slow"]
df["Signal"] = df["MACD"].ewm(span=9, min_periods=9).mean()

df.dropna(axis=0,inplace=True)
df = df[["Adj Close","MACD", "Signal"]]


# Lagging indicator
def MACD(df, a=12, b=26, c=9):
    temp = df.copy()
    temp["MA_fast"] = temp["Adj Close"].ewm(span=a, min_periods=a).mean()
    temp["MA_slow"] = temp["Adj Close"].ewm(span=b, min_periods=b).mean()
    temp["MACD"] = temp["MA_fast"] - temp["MA_slow"]
    temp["Signal"] = temp["MACD"].ewm(span=c, min_periods=c).mean()
    temp.dropna(axis=0, inplace=True)
    return temp

fig, (ax0, ax1) = plt.subplots(nrows = 2, ncols = 1, sharex = True, figsize = (7,4))

# Closing price plot
ax0.plot(list(df.index), list(df["Adj Close"]), color = 'black')
ax0.set(title="Closing Price", ylabel="Price ($)")

# MACD plot
ax1.plot(list(df.index), list(df["MACD"]), color = 'red', linewidth = 0.5, label = "MACD")
ax1.plot(list(df.index), list(df["Signal"]), color = 'blue', linewidth = 0.5, label = "Signal")
ax1.set(title="MACD and Signal", xlabel = "Date", ylabel="MACD")
ax1.legend(loc='upper left', frameon=False)
fig.suptitle("MSFT 2020 Year", fontsize=14, fontweight="bold")
