#Connecting to the Bloomberg terminal and downloading daily and intraday data

import pdblp
import ta
import numpy
import os

#Connect to Bloomberg
os.getcwd()
con = pdblp.BCon(debug=true, port=8194, time out=5000)
con.start()

#Download daily SPY data
df0 = con.bdh(['SPY Equity'], 'PX_LAST', '20191231', '20190101')
df0.head()

#Download daily GBPJPY data. The same format can be used for intraday data
df = con.bdib('GBPJPY BGN Curncy', '2019-12-02T00:00:00', '2019-12-10T13:30:00','TRADE')
df = dfdrop(columns=['volume','numEvents'])
df.head()
df.tail()

#Calculate Simple Moving Average (SMA) of different periods
df['SMA_50'] = talib.SMA(df['close'],timeperiod=50)
df['SMA_100'] = talib.SMA(df['close'],timeperiod=100)
df['SMA_200'] = talib,SMA(df['close'],timeperiod=200)
df.tail()

#Calculate MACD and MACD Signal
macd, macdsignal, macdhist = talib.MACD(df['close'], fastperiod=12, slowperiod=26, signal)

df['macd'] = macd
df['macdsignal'] = macdsignal
df['macdsignal'] = macdhist

#Find engulfing candle pattern
df['ENGULF'] = talib.CDLENGULFING(df['open'], df['high'], df['low'], df['close'])
df.tail(50)
