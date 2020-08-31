# -*- coding: utf-8 -*-
"""
Created on Wed Aug 12 10:44:38 2020

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

def ADX(DF, n=14):
    temp = DF.copy()
    
    temp["H-L"] = abs(temp["High"] - temp["Low"]) 
    temp["H-PC"] = abs(temp["High"] - temp["Adj Close"].shift(1)) # high - previous day close
    temp["L-PC"] = abs(temp["Low"] - temp["Adj Close"].shift(1))
    temp["TR"] = temp[["H-L", "H-PC", "L-PC"]].max(axis=1, skipna = False)
    
    dm_p = []
    highs = (temp["High"] - temp["High"].shift(1)).tolist()
    lows = (temp["Low"].shift(1) - temp["Low"]).tolist()
    for i in range(len(temp)):
        if highs[i] > lows[i]:
            dm_p.append(max(highs[i],0))
        else:
            dm_p.append(0)
    
    dm_n = []    
    highs = (temp["High"].shift(1) - temp["High"]).tolist()
    lows = (temp["Low"] - temp["Low"].shift(1)).tolist()  
    for i in range(len(temp)):
        if lows[i] > highs[i]:
            dm_n.append(max(lows[i],0))
        else:
            dm_n.append(0)
    
    temp["DM+"] = np.array(dm_p)
    temp["DM-"] = np.array(dm_n)
    
    tr_14 = []
    dm_p_14 = []
    dm_n_14 = []
    tr_lst = temp["TR"].tolist()
    
    for i in range(len(temp)):
       if i < n:
            tr_14.append(np.NaN)
            dm_p_14.append(np.NaN)
            dm_n_14.append(np.NaN)
       elif i == n:
            tr_14.append(temp['TR'].rolling(n).mean().tolist()[n])
            dm_p_14.append(temp['DM+'].rolling(n).mean().tolist()[n])
            dm_n_14.append(temp['DM-'].rolling(n).mean().tolist()[n])
       elif i > n:
            tr_14.append(tr_14[i-1]-tr_14[i-1]/n + tr_lst[i])
            dm_p_14.append(dm_p_14[i-1]-dm_p_14[i-1]/n+dm_p[i])
            dm_n_14.append(dm_n_14[i-1]-dm_n_14[i-1]/n+dm_n[i])
            
    temp["DI+"] = 100*(np.array(dm_p_14)/np.array(tr_14))
    temp["DI-"] = 100*(np.array(dm_n_14)/np.array(tr_14))
    
    temp["DI+ Sum"] = temp["DI+"] +  temp["DI-"]
    temp["DI+ Diff"] = abs(temp["DI+"] - temp["DI-"])
    temp["DX"] = 100*(temp["DI+ Diff"]/temp["DI+ Sum"])
    
    adx_lst = []
    dx = temp["DX"].tolist()
    
    for i in range(len(temp)):
        if i < 2*n: # a rolling calculation of a rolled calcuation
            adx_lst.append(np.NaN)
        elif i == 2*n:
            adx_lst.append(temp['DX'].rolling(n).mean().tolist()[2*n])
        elif i > 2*n:
            adx_lst.append(((n-1)*adx_lst[i-1] + dx[i])/n)
    
    temp["ADX"] = np.array(adx_lst)
    return_val = temp.drop(["H-L", "L-PC", "TR" , "DM+", "DM-", "DI+", "DI-", "DI+ Sum", "DI+ Diff", "DX"], axis=1)
    return return_val
            
            