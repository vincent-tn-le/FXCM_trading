# -*- coding: utf-8 -*-
"""
Created on Sun Aug 16 10:34:23 2020

@author: 97vin
"""

import numpy as np
import pandas as pd
import pandas_datareader as pdr
import datetime as dt
import matplotlib.pyplot as plt
import copy


## Key performance indicators adjusted for monthly returns
def CAGR(DF):
    temp = DF.copy()
    temp["Cumulative Return"] = (1+temp["Monthly Return"]).cumprod()
    CAGR = (temp["Cumulative Return"].tolist()[-1])**(1/(len(temp)/12)) - 1
    return CAGR

def volatility(DF):
    temp = DF.copy()
    vol = temp["Monthly Return"].std()*(np.sqrt(12))
    return vol

def sharpe(DF,rf): #risk-free rate changes depends on the market
    temp = DF.copy()
    return (CAGR(temp) - rf)/volatility(temp)

def max_drawdown(DF):
    temp = DF.copy()
    temp["Cumulative Return"] = (1+temp["Monthly Return"]).cumprod()
    
    temp["Cumulative Return Max"] = temp["Cumulative Return"].cummax()
    temp["Range"] = (temp["Cumulative Return Max"] - temp["Cumulative Return"])/temp["Cumulative Return Max"]
    drawdown = temp["Range"].max()
    return drawdown

def calmar(DF):
    return CAGR(DF)/max_drawdown(DF)


## DJI constituent stocks
tickers = ["AXP", "JPM", "MRK", "NKE", "AAPL", "MSFT", "KO", "MMM", "JNJ", "IBM",
           "GS", "MCD", "PFE", "DIS", "HD", "XOM", "VZ", "V", "PG", "CAT", "CSCO",
           "RTX", "TRV", "WMT", "CVX", "UNH", "INTC", "DOW", "BA", "WBA"]

start_date = dt.date.today() - dt.timedelta(10*365)
end_date = dt.date.today()
ohlc_mon = {}
attempt = 0
drop = []

    tickers = [j for j in tickers if j not in drop]
    for i in range(len(tickers)):
        try:
            ohlc_mon[tickers[i]] = pdr.get_data_yahoo(tickers[i], start_date, end_date, interval='m')
            ohlc_mon[tickers[i]].dropna(inplace=True)
            drop.append(tickers[i])
        except:
            print(tickers[i], ": failed to fetch data... retrying")
            continue
    attempt+=

for i in range(len(tickers)):
    try:
        ohlc_mon[tickers[i]] = pdr.get_data_yahoo(tickers[i], start_date, end_date, interval='m')
        ohlc_mon[tickers[i]].dropna(inplace=True)
    except:
        print(tickers[i], ": failed to fetch data... retrying")
        continue
    
tickers = ohlc_mon.keys()

## Backtesting
ohlc_dict = copy.deepcopy(ohlc_mon)
return_df = pd.DataFrame()

for ticker in tickers:
    ohlc_dict[ticker]["Monthly Return"] = ohlc_dict[ticker]["Adj Close"].pct_change()
    return_df[ticker] = ohlc_dict[ticker]["Monthly Return"]
    
# portfolio return
# assuming equal distribution of stocks
def pftlio(DF,m,x):
    temp = DF.copy()
    portfolio = []
    monthly_return = []
    for i in range(1,len(temp)):
        if len(portfolio) > 0:
            monthly_return.append(temp[portfolio].iloc[i,:].mean())
            bad_stocks = temp[portfolio].iloc[i,:].sort_values(ascending=True)[:x].index.values.tolist()
            portfolio = [t for t in portfolio if t not in bad_stocks]
        fill = m - len(portfolio)
        new_picks = temp.iloc[i,:].sort_values(ascending = False)[:fill].index.values.tolist()
        portfolio = portfolio + new_picks
        print(portfolio)
    monthly_ret_df = pd.DataFrame(np.array(monthly_return), columns = ["Monthly Return"])
    return monthly_ret_df

CAGR(pftlio(return_df, 6, 3))
sharpe(pftlio(return_df, 6, 3),0.025)
calmar(pftlio(return_df, 6, 3))

    
## Benchmark
DJI = pdr.get_data_yahoo("^DJI", start_date, end_date, interval='m')
DJI["Monthly Return"] = DJI["Adj Close"].pct_change()
CAGR(DJI) # 0.11197029174395756
sharpe(DJI, 0.025) #0.5845324907200347
calmar(DJI) #0.4826042292147098
