# -*- coding: utf-8 -*-
"""
Created on Fri Aug 21 09:59:29 2020

@author: 97vin
"""

import pandas as pd
import yahoo_fin.stock_info as si
import numpy as np

tickers = ["AAPL","CAT","CVX","CSCO","DOW","XOM"]#,
          # "HD","IBM","INTC","JNJ","KO","MCD","MMM","MRK","MSFT",
          # "NKE","PFE","PG","TRV","UTX","UNH","VZ","V","WMT","WBA"]

financial_dir = {}
financial_dir_py = {}
financial_dir_py2 = {}

def stringToNum(x):
    last = x[-1].lower()
    if last == "t":
        return float(x[:-1]) * 1000000000000
    elif last == "b":
        return float(x[:-1]) * 1000000000
    elif last == "m":
        return float(x[:-1]) * 1000000
    else: # when it's a percentage
        try:
            return float(x.split(" (")[1].strip("%)"))/100
        except:
            return np.nan
   
stats = ["Net income available to common shareholders",
         "Total assets",
         "Net cash provided by operating activities",
         "Long-term debt",
         "Other long-term liabilities",
         "Total current assets",
         "Total current liabilities",
         "Common stock",
         "Total revenue",
         "Gross profit"]        
   
for ticker in tickers:
    temp_dict = {}
    temp_dict2 = {}
    temp_dict3 = {}
    bal = si.get_balance_sheet(ticker)
    cf = si.get_cash_flow(ticker)
    income = si.get_income_statement(ticker)
    print("getting financial data for: ", ticker)
    try:
        temp_dict["Net income available to common shareholders"] = income.loc["netIncomeApplicableToCommonShares",:][0]
        temp_dict2["Net income available to common shareholders"] = income.loc["netIncomeApplicableToCommonShares",:][1]
        temp_dict3["Net income available to common shareholders"] = income.loc["netIncomeApplicableToCommonShares",:][2]
    except:
        temp_dict["Net income available to common shareholders"] = np.nan
        temp_dict2["Net income available to common shareholders"] = np.nan
        temp_dict3["Net income available to common shareholders"] = np.nan
    
    try:
        temp_dict["Total Current Assets"] = bal.loc["totalCurrentAssets",:][0]
        temp_dict2["Total Current Assets"] = bal.loc["totalCurrentAssets",:][1]
        temp_dict3["Total Current Assets"] = bal.loc["totalCurrentAssets",:][2]
    except:
        temp_dict["Total Current Assets"] = np.nan
        temp_dict2["Total Current Assets"] = np.nan
        temp_dict3["Total Current Assets"] = np.nan
    try:
        temp_dict["Net cash from operating activities"] = cf.loc["totalCashFromOperatingActivities",:][0]
        temp_dict2["Net cash from operating activities"] = cf.loc["totalCashFromOperatingActivities",:][1]
        temp_dict3["Net cash from operating activities"] = cf.loc["totalCashFromOperatingActivities",:][2]
    except:
        temp_dict["Net cash from operating activities"] = np.nan
        temp_dict2["Net cash from operating activities"] = np.nan
        temp_dict3["Net cash from operating activities"] = np.nan
    try:
        temp_dict["Long-term Debt"] = bal.loc["longTermDebt",:][0]
        temp_dict2["Long-term Debt"] = bal.loc["longTermDebt",:][1]
        temp_dict3["Long-term Debt"] = bal.loc["longTermDebt",:][2]
    except:
        temp_dict["Long-term Debt"] = np.nan
        temp_dict2["Long-term Debt"] = np.nan
        temp_dict3["Long-term Debt"] = np.nan
    try:
        temp_dict["Other Liabilities"] = bal.loc["otherLiab",:][0]
        temp_dict2["Other Liabilities"] = bal.loc["otherLiab",:][1]
        temp_dict3["Other Liabilities"] = bal.loc["otherLiab",:][2]
    except:
        temp_dict["Other Liabilities"] = np.nan
        temp_dict2["Other Liabilities"] = np.nan
        temp_dict3["Other Liabilities"] = np.nan
    try:
        temp_dict["Total Current Assets"] = bal.loc["totalCurrentAssets",:][0]
        temp_dict2["Total Current Assets"] = bal.loc["totalCurrentAssets",:][1]
        temp_dict3["Total Current Assets"] = bal.loc["totalCurrentAssets",:][2]
    except:
        temp_dict["Total Current Assets"] = np.nan
        temp_dict2["Total Current Assets"] = np.nan
        temp_dict3["Total Current Assets"] = np.nan
    try:
        temp_dict["Total Current Liabilities"] = bal.loc["totalCurrentLiabilities",:][0]
        temp_dict2["Total Current Liabilities"] = bal.loc["totalCurrentLiabilities",:][1]
        temp_dict3["Total Current Liabilities"] = bal.loc["totalCurrentLiabilities",:][2]
    except:
        temp_dict["Total Current Liabilities"] = np.nan
        temp_dict2["Total Current Liabilities"] = np.nan
        temp_dict3["Total Current Liabilities"] = np.nan
    try:
        temp_dict["Common Stock"] = bal.loc["commonStock",:][0]
        temp_dict2["Common Stock"] = bal.loc["commonStock",:][1]
        temp_dict3["Common Stock"] = bal.loc["commonStock",:][2]
    except:
        temp_dict["Common Stock"] = np.nan
        temp_dict2["Common Stock"] = np.nan
        temp_dict3["Common Stock"] = np.nan
    try:
        temp_dict["Total Revenue"] = income.loc["totalRevenue",:][0]
        temp_dict2["Total Revenue"] = income.loc["totalRevenue",:][1]
        temp_dict3["Total Revenue"] = income.loc["totalRevenue",:][2]
    except:
        temp_dict["Total Revenue"] = np.nan
        temp_dict2["Total Revenue"] = np.nan
        temp_dict3["Total Revenue"] = np.nan
    try:
        temp_dict["Gross Profit"] = income.loc["grossProfit",:][0]
        temp_dict2["Gross Profit"] = income.loc["grossProfit",:][1]
        temp_dict3["Gross Profit"] = income.loc["grossProfit",:][2]
    except:
        temp_dict["Gross Profit"] = np.nan
        temp_dict2["Gross Profit"] = np.nan
        temp_dict3["Gross Profit"] = np.nan
    financial_dir[ticker] = temp_dict
    financial_dir_py[ticker] = temp_dict2
    financial_dir_py2[ticker] = temp_dict3
        
        

# f score for each ticker
f_score = {}
for ticker in tickers:
    print("calculating F-score for: ", ticker)
    ROA_fs = int(financial_dir[ticker]["Net income available to common shareholders"]/(financial_dir_py[ticker]["Total Current Assets"] + financial_dir[ticker]["Total Current Assets"]) >0)
    CFO_fs = int(financial_dir[ticker]["Net cash from operating activities"]>0)
    ROA_D_fs = int(financial_dir[ticker]["Net income available to common shareholders"]/(financial_dir_py[ticker]["Total Current Assets"] + financial_dir[ticker]["Total Current Assets"]) > financial_dir_py[ticker]["Net income available to common shareholders"]/(financial_dir_py[ticker]["Total Current Assets"] + financial_dir_py2[ticker]["Total Current Assets"]))
    CFO_ROA_fs = int(financial_dir[ticker]["Net cash from operating activities"]/financial_dir[ticker]["Total Current Assets"] > financial_dir[ticker]["Net income available to common shareholders"]/(financial_dir_py[ticker]["Total Current Assets"] + financial_dir[ticker]["Total Current Assets"]))
    LTD_fs = int((financial_dir[ticker]["Long-term Debt"] + financial_dir[ticker]["Other Liabilities"]) < (financial_dir_py[ticker]["Long-term Debt"] + financial_dir_py[ticker]["Other Liabilities"]))
    CR_fs = int((financial_dir[ticker]["Total Current Assets"]/financial_dir[ticker]["Total Current Liabilities"]) > (financial_dir_py[ticker]["Total Current Assets"]/financial_dir_py[ticker]["Total Current Liabilities"]))
    Dilution_fs = int(financial_dir[ticker]["Common Stock"] <= financial_dir_py[ticker]["Common Stock"])
    GM_fs = int((financial_dir[ticker]["Gross Profit"]/financial_dir[ticker]["Total Revenue"]) > (financial_dir_py[ticker]["Gross Profit"]/financial_dir_py[ticker]["Total Revenue"]))
    ATO_fs = int(financial_dir[ticker]["Total Revenue"]/((financial_dir[ticker]["Total Current Assets"] + financial_dir_py[ticker]["Total Current Assets"])/2) > financial_dir_py[ticker]["Total Revenue"]/((financial_dir_py[ticker]["Total Current Assets"] + financial_dir_py2[ticker]["Total Current Assets"])/2))
    score = sum([ROA_fs, CFO_fs, ROA_D_fs, CFO_ROA_fs, LTD_fs, CR_fs, Dilution_fs, GM_fs, ATO_fs])
    f_score[ticker] = score
        
f_score
    
    
    
    
    
    
    
    
    