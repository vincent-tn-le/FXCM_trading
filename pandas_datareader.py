# -*- coding: utf-8 -*-
"""
Created on Sat Aug  8 10:26:48 2020

@author: 97vin
"""

# Import necessary libraries
import pandas as pd
import pandas_datareader.data as pdr
import datetime as dt

# Single ticker example
ticker = "AMZN"
start_date = dt.date.today() - dt.timedelta(365)
end_date = dt.date.today()

data = pdr.get_data_yahoo(ticker, start_date, end_date, interval = "m")

# Multiple Ticker Example
tickers = ["ASIANPAINT.NS", "ADANIPORTS.NS", "AXISBANK.NS", "BAJAJ-AUTO.NS",
           "BAJFINANCE.NS", "BAJAJFINSV.NS", "BPCL.NS", "BHARTIARTL.NS",
           "INFRATEL.NS","CIPLA.NS","COALINDIA.NS","DRREDOY.NS","EICHERMOT.NS",
           "GAIL.NS", "GRASIM.NS", "HCLTECH.NS", "HOFCBANK.NS","HERMOTOCO.NS",
           "HINDALCO.NS","HINDPETRO.NS","HINDUNILVR.NS","HDFC.NS","ITC.NS",
           "ICICIBANK.NS", "IBULMSGFIN.NS","IOC.NS","INDUSINDOK.NS", "INFY.NS",
           "KOTAKBANK.NS","LT.NS","LUPIN.NS","M&M.NS", "MARUTI.NS", "NTPC.NS",
           "ONGC.NS", "POWERGRID.NS", "RELIANCE.NS", "SBIN.NS", "SUNPHARMA.NS",
           "TCS.NS", "TATAMOTORS.NS", "TATASTEEL.NS","TECHM.NS", "TITAN.NS",
           "UPL.NS","ULTRACEMCO.NS","VEDL.NS","WIPRO.NS","YESBANK.NS","ZEEL.NS"]

stock_cp = pd.DataFrame() # final dataframe to store close price of ticker
attempt = 0 # passthrough variable
drop = [] # initializing list to store tickers whose close price was successfully extracted

while len(tickers) != 0 and attempt <= 5:
    # removing stocks whose data has been extracted
    tickers = [j for j in tickers if j not in drop]
    for i in range(len(tickers)):
        try:
            temp = pdr.get_data_yahoo(tickers[i], start_date, end_date, interval = "m")
            temp.dropna(inplace = True)
            stock_cp[tickers[i]] = temp["Adj Close"]
            drop.append(tickers[i])
        except:
            print(tickers[i], ": failed to fetch data ... retrying")
    attempt += 1


# the nested loop accounts for API failures, and perhaps on another run through it may work
# otherwise attempting this on my own, it would have just been the for loop
