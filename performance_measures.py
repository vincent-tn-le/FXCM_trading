# -*- coding: utf-8 -*-
"""
Created on Fri Aug 14 10:06:47 2020

@author: 97vin
"""

import pandas_datareader.data as pdr
import numpy as np
import datetime as dt

ticker = "^GSPC"
start_date = dt.date.today() - dt.timedelta(1825)
end_date = dt.date.today()

SnP = pdr.get_data_yahoo(ticker, start_date, end_date)

def CAGR(DF):
    temp = DF.copy()
    temp["Daily Return"] = temp["Adj Close"].pct_change()
    temp["Cumulative Return"] = (1+temp["Daily Return"]).cumprod()
    
    CAGR = (temp["Cumulative Return"][-1])**(1/(len(temp)/252)) - 1
    return CAGR

def CAGR2(DF):
    temp = DF.copy()
    return (temp["Adj Close"][-1]/temp["Adj Close"][0])**(1/(len(temp)/252)) - 1

def volatility(DF):
    temp = DF.copy()
    return temp["Adj Close"].pct_change().std()*(np.sqrt(252))

def sharpe(DF,rf): #risk-free rate changes depends on the market
    temp = DF.copy()
    return (CAGR(temp) - rf)/volatility(temp)

def sortino(DF, rf):
    temp = DF.copy()
    vol = temp["Adj Close"].pct_change()[temp["Adj Close"].pct_change() < 0].std()*np.sqrt(252)
    return (CAGR(temp) - rf)/vol
    
def sortino2(DF,rf):
    temp = DF.copy()
    temp["Daily Return"] = temp["Adj Close"].pct_change()
    neg_vol = temp[temp["Daily Return"] < 0]["Daily Return"].std() * np.sqrt(252)
    sr = (CAGR(temp) - rf)/neg_vol
    return sr

def max_drawdown(DF):
    temp = DF.copy()
    temp["Daily Return"] = temp["Adj Close"].pct_change()
    temp["Cumulative Return"] = (1+temp["Daily Return"]).cumprod()
    
    temp["Cumulative Return Max"] = temp["Cumulative Return"].cummax()
    temp["Range"] = (temp["Cumulative Return Max"] - temp["Cumulative Return"])/temp["Cumulative Return Max"]
    drawdown = temp["Range"].max()
    
    return drawdown

def calmar(DF):
    return CAGR(DF)/max_drawdown(DF)