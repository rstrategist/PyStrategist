import numpy as np
from numpy.matlib import repmat
import pandas as pd
from pandas_datareader import data
#from datetime import datetime, timedelta, date
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import statsmodels.api as sm
#import statsmodels.formula.api as smf
import statsmodels.tsa.stattools as ts
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.vector_ar.vecm import coint_johansen
import yfinance as yf
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()


# Paths for data
def data_path(loc):
    if loc == 'PC':
        root_path = 'C:/MarketData/'
    elif loc == 'MAC':
        root_path = '/Users/rashidrasul/MarketData/'
    return root_path

# Get yahoo data
def get_yahoo_data(tickers, start_date, end_date):
    panel_data = data.DataReader(tickers , 'yahoo', start_date, end_date)
    df = panel_data.loc[:, ('Adj Close', slice(None))]
    df.columns = df.columns.droplevel()
    df.index = pd.to_datetime(df.index,  format = '%Y%m%d').date # remove HH:MM:SS
    
    return df

# Plot two series on a chart and label
def plot_price_series(df, ts1, ts2, start_date, end_date):
    months = mdates.YearLocator()  # every month use .MonthLocator
    fig, ax = plt.subplots()
    ax.plot(df.index, df[ts1], label=ts1, color='b')
    ax.plot(df.index, df[ts2], label=ts2, color='g')
    ax.xaxis.set_major_locator(months)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y')) # use %b %Y
    ax.set_xlim(start_date, end_date)
    ax.grid(True)
    fig.autofmt_xdate()
    plt.xlabel('Month/Year')
    plt.ylabel('Price ($)')
    plt.title('%s and %s Daily Prices' % (ts1, ts2))
    plt.legend()
    plt.show()

# Plot simple two series on a chart and label
def plot_simple(df, ts1, ts2, start_date, end_date):
    plt.figure(figsize = (17, 6))
    plt.plot(df[ts1], label = ts1)
    plt.plot(df[ts2], label = ts2)
    plt.legend()
    plt.show()

# plot a scatter plot of multiple price series
def plot_scatter_series(df, ts1, ts2):
    plt.xlabel('%s Price ($)' % ts1)
    plt.ylabel('%s Price ($)' % ts2)
    plt.title(f'{ts1} and {ts2} Price Scatterplot')
    plt.scatter(df[ts1], df[ts2])
    plt.show()

# plot the residual values from the fitted linear model of the two price series
def plot_residuals(df, start_date, end_date):
    months = mdates.YearLocator()  # every month use .MonthLocator
    fig, ax = plt.subplots()
    ax.plot(df.index, df["RES"], label="Residuals", color="b")
    ax.xaxis.set_major_locator(months)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax.set_xlim(start_date, end_date)
    #ax.set_ylim([4,12])
    ax.grid(True)
    fig.autofmt_xdate()

    plt.xlabel('Year')
    plt.ylabel('Price ($)')
    plt.title('Residual Plot')
    plt.legend()

    plt.plot(df["RES"])
    plt.show()

def summarise_johansen(result):
    # Present Johansen test results
    print ('--------------------------------------------------')
    print ('--> Trace Statistics')
    print ('variable statistic Crit-90% Crit-95%  Crit-99%')
    for i in range(len(result.lr1)):
        print ('r =', i, '\t', round(result.lr1[i], 4), result.cvt[i, 0], result.cvt[i, 1], result.cvt[i, 2])
    print ('--------------------------------------------------')
    print ('--> Eigen Statistics')
    print ('variable statistic Crit-90% Crit-95%  Crit-99%')
    for i in range(len(result.lr2)):
        print ('r =', i, '\t', round(result.lr2[i], 4), result.cvm[i, 0], result.cvm[i, 1], result.cvm[i, 2])
    print ('--------------------------------------------------')
    print ('eigenvalues:\n', result.eig)
    print ('--------------------------------------------------')
    print ('eigenvectors:\n', result.evec)
    print ('--------------------------------------------------')

    # The first eigenvector shows the strongest cointegration relationship 
    w = result.evec[:, 0]
    print('Best eigenvector is: {}.'.format(str(w)))

# Normal CDF
def normcdf(X):
    (a1,a2,a3,a4,a5) = (0.31938153, -0.356563782, 1.781477937, -1.821255978, 1.330274429)
    L = abs(X)
    K = 1.0 / (1.0 + 0.2316419 * L)
    w = 1.0 - 1.0 / sqrt(2*pi)*exp(-L*L/2.) * (a1*K + a2*K*K + a3*pow(K,3) + a4*pow(K,4) + a5*pow(K,5))
    if X < 0:
        w = 1.0-w
    return w

def vratio(a, lag = 2, cor = 'hom'):
    """ the implementation found in the blog Leinenbock  
    http://www.leinenbock.com/variance-ratio-test/
    """
    #t = (std((a[lag:]) - (a[1:-lag+1])))**2;
    #b = (std((a[2:]) - (a[1:-1]) ))**2;
 
    n = len(a)
    mu  = sum(a[1:n]-a[:n-1])/n;
    m=(n-lag+1)*(1-lag/n);
    #print( mu, m, lag)
    b=sum(square(a[1:n]-a[:n-1]-mu))/(n-1)
    t=sum(square(a[lag:n]-a[:n-lag]-lag*mu))/m
    vratio = t/(lag*b);
 
    la = float(lag)
     
    if cor == 'hom':
        varvrt=2*(2*la-1)*(la-1)/(3*la*n)
 
    elif cor == 'het':
        varvrt=0;
        sum2=sum(square(a[1:n]-a[:n-1]-mu));
        for j in range(lag-1):
            sum1a=square(a[j+1:n]-a[j:n-1]-mu);
            sum1b=square(a[1:n-j]-a[0:n-j-1]-mu)
            sum1=dot(sum1a,sum1b);
            delta=sum1/(sum2**2);
            varvrt=varvrt+((2*(la-j)/la)**2)*delta
 
    zscore = (vratio - 1) / sqrt(float(varvrt))
    pval = normcdf(zscore);
 
    return  vratio, zscore, pval
 
def hurst2(ts):
    """ the implementation found in the blog Leinenbock  
    http://www.leinenbock.com/calculation-of-the-hurst-exponent-to-test-for-trend-and-mean-reversion/
    """
    tau = []; lagvec = []
    #  Step through the different lags
    for lag in range(2,100):
        #  produce price difference with lag
        pp = subtract(ts[lag:],ts[:-lag])
        #  Write the different lags into a vector
        lagvec.append(lag)
        #  Calculate the variance of the differnce vector
        tau.append(sqrt(std(pp)))
 
    #  linear fit to double-log graph (gives power)
    m = polyfit(log10(lagvec),log10(tau),1)
    # calculate hurst
    hurst = m[0]*2.0
    # plot lag vs variance
    #plt.plot(lagvec,tau,'o')
    #plt.show()
 
    return hurst

def hurst(ts):
    """ the implementation on the blog http://www.quantstart.com
    http://www.quantstart.com/articles/Basics-of-Statistical-Mean-Reversion-Testing
    Returns the Hurst Exponent of the time series vector ts"""
    # Create the range of lag values
    lags = range(2, 100)
    # Calculate the array of the variances of the lagged differences
    tau = [sqrt(std(subtract(ts[lag:], ts[:-lag]))) for lag in lags]
    # Use a linear fit to estimate the Hurst Exponent
    poly = polyfit(log(lags), log(tau), 1)
    # Return the Hurst exponent from the polyfit output
    return poly[0]*2.0

""""def half_life(ts):  
    """ this function calculate the half life of mean reversion
    """
    # calculate the delta for each observation. 
    # delta = p(t) - p(t-1)
    delta_ts = diff(ts)
        # calculate the vector of lagged prices. lag = 1
    # stack up a vector of ones and transpose
    lag_ts = vstack([ts[1:], ones(len(ts[1:]))]).T
   
    # calculate the slope (beta) of the deltas vs the lagged values 
    beta = linalg.lstsq(lag_ts, delta_ts)
    
    # compute half life
    half_life = log(2) / beta[0]
    
    return half_life[0]
""""
def random_walk(seed=1000, mu = 0.0, sigma = 1, length=1000):
    """ this function creates a series of independent, identically distributed values
    with the form of a random walk. Where the best prediction of the next value is the present
    value plus some random variable with mean and variance finite 
    We distinguish two types of random walks: (1) random walk without drift (i.e., no constant
    or intercept term) and (2) random walk with drift (i.e., a constant term is present).  
    The random walk model is an example of what is known in the literature as a unit root process.
    RWM without drift: Yt = Yt−1 + ut
    RWM with drift: Yt = δ + Yt−1 + ut
    """
    
    ts = []
    for i in range(length):
        if i == 0:
            ts.append(seed)
        else:    
            ts.append(mu + ts[i-1] + random.gauss(0, sigma))

    return ts

def subset_df(data, start_date, end_date):
    return data.loc[start_date:end_date]


def cointegration_test(y, x):
    ols_result = sm.OLS(y, x).fit()
    return ts.adfuller(ols_result.resid, maxlag=1) 



def create_portfolio(df, jo_test_result):
    # From https://github.com/fplon/trading_strategies/blob/master/ewc_ewa_mean_reversion_pairs_trade.ipynb
    # Needs to be adapted to be used here.
    '''# uses the first column of eigenvectors as this will have the shortest
    # half life due to the eigenvectors are ordered with the strongest first
    # uses matrix multiplication to create a 1500x1 vector 'y_port'''
    y_port = pd.DataFrame(np.dot(df.values, jo_test_result.evec[:, 0]), #  ***look-ahead bias***
                      columns = ['y'], # single price the portfolio (eigenvector * prices)
                      index = df.index) #  (net) market value of portfolio

    y_port['y_lag'] = y_port.shift() # one day lag
    y_port['delta_y'] = y_port['y'] - y_port['y_lag']

    regress_results = sm.ols(formula = 'delta_y ~ y_lag', data = y_port).fit() # Note this can deal with NaN in top row

    halflife = -np.log(2) / regress_results.params['y_lag']
    # the steeper the slope of the regression line, the smaller (shorter) the half day
    
    #  Apply a simple linear mean reversion strategy to EWA-EWC
    lookback = np.round(halflife).astype(int) #  setting lookback to the halflife found above
    y_port['roll_avg'] = y_port['y'].rolling(lookback).mean()
    y_port['roll_std'] = y_port['y'].rolling(lookback).std()
                       
    # capital invested in portfolio in dollars.  
    # rolling z-score to determine position weights
    # no limits on num_units in this strategy
    # volatility scaled - lower vol results in a bigger positon size
    y_port['num_units'] = -(y_port['y'] - y_port['roll_avg']) / y_port['roll_std']
    
    # eigenvector can be viewed as the capital allocation (weights), 
    # while positions is the dollar capital in each ETF.
    num_units = np.expand_dims(y_port['num_units'].values, axis = 1)
    row_evecs = np.expand_dims(jo_test_result.evec[:, 0], axis=1).T
    
    # Dollar positions
    positions = pd.DataFrame(np.dot(num_units, row_evecs) * df.values, 
                             index = df.index,
                             columns = df.columns) 
    positions['capital'] = np.sum(np.abs(positions.shift()), axis = 1)
    
    return y_port, positions

class color:
   PURPLE = '\033[95m'
   CYAN = '\033[96m'
   DARKCYAN = '\033[36m'
   BLUE = '\033[94m'
   GREEN = '\033[92m'
   YELLOW = '\033[93m'
   RED = '\033[91m'
   BOLD = '\033[1m'
   UNDERLINE = '\033[4m'
   END = '\033[0m'