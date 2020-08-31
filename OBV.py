# -*- coding: utf-8 -*-
"""
Created on Thu Aug 13 09:48:58 2020

@author: 97vin
"""

import pandas_datareader as pdr
import datetime as dt
import numpy as np

ticker = "AAPL"
start_date = dt.date.today() - dt.timedelta(365)
end_date = dt.date.today()

original_data = pdr.get_data_yahoo(ticker, start_date, end_date, interval = "d")

temp=original_data.copy()

def OBV(DF):
    temp = DF.copy()
    
    temp["Delta"] = temp["Adj Close"] - temp["Adj Close"].shift(1)
    temp["Direction"] = np.where(temp["Delta"] > 0, 1, -1)
    temp["Direction"] = np.where(temp["Delta"] == 0, 0, temp["Direction"])
    temp["OBV"] = (temp["Direction"] * temp["Volume"]).cumsum()
    
    return_val = temp.drop(["Delta", "Direction"])
    return return_val