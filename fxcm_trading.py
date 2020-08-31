# -*- coding: utf-8 -*-
"""
Created on Mon Aug 24 10:04:27 2020

@author: 97vin
"""

# import necessary libraries
import fxcmpy
import numpy as np
from stocktrends import Renko
import statsmodels.api as sm
import time
import copy


# API connection
token = "bfd5aad5bc1e7213353a84540235382d94c56bff"
con = fxcmpy.fxcmpy(access_token=token, log_level = "error", server = "demo")

# strategy parameters
pairs = ['EUR/USD', 'GBP/USD', 'USD/CHF', 'AUD/USD', 'USD/CAD'] # currency pairs
pos_size = 10 # max capital allocated/position size

# functions for determining signals
def MACD(df, a=12, b=26, c=9):
    temp = df.copy()
    temp["MA_fast"] = temp["Close"].ewm(span=a, min_periods=a).mean()
    temp["MA_slow"] = temp["Close"].ewm(span=b, min_periods=b).mean()
    temp["MACD"] = temp["MA_fast"] - temp["MA_slow"]
    temp["Signal"] = temp["MACD"].ewm(span=c, min_periods=c).mean()
    temp.dropna(axis=0, inplace=True)
    return (temp["MACD"], temp["Signal"])

def ATR(DF,n=20):
    temp = DF.copy()
    temp["H-L"] = abs(temp["High"] - temp["Low"]) 
    temp["H-PC"] = abs(temp["High"] - temp["Close"].shift(1)) # high - previous day close
    temp["L-PC"] = abs(temp["Low"] - temp["Close"].shift(1))
    temp["TR"] = temp[["H-L", "H-PC", "L-PC"]].max(axis=1, skipna = False)
    temp["ATR"] = temp["TR"].rolling(n).mean()
    
    return_val = temp.drop(["H-L","H-PC","L-PC"], axis=1)
    return return_val

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

def renko_DF(DF):
    df = DF.copy()
    df.reset_index(inplace=True)
    df = df.iloc[:,[0,1,2,3,4,5]]
    df.columns = ["date", "low", "high", "open", "close", "volume"]

    df2 = Renko(df)
    df2.brick_size = max(0.5, round(ATR(DF,120)["ATR"][-1],0))
    renko_df = df2.get_ohlc_data()
    renko_df["bar_num"] = np.where(renko_df["uptrend"] == True, 1, np.where(renko_df["uptrend"] == False, -1, 0))
    for i in range(1, len(renko_df["bar_num"])):
        if renko_df["bar_num"][i]>0 and renko_df["bar_num"][i-1] >0:
            renko_df["bar_num"].iloc[i] += renko_df["bar_num"][i-1]
        elif renko_df["bar_num"][i]<0 and renko_df["bar_num"][i-1] <0:
            renko_df["bar_num"].iloc[i] += renko_df["bar_num"][i-1]
    renko_df.drop_duplicates(subset="date", keep="last", inplace=True)
    return renko_df

def renko_merge(DF):
    df = copy.deepcopy(DF)
    renko = renko_DF(df)
#    df["date"] = df.index
    merged_df = df.merge(renko.loc[:,["date","bar_num"]],how="outer",on="date")
    merged_df["bar_num"].fillna(method="ffill", inplace=True)
    merged_df["MACD"] = MACD(merged_df)[0]
    merged_df["Signal"] = MACD(merged_df)[1]
    merged_df["MACD Slope"] = slope(merged_df["MACD"])
    merged_df["Signal Slope"] = slope(merged_df["Signal"])
    return merged_df


## Determining Renko Chart + MACD signal based off of data
def trade_signal(MERGED_DF, l_s):
    signal = ""
    df = copy.deepcopy(MERGED_DF)
    if l_s == "":
        if df["bar_num"].tolist()[-1] >= 2 and df["MACD"].tolist()[-1] > df["Signal"].tolist()[-1] and df["MACD Slope"].tolist()[-1] > df["Signal Slope"].tolist()[-1]:
            signal = "Buy"
        elif df["bar_num"].tolist()[-1] <= -2 and df["MACD"].tolist()[-1] < df["Signal"].tolist()[-1] and df["MACD Slope"].tolist()[-1] < df["Signal Slope"].tolist()[-1]:
            signal = "Sell"
    
    elif l_s == "long":
        if df["bar_num"].tolist()[-1] <= -2 and df["MACD"].tolist()[-1] < df["Signal"].tolist()[-1] and df["MACD Slope"].tolist()[-1] < df["Signal Slope"].tolist()[-1]:
            signal = "Close_Sell"
        elif df["MACD"].tolist()[-1] < df["Signal"].tolist()[-1] and df["MACD Slope"].tolist()[-1] < df["Signal Slope"].tolist()[-1]:
            signal = "Close"
    
    elif l_s == "short":
        if df["bar_num"].tolist()[-1] >= 2 and df["MACD"].tolist()[-1] > df["Signal"].tolist()[-1] and df["MACD Slope"].tolist()[-1] > df["Signal Slope"].tolist()[-1]:
            signal = "Close_Buy"
        elif df["MACD"].tolist()[-1] > df["Signal"].tolist()[-1] and df["MACD Slope"].tolist()[-1] > df["Signal Slope"].tolist()[-1]:
            signal = "Close"
    return signal
    

## Trading function
def main():
    try:
        open_pos = con.get_open_positions()
        for currency in pairs:
            long_short = ""
            if len(open_pos) > 0:
                open_pos_cur = open_pos[open_pos["currency"] == currency]
                if len(open_pos_cur) > 0:
                    if open_pos_cur["isBuy"].tolist()[0] == True:
                        long_short = "long"
                    elif open_pos_cur["isBuy"].tolist()[0] == False:
                        long_short = "short"
            data = con.get_candles(currency, period="m5", number = 250)
            ohlc = data.iloc[:,[0,1,2,3,8]]
            ohlc.columns = ["Open", "Close", "High", "Low", "Volume"]
            signal = trade_signal(renko_merge(ohlc), long_short)
            
            if signal == "Buy":
                con.open_trade(symbol=currency, is_buy = True, is_in_pips = True, amount = pos_size,
                               time_in_force = "GTC", order_type = "AtMarket")
                print("New long position initiated for ", currency)
            elif signal == "Sell":
                con.open_trade(symbol=currency, is_buy = False, is_in_pips = True, amount = pos_size,
                               time_in_force = "GTC", order_type = "AtMarket")
                print("New short position initiated for ", currency)
            elif signal == "Close":
                con.close_all_for_symbol(currency)
                print("All positions closed for ", currency)
            elif signal == "Close_Buy":
                con.close_all_for_symbol(currency)
                print("Existing short positions closed for ", currency)
                con.open_trade(symbol=currency, is_buy=True, is_in_pips = True, amount = pos_size, 
                               time_in_force = "GTC", order_type = "AtMarket")
                print("New long position initiated for ", currency)
            elif signal == "Close_Sell":
                con.close_all_for_symbol(currency)
                print("Existing long positions closed for ", currency)
                con.open_trade(symbol=currency, is_buy=False, is_in_pips=True, amount=pos_size,
                               time_in_force = "GTC", order_type="AtMarket")
                print("New short position intitated for ", currency)
    except:
        print("Error encountered for ", currency, "skipping this iteration")
        
    
## Continual execution
start_time = time.time()
end_time = time.time() + 60*60*24 # 24 hour from when it starts

while time.time() <= end_time:
    try:
        print("Passthrough at ", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())))
        main()
        time.sleep(60 - ((time.time() - start_time) % 60)) # running main() every minute
    except KeyboardInterrupt:
        print("\n\nKeyboard exception received. Exiting.")
        exit()
        
# CLosing connection to FXCM api
for currency in pairs:
    print("Closing all positions for ", currency)
    con.close_all_for_symbol(currency)
con.close()