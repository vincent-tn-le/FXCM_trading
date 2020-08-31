# -*- coding: utf-8 -*-
"""
Created on Wed Aug 12 09:56:47 2020

@author: 97vin
"""

import pandas_datareader as pdr
import datetime as dt
import numpy as np

ticker = "MSFT"
start_date = dt.date.today() - dt.timedelta(365)
end_date = dt.date.today()

original_data = pdr.get_data_yahoo(ticker, start_date, end_date, interval = "d")



def RSI(DF, n = 14):
    temp = DF.copy()
    temp["Diff"] = temp["Adj Close"] - temp["Adj Close"].shift(1)
    temp["Gain"] = temp.apply(lambda x: max(x["Diff"],0), axis=1)
    temp["Loss"] = abs(temp.apply(lambda x: min(x["Diff"],0), axis=1))
    
    av_gain = []
    av_loss = []
    gain = temp["Gain"].tolist()
    loss = temp["Loss"].tolist()
    
    for i in range(len(temp)):
        if i < n:
            av_gain.append(np.NaN)
            av_loss.append(np.NaN)
        elif i == n:
            av_gain.append(temp['Gain'].rolling(n).mean().tolist()[n])
            av_loss.append(temp['Loss'].rolling(n).mean().tolist()[n])
        elif i > n:
            av_gain.append(((n-1)*av_gain[i-1] + gain[i])/n)
            av_loss.append(((n-1)*av_loss[i-1] + loss[i])/n)
    
    temp["Avg Gain"] = np.array(av_gain)
    temp["Avg Loss"] = np.array(av_loss)
    temp["RS"] = temp["Avg Gain"]/temp["Avg Loss"]
    temp["RSI"] = 100 - (100/(1+temp["RS"]))
    
    return_val = temp.drop(["Diff", "Gain", "Loss","Avg Gain","Avg Loss", "RS"], axis=1)
    return return_val
