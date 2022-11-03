import tweepy
import random
import time
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import schedule
#holds my keys
import twitter_creds

#auth
api_key = twitter_creds.key
api_key_secret = twitter_creds.key_sec
access_token = twitter_creds.token
access_token_secret = twitter_creds.token_sec


auth = tweepy.OAuth1UserHandler(
   api_key, api_key_secret, access_token, access_token_secret
)

api = tweepy.API(auth)


# First we need to retrieve an updated list of the tickers we would like to track. For now, we will use the S&P100.
#The S&P500 cannot be used due to request rate limits on the yfinance API
#must be refreshed in event of rebalance.
#tickers = pd.read_html('https://en.wikipedia.org/wiki/S%26P_100', attrs = {'id': 'constituents'})[0].drop(["Name", "Sector"], axis = 1)['Symbol'].values.tolist()

# Shortened list for testing
tickers = ['AAPL', 'GOOG', 'AMZN', 'JPM']

#The tickers and their corresponding prices will be stored here
quotes_open = {}
quotes_last = {}

all_stocks_df = pd.DataFrame()


#Getting open prices for each ticker
def update_at_open():

    for i in range(len(tickers)): 
        current_ticker = yf.Ticker(str(tickers[i]))
        #info = current_ticker.history(period = '1d')
        open_price = current_ticker.info['open']
        quotes_open[tickers[i]] = open_price
        print(tickers[i] + ' Opened at ' + str(open_price))
        

def update_intraday():
    time.sleep(1)
    for ticker in tickers:
        current_ticker = yf.Ticker(str(ticker))
        current_price = current_ticker.info['regularMarketPrice']
        #update to make 'current_price' the 'last_price' for next interation
        quotes_last[ticker] = current_price
        print(ticker + ' is trading at ' + str(current_price))
        
        #Calculating price change
        delta_price = round(((quotes_last[ticker] - quotes_open[ticker]) / quotes_open[ticker]) * 100, 2)
        

        monthly_hist = current_ticker.history(period = '30d')
        monthly_hist.reset_index(inplace=True)
        monthly_closing_prices = list(monthly_hist["Close"])
        all_stocks_df["Date"] = monthly_hist["Date"]
        all_stocks_df[ticker] = monthly_closing_prices
        #all_stocks_df.columns = [monthly_hist["Date"]]
    
        fig, ax = plt.subplots()
        ax.plot(all_stocks_df["Date"],all_stocks_df[ticker])
        plt.title("$" + ticker + " | @tedbot97")
        plt.xlabel('Date')
        plt.ylabel('Price')
        #plt.figure(figsize=(20,5))
        plt.setp(ax.get_xticklabels(), rotation=30, horizontalalignment='right')

        plt.savefig(ticker + '.png', bbox_inches='tight')
        #plt.show()

        if delta_price < -2:
            api.update_status_with_media('#' + ticker + ' is down ' + str(abs(delta_price)) + '% Today!', ticker + '.png')
            


        if delta_price > 2:
            api.update_status_with_media('#' + ticker + ' is up ' + str(abs(delta_price)) + '% Today!', ticker + '.png')
        

schedule.every().day.at("10:02").do(update_at_open)
schedule.every().day.at("11:00").do(update_intraday)
schedule.every().day.at("13:00").do(update_intraday)









