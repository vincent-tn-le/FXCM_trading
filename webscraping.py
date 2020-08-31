# -*- coding: utf-8 -*-
"""
Created on Sun Aug  9 12:23:12 2020

@author: 97vin
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd

# Webscraping income statements

url = "https://finance.yahoo.com/quote/TWTR/financials?p=TWTR"
page = requests.get(url) # establishing the connection
page_contents = page.content
soup = BeautifulSoup(page_contents, "html.parser")
tabl = soup.find_all("div", class_ = "D(tbr)") #each row that comprises the table
type(tabl)

lst = []
tmp_lst = []

for t in tabl:
    val = t.find_all("div", {"class":'D(tbc)'}) 
    for line in val: # each value
        tmp_lst.append(line.text)
    lst.append(tmp_lst)
    tmp_lst=[]
        
lst
df = pd.DataFrame(lst)


# Attempt with multiple ticker names (assuming that the HTML is general)
tickers = ["AAPL", "MSFT", "GOOGL", "CSCO"]
financials = {}

for i in range(len(tickers)):
    
    lst = []
    tmp_lst = []
    
    # income statement
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
    


    financials[tickers[i]] = pd.DataFrame(lst[:-1])
    financials[tickers[i]].dropna(axis=0, inplace = True)
    financials[tickers[i]].columns = ["Breakdown", tickers[i]]
    financials[tickers[i]].set_index("Breakdown",inplace =True)
    page.close()
    
combined_financials = pd.concat(financials, axis=1)
combined_financials.fillna(0)
