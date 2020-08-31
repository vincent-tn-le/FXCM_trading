# -*- coding: utf-8 -*-
"""
Created on Thu Aug 13 10:47:04 2020

@author: 97vin
"""

import pandas_datareader as pdr
import datetime as dt
import numpy as np
import statsmodels.api as sm

ticker = "AAPL"
start_date = dt.date.today() - dt.timedelta(365)
end_date = dt.date.today()

original_data = pdr.get_data_yahoo(ticker, start_date, end_date, interval = "d")

def slope(ser, n=5):
    slopes = [i*0 for i in range(n-1)]
    for i in range(n,len(ser)+1):
        y = ser[i-n:i]
        x = np.array(range(n))
        y_scaled = (y-y.min())/(y.max() - y.min())
        x_scaled = (x-x.min())/(x.max() - x.min())
        x_scaled = sm.add_constant(x_scaled)
        model = sm.OLS(y_scaled, x_scaled)
        results = model.fit()
        slopes.append(results.params[-1])
    slope_angle = (np.rad2deg(np.arctan(np.array(slopes))))
    return np.array(slope_angle)