# -*- coding: utf-8 -*-
"""
Created on Sat Aug  8 11:32:06 2020

@author: 97vin
"""

import pandas as pd
import datetime as dt
from yahoofinancials import YahooFinancials

# single ticker example
ticker = "AAPL"
yahoo_financials = YahooFinancials(ticker)
historical_stock_prices = yahoo_financials.get_historical_price_data('2007-08-15', '2008-09-15', 'daily')

# multi level dictionary example
country_data = {"USA": 
                {"Capital City": "Washington DC", 
                 "Currency": "USD", 
                 "Major_cities": ["NY", "LA", "SF"]},
                "France":
                    {"Capital City": "Paris",
                     "Currency": "Euro",
                     "Major_cities": ["Paris", "Dunkirk"]}}
    

# multiple ticker example
all_tickers = ["AAPL", "MSFT", "CSCO", "AMZN", "INTC"]

close_price = pd.DataFrame()
end_date = (dt.date.today()).strftime("%Y-%m-%d") 
start_date = (dt.date.today() - dt.timedelta(365)).strftime("%Y-%m-%d")
cp_tickers = all_tickers
attempt = 0
drop = []

while len(cp_tickers) != 0 and attempt <=5:
    cp_tickers = [j for j in cp_tickers if j not in drop]
    for i in range(len(cp_tickers)):
        try:
            yahoo_financials = YahooFinancials(cp_tickers[i]) #creating object
            json_obj = yahoo_financials.get_historical_price_data(start_date, end_date, "daily") #getting dictionary from obj
            chlv = json_obj[cp_tickers[i]]['prices'] #accessing prices
            temp = pd.DataFrame(chlv)[["formatted_date", "adjclose"]] # only the closing price
            temp.set_index("formatted_date", inplace=True) # setting the index to be the date
            temp2 = temp[~temp.index.duplicated(keep="first")] # accounting for dividend payouts
            close_price[cp_tickers[i]] = temp2["adjclose"] # Writing to main dictionary
            drop.append(cp_tickers[i]) #done with the ticker
        except:
            print(cp_tickers[i] + ": failed to fetch data... retrying")
            continue
    attempt += 1
    