# -*- coding: utf-8 -*-
"""
Created on Sun Aug  9 10:57:36 2020

@author: 97vin
"""

from alpha_vantage.timeseries import TimeSeries
import pandas as pd

# AlphaVantage API key: K1I429GVVREGYUWT

ts = TimeSeries(key="K1I429GVVREGYUWT", output_format = "pandas")
data, meta_data = ts.get_intraday("MSFT", interval="1min", outputsize="full")
data.columns = ["Open", "High", "Low", "Close", "Volume"]
