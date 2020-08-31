# -*- coding: utf-8 -*-
"""
Created on Thu Aug 13 13:08:34 2020

@author: 97vin
"""

import talib
from alpha_vantage.timeseries import TimeSeries
import copy
import pandas as pd

ts = TimeSeries(key="K1I429GVVREGYUWT", output_format = "pandas")
tickers = ["MSFT", "AAPL", "FB", "AMZN", "CSCO"]#, "IBM", "LYFT"]

ohlc_tech = {}
done = []

for i in range(len(tickers)):
    try:
        ohlc_tech[tickers[i]] = ts.get_daily(tickers[i], outputsize="full")[0]
        ohlc_tech[tickers[i]].columns = ["Open", "High", "Low", "Close", "Vol"]
        done.append(tickers[i])
    except:
        print(tickers[i], ": failed to fetch data ... retrying")
        continue
    
tickers = ohlc_tech.keys() # remove corrupted data

ohlc_dict = copy.deepcopy(ohlc_tech)

for ticker in ohlc_dict:
    ohlc_dict[ticker]["3I"] = talib.CDL3INSIDE(ohlc_dict[ticker]["Open"], 
                                               ohlc_dict[ticker]["High"], 
                                               ohlc_dict[ticker]["Low"], 
                                               ohlc_dict[ticker]["Close"])
    