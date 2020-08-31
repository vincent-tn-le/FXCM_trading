# -*- coding: utf-8 -*-
"""
Created on Mon Aug 10 10:26:55 2020

@author: 97vin
"""

import pandas as pd
import pandas_datareader.data as pdr
import datetime as dt
import matplotlib.pyplot as plt


start_date = dt.date.today() - dt.timedelta(3650)
end_date = dt.date.today()

tickers = ["MSFT","AMZN","AAPL","CSCO","IBM","FB"]

stock_cp = pd.DataFrame() # final dataframe to store close price of ticker
attempt = 0 # passthrough variable
drop = [] # initializing list to store tickers whose close price was successfully extracted


# doesn't work for some reason
while len(tickers)!=0 and attempt <= 5:
    #tickers = [j for j in tickers if j not in drop]
    print("attempt: " + str(attempt))
    print("ticker: " + str(tickers))
    print("ticker len: " + str(len(tickers)))
    print("drop: " + str(drop))

    for i in range(len(tickers)):
        try:
            print("for loop try")
            temp = pdr.get_data_yahoo(tickers[i], start_date, end_date, interval = "m")
            temp.dropna(inplace = True)
            stock_cp[tickers[i]] = temp["Adj Close"]
            drop.append(tickers[i])
        except:
            print("except")
            print(tickers[i], ": failed to fetch data ... retrying")
            continue
    tickers = [j for j in tickers if j not in drop]
    attempt+=1
    print("ticker after loop: " + str(tickers))
    print("ticker len: " + str(len(tickers)))
    print("drop after loop: " + str(drop))



# This works to update stock_cp
for i in tickers:
    try:
        temp = pdr.get_data_yahoo(i, start_date, end_date, interval = "d")
        temp.dropna(inplace = True)
        stock_cp[i] = temp["Adj Close"]
    except:
        print(i, ": failed to fetch data ... retrying")
        continue
stock_cp["Date"] = stock_cp.index



# Visualization using built in pandas
stock_cp.plot()
((stock_cp - stock_cp.mean())/stock_cp.std()).plot() #plot of Z scores over time

stock_cp.plot(subplots = True, layout = (2,3), grid = True)


# Visualization with matplotlib/pyplot
stock_cp.fillna(method='bfill', inplace=True)
daily_return = stock_cp.pct_change()

plt.style.available
plt.style.use("seaborn")
stock_cp.plot()

fig, ax = plt.subplots()
stock_cp.plot(kind = "line", y="AAPL", x="Date", ax=ax)
ax.set_xlim(stock_cp["Date"][0],stock_cp["Date"][-1])
ax.set(title="AAPL Stock Evolution", ylabel= "Price", xlabel = "Date")
plt.show()

# Bar chart
fig, ax = plt.subplots(figsize = (7,4))
ax.bar(daily_return.columns, daily_return.mean())
ax.set(title= "Daily Returns for Big Tech", xlabel = "Ticker", ylabel = "Return")
avg_return = daily_return.dropna().values.mean()
ax.axhline(y = avg_return, label = "Average Daily Return", linewidth=1, color='r')

from matplotlib.ticker import FuncFormatter

def returns(x, pos):
    return '{:1.2f}%'.format(x*100)

returns(0.00134,1)

formatter = FuncFormatter(returns)
ax.yaxis.set_major_formatter(formatter)
ax.legend().set_visible(False)

plt.style.use("tableau-colorblind10")
plt.show()

