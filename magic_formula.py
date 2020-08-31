# -*- coding: utf-8 -*-
"""
Created on Wed Aug 19 10:51:08 2020

@author: 97vin
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd

tickers = ["AXP","AAPL","BA","CAT","CVX","CSCO","DIS","DOW", "XOM",
           "HD","IBM","INTC","JNJ","KO","MCD","MMM","MRK","MSFT",
           "NKE","PFE","PG","TRV","UTX","UNH","VZ","V","WMT","WBA"]



financial_dir = {}

for i in range(len(tickers)):
    lst = []
    tmp_lst = []
    
    # income statement
    print("income statement for", tickers[i])
    url = "https://finance.yahoo.com/quote/%s/financials?p=%s" % (tickers[i],tickers[i])
    page = requests.get(url)
    page_contents = page.content
    soup = BeautifulSoup(page_contents, "html.parser")
    tabl = soup.find_all("div", class_ = "D(tbr)")

        
    for t in tabl: #every table row
        row = t.find_all("div", {"class":"D(tbc)"})
        for item in row: #every row cell
            tmp_lst.append(item.text)
        lst.append(tmp_lst[:2])
        tmp_lst=[]
        
    
    #balance sheet
    print("balance sheet for", tickers[i])
    url = "https://finance.yahoo.com/quote/%s/balance-sheet?p=%s" % (tickers[i],tickers[i])
    page = requests.get(url)
    page_contents = page.content
    soup = BeautifulSoup(page_contents, "html.parser")
    tabl = soup.find_all("div", class_ = "D(tbr)")

        
    for t in tabl: #every table row
        row = t.find_all("div", {"class":"D(tbc)"})
        for item in row: #every row cell
            tmp_lst.append(item.text)
        lst.append(tmp_lst[:2])
        tmp_lst=[]
    
    #cashflow statement
    print("cashflow statement for", tickers[i])
    url = "https://finance.yahoo.com/quote/%s/cash-flow?p=%s" % (tickers[i],tickers[i])
    page = requests.get(url)
    page_contents = page.content
    soup = BeautifulSoup(page_contents, "html.parser")
    tabl = soup.find_all("div", class_ = "D(tbr)")
    
        
    for t in tabl: #every table row
        row = t.find_all("div", {"class":"D(tbc)"})
        for item in row: #every row cell
            tmp_lst.append(item.text)
        lst.append(tmp_lst[:2])
        tmp_lst=[]
    
    #key statistics
    print("key statistics for", tickers[i])
    url = "https://finance.yahoo.com/quote/%s/key-statistics?p=%s" % (tickers[i],tickers[i])
    page = requests.get(url)
    page_contents = page.content
    soup = BeautifulSoup(page_contents, "html.parser")
    tabl = soup.find_all("table", class_ = "D(itb)")
    
        
    for t in tabl: #every table row
        row = t.find_all("tr")
        for item in row: #every row cell
            tmp_lst.append(item.text)
        lst.append(tmp_lst[:2])
        tmp_lst=[]
    


    financial_dir[tickers[i]] = pd.DataFrame(lst[:-1])
    financial_dir[tickers[i]].dropna(axis=0, inplace = True)
    financial_dir[tickers[i]].columns = ["Breakdown", tickers[i]]
    financial_dir[tickers[i]].set_index("Breakdown",inplace =True)
    page.close()
    

combined_financials = pd.DataFrame(financial_dir, index=["breakdown"])

## required sheet data
stats = ["EBITDA",
         "Depreciation & amortisation",
         "Market cap (intra-day)",
         "Net income available to common shareholders",
         "Net cash provided by operating activities",
         "Capital expenditure",
         "Total current assets",
         "Total current liabilities",
         "Net property, plant and equipment",
         "Total stockholders' equity",
         "Long-term debt",
         "Forward annual dividend yield"] # change as required
