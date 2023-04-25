import sys
from datetime import datetime
import json
import csv
import os
import requests
import time
import pandas as pd
import argparse
import timeit
import urllib3
import numpy as np 
import collections
import matplotlib as plt
from easydict import EasyDict

def default_settings(): 
    ##Setting crypto market & crypto currency after run

    setting = EasyDict({
        'market' : str(input("select market :" )),
        'currency' : str(input("select currency: "))
    })

    #validation
    while (setting.market not in market_list) or (setting.currency not in currency_list):

        if setting.market not in market_list:
            print(market_list)
            print("Unavailable market. Please try other market above")
            setting.market = input("select market: " )

        if setting.currency not in currency_list:
            print(currency_list)
            print("Unavailable currency. Please try other currency above")
            setting.currency = input("select currency: " )

    return setting

def write_csv(data, timestamp):
    date = timestamp.strftime('%Y-%m-%d')

    #File name: Date_market_orderbook.csv
    csv_directory = "./" + date + "_" + market + "_orderbook.csv"

    #Save header when file doesn't exists
    should_write_header = os.path.exists(csv_directory)

    if should_write_header == False:
        data.to_csv(csv_directory, index=False, header=True, mode = 'a')
    else:
        data.to_csv(csv_directory, index=False, header=False, mode = 'a')

def pull_csv_orderbook():

    timestamp = datetime.now()
    time_interval = 0

    while(1):
        # setting pull time interval
        time_interval = datetime.now() - timestamp
        if (time_interval.total_seconds() < 5):
            continue

        timestamp = datetime.now()

        response = requests.get(url_dictionary[market])

        orderbook = response.json()
        
        data = orderbook['data']
        
        ##bid = buy
        bids = (pd.DataFrame(data['bids'])).apply(pd.to_numeric, errors='ignore')
        bids.sort_values('price', ascending=False, inplace=True) ##ascending
        bids = bids.reset_index(); del bids['index']

        ##aks = sell
        asks = (pd.DataFrame(data['asks'])).apply(pd.to_numeric, errors='ignore')
        asks.sort_values('price', ascending=True, inplace=True) ##descending
        asks = asks.reset_index(); del asks['index']

        #rearranged orderbook
        new_orderbook = pd.concat([bids, asks])
        new_orderbook['quantity'] = new_orderbook['quantity'].round(decimals=4)
        new_orderbook['timestamp'] = timestamp

        """
        new_orderbook format:
        Bid 1 | Lowest price      |   quantity, timestamp
        Bid 2 | 2nd lowest price  |   quantity, timestamp
         ...  |        ...        |           ...
        Bid n | Highest price     |   quantity, timestamp
        Ask 1 | Highest price     |   quantity, timestamp
        Ask 2 | 2nd highest price |   quantity, timestamp
         ...  |        ...        |           ...
        Ask n |Lowest price       |  quantity, timestamp
        """

        #print(new_orderbook)

        write_csv(new_orderbook, timestamp)



market_list = ['Bithumb', 'Upbit' ]
currency_list = ['BTC', 'ETH', 'USDT']

def main():

    global market
    global currency 
    global url_dictionary

    initial_setting = default_settings()
    market = initial_setting["market"]
    currency = initial_setting["currency"]
    print(market)
    print(currency)

    url_dictionary = {'Bithumb':'https://api.bithumb.com/public/orderbook/%s_KRW/?count=10' %currency, 
                'Upbit':"'https://api.upbit.com/v1/orderbook?markets=KRW-%s' % currency"}

    pull_csv_orderbook()

    
main()
