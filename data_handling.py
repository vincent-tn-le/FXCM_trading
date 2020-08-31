# -*- coding: utf-8 -*-
"""
Created on Sun Aug  9 17:32:01 2020

@author: 97vin
"""

import pandas as pd
import pandas_datareader.data as pdr
import datetime as dt

start_date = dt.date.today() - dt.timedelta(3650)
end_date = dt.date.today()

tickers = ["MSFT","AMZN","AAPL","CSCO","IBM","FB"]

stock_cp = pd.DataFrame() # final dataframe to store close price of ticker
attempt = 0 # passthrough variable
drop = [] # initializing list to store tickers whose close price was successfully extracted

while len(tickers) != 0 and attempt <= 5:
    # removing stocks whose data has been extracted
    tickers = [j for j in tickers if j not in drop]
    for i in range(len(tickers)):
        try:
            temp = pdr.get_data_yahoo(tickers[i], start_date, end_date, interval = "d")
            temp.dropna(inplace = True)
            stock_cp[tickers[i]] = temp["Adj Close"]
            drop.append(tickers[i])
        except:
            print(tickers[i], ": failed to fetch data ... retrying")
    attempt += 1

# Handling NaN values
stock_cp.fillna(method = "bfill", inplace = True)
stock_cp.dropna(axis=0, inplace = True)

# Mean, Median, Standard Deviation, daily return
stock_cp.mean(axis=0) # along columns - by companies
stock_cp.mean(axis=1) # along rows - by day
stock_cp.median(axis=0)
stock_cp.std(axis=0)

daily_return = stock_cp.pct_change()
(stock_cp/stock_cp.shift(1)) - 1
daily_return.std()

# Rolling mean and standard deviation
daily_return_rolling = daily_return.rolling(window = 20, min_periods = 1).mean()
daily_return.rolling(window = 20).std()
daily_return.ewm(span = 20, min_periods = 20).mean() #exponential weighted moveing average













