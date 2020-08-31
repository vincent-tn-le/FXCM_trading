# -*- coding: utf-8 -*-
"""
Created on Mon Aug 10 10:44:36 2020

@author: 97vin
"""

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

df = pd.read_excel("https://github.com/chris1610/pbpython/blob/master/data/sample-salesv3.xlsx?raw=true")
df.head()

top_10 = df.groupby("name").agg({'ext price':'sum', 'quantity':'count'}).sort_values(by='ext price', ascending=False)[:10].reset_index()
top_10.columns = ["Name", "Sales", "Purchases"]

# function for formatting USD in 100K's
def currency(x,pos):
    # millions
    if x >= 1000000:
        return '${:1.1f}M'.format(x*1e-6) # :1 is format idk, .1 is first decimal place number
    # thousands
    return '${:1.0f}K'.format(x*1e-3)

# have to run this everytime before plt.show()
fig, ax = plt.subplots()
ax.barh(list(top_10["Name"]), list(top_10["Sales"]))
# top_10.plot(kind="barh", y="Sales", x="Name", ax=ax)
ax.set_xlim([-10000, 140000])
ax.set(title="2014 Revenue", xlabel="Total Revenue", ylabel="Customer")
ax.legend().set_visible(False)

# adding a vertical line
avg = top_10["Sales"].mean()
ax.axvline(x=avg, color = 'b', label = "average", linestyle = "--", linewidth=1)

# marking new customers
for cust in [3,5,8]:
    ax.text(115000, cust, "New Customer")

# formatting x-axis
formatter = FuncFormatter(currency)
ax.xaxis.set_major_formatter(formatter)

plt.show()


## Multiple chart example
fig, (ax0,ax1) = plt.subplots(nrows=1, ncols=2, sharey=True, figsize = (7,4))
ax0.barh(list(top_10["Name"]), list(top_10["Sales"]))
ax1.barh(list(top_10["Name"]), list(top_10["Sales"]))

ax0.set_xlim([-10000, 140000])
ax0.set(title="Revenue", xlabel = "Total Revenue", ylabel="Customer")
ax0.legend().set_visible(False)

sales_avg = top_10["Sales"].mean()
ax0.axvline(x=sales_avg, color = 'b', label="Sales Average", linestyle = "--", linewidth=1)

ax1.set_xlim([-10, 100])
ax1.set(title="Units", xlabel = "Total Units")
ax1.legend().set_visible(False)

units_avg = top_10["Purchases"].mean()
ax1.axvline(x=units_avg, color = 'b', label="Sales Average", linestyle = "--", linewidth=1)

fig.suptitle("2014 Sales Analysis", fontsize=14, fontweight="bold")

plt.show()
