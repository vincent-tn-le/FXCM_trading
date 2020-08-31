# -*- coding: utf-8 -*-
"""
Created on Wed Aug 12 09:18:47 2020

@author: 97vin
"""

import pandas_datareader as pdr
import datetime as dt

ticker = "MSFT"
start_date = dt.date.today() - dt.timedelta(365)
end_date = dt.date.today()

original_data = pdr.get_data_yahoo(ticker, start_date, end_date, interval = "d")

def ATR(DF,n=20):
    temp = DF.copy()
    temp["H-L"] = abs(temp["High"] - temp["Low"]) 
    temp["H-PC"] = abs(temp["High"] - temp["Adj Close"].shift(1)) # high - previous day close
    temp["L-PC"] = abs(temp["Low"] - temp["Adj Close"].shift(1))
    temp["TR"] = temp[["H-L", "H-PC", "L-PC"]].max(axis=1, skipna = False)
    temp["ATR"] = temp["TR"].rolling(n).mean()
    
    return_val = temp.drop(["H-L","H-PC","L-PC"], axis=1)
    return return_val


def bollinger_bands(DF, n=20, a = 2):
    temp = DF.copy()
    temp["MA"] = temp["Adj Close"].rolling(n).mean()
    temp["BB_up"] = temp["MA"] + a*temp["MA"].rolling(n).std()
    temp["BB_down"] = temp["MA"] - a*temp["MA"].rolling(n).std()
    temp["BB_range"] = temp["BB_up"] - temp["BB_down"]

    temp.dropna(inplace=True)
    return temp