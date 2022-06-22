#%% Strategy - Mean Reversion of EWA and EWC (Australian and Canadian Equity Market ETFs)
#   Shows cointegration of combined portfolio using CADF and Johansen tests.

""" This is an implementation of examples 2.6-2.8 of Ernest chan's
book ALGORITHMIC TRADING - Winning Strategies and Their Rationale
"""

#pip install yfinance
from functions import *
import datetime
import numpy as np
import pandas as pd
from numpy.matlib import repmat
#https://docs.scipy.org/doc/numpy/reference/generated/numpy.matlib.repmat.html
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
#https://pandas.pydata.org/pandas-docs/version/0.23.0/generated/pandas.Timedelta.html
import yfinance as yf
import statsmodels.api as sm
import statsmodels.tsa.stattools as ts
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.vector_ar.vecm import coint_johansen
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()

#%% Download Data and Plot

if __name__ == "__main__":


    start = datetime.datetime(2005, 1, 1)
    end = datetime.datetime(2020, 2, 15)
    
    ewa = yf.download("EWA", start, end)
    ewc = yf.download("EWC", start, end)
    ige = yf.download("IGE", start, end)
    
    df = pd.DataFrame(index=ewa.index)
    df["EWA"] = ewa["Adj Close"]
    df["EWC"] = ewc["Adj Close"]
    df["IGE"] = ige["Adj Close"]
    
    # Plot the two time series
    print(color.BOLD + "\n Dates: Jan-2005 to Dec-2012" + color.END)
    start = datetime.datetime(2005, 1, 1)
    end = datetime.datetime(2012, 12, 31)
    plot_price_series(df, "EWA", "EWC", start, end)
    
    print(color.BOLD + "\n Dates: Jan-2013 to Feb-2020" + color.END)
    start = datetime.datetime(2013, 1, 1)
    end = datetime.datetime(2020, 2, 15)
    plot_price_series(df, "EWA", "EWC", start, end)
    
    # Display a scatter plot of the two time series
    start = datetime.datetime(2013, 1, 1)
    end = datetime.datetime(2020, 2, 15)
    plot_scatter_series(df, "EWA", "EWC")