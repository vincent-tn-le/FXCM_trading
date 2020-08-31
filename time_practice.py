# -*- coding: utf-8 -*-
"""
Created on Fri Aug 21 11:18:51 2020

@author: 97vin
"""

import time
import numpy as np

def fibonacci(n):
    if n <= 1:
        return n
    else:
        return(fibonacci(n-1) + fibonacci(n-2))
    
def main():
    num = np.random.randint(1,25)
    print("%dth fibonacci number is: %d"%(num,fibonacci(num)))

starttime = time.time()
timeout = time.time() + 60*2

while time.time() <= timeout:
    try:
        main()
        time.sleep(5 - ((time.time() - starttime) % 5.0))
    except KeyboardInterrupt:
        print("\n\nKeyboard exception received. Exiting.")
        exit()