import pandas as pd
import yfinance as yf
import os
import ta
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import warnings

warnings.filterwarnings("ignore")

class Company:

    def __init__(self, ticker, filename):
        self.ticker = ticker
        self.filename = filename
        self.data = self.load_data()

    def load_data(self):
        if os.path.exists(self.filename):
            # If file exists, load data from the file
            data = pd.read_csv(self.filename, index_col=0, parse_dates=True)
            last_date = data.index[-1]  # Get the last date in the data

            # Check if the data needs to be updated (if it's less than a year old)
            if last_date >= datetime.now() - timedelta(days=365):
                return data  # If data is up to date, return it

            # If data needs to be updated, fetch new data from Yahoo Finance
            start_date = last_date + timedelta(days=1)
            end_date = datetime.now()
            new_data = yf.download(self.ticker, start=start_date, end=end_date)
            data = pd.concat([data, new_data])  # Concatenate old and new data
            data.to_csv(self.filename)  # Save updated data to file
        else:
            # If file doesn't exist, fetch data from Yahoo Finance for one year
            end_date = datetime.now()
            start_date = end_date - timedelta(days=365)
            data = yf.download(self.ticker, start=start_date, end=end_date)
            data.to_csv(self.filename)  # Save fetched data to file

        return data

    def save_data(self):
        self.data.to_csv(self.filename)

    def generate_signals(self):
        self.data['RSI'] = ta.momentum.RSIIndicator(self.data['Close'], window=14).rsi()
        self.data['MACD'] = ta.trend.MACD(self.data['Close']).macd()
        self.data['MACD_Signal'] = ta.trend.MACD(self.data['Close']).macd_signal()
        self.data['BollingerB_High'] = ta.volatility.BollingerBands(self.data['Close']).bollinger_hband()
        self.data['BollingerB_Low'] = ta.volatility.BollingerBands(self.data['Close']).bollinger_lband()

        signals = []
        for i in range(len(self.data)):
            if self.data['RSI'][i] < 30 and self.data['MACD'][i] > self.data['MACD_Signal'][i] and self.data['Close'][i] < self.data['BollingerB_Low'][i]:
                signals.append('Buy')
            elif self.data['RSI'][i] > 70 and self.data['MACD'][i] < self.data['MACD_Signal'][i] and self.data['Close'][i] > self.data['BollingerB_High'][i]:
                signals.append('Sell')
            else:
                signals.append('Hold')
        
        self.data['Signals'] = signals

    def plot_technical_indicators(self):
        # Plot 1: Price, Bollinger Bands, RSI
        plt.figure(figsize=(12, 10))

        plt.subplot(2, 1, 1)
        plt.plot(self.data['Close'], label='Price')

        plt.plot(self.data['BollingerB_High'], label='Bollinger Band High', linestyle='--')
        plt.plot(self.data['BollingerB_Low'], label='Bollinger Band Low', linestyle='--')

        plt.axhline(y=70, color='r', linestyle='--', label='RSI Overbought (70)')
        plt.axhline(y=30, color='g', linestyle='--', label='RSI Oversold (30)')
        plt.plot(self.data['RSI'], label='RSI', linestyle='-')

        # Fill periods when price is outside Bollinger Bands and RSI is in overbought/oversold territory
        for i in range(len(self.data)):
            if (self.data['Close'][i] > self.data['BollingerB_High'][i] and self.data['RSI'][i] > 70) or \
                    (self.data['Close'][i] < self.data['BollingerB_Low'][i] and self.data['RSI'][i] < 40):
                plt.axvspan(self.data.index[i], self.data.index[i+1], color='gray', alpha=0.3)

        plt.title(f'{self.ticker} Price, Bollinger Bands, and RSI')
        plt.legend()
        plt.xlabel('Date')
        plt.ylabel('Price/Indicator Value')

        # Plot 2: MACD and MACD Signal
        plt.subplot(2, 1, 2)
        plt.plot(self.data['MACD'], label='MACD')
        plt.plot(self.data['MACD_Signal'], label='MACD Signal')

        plt.title(f'{self.ticker} MACD and Signal Line')
        plt.legend()
        plt.xlabel('Date')
        plt.ylabel('MACD Value')
        plt.tight_layout()

        plot_file_name = f'plots/{ticker}_technical_indicators.png'
        plt.savefig(plot_file_name)
        plt.close()

# List of company tickers
company_tickers = ['AAPL', 'MSFT', 'GOOGL']  # Add more company tickers as needed
paris_companies = ['ML.PA', 'DG.PA', 'AI.PA', 'SU.PA', 'CAP.PA', 'EN.PA', 'RI.PA', 'SW.PA', 'AIR.PA', 'WLN.PA', 'OR.PA','HO.PA', 'MC.PA', 'CA.PA', 'BN.PA', 'KER.PA', 'LR.PA', 'ACA.PA', 'ATO.PA', 'VIE.PA', 'SAN.PA', 'GLE.PA', 'ORA.PA', 'SGO.PA', 'VIV.PA', 'AC.PA', 'ENGI.PA', 'BNP.PA']
companies = ['CA.PA']

# Iterate through each company ticker
for ticker in paris_companies:
    file_name = f'datas/{ticker}_data.csv'
    company = Company(ticker, file_name)

    # Daily Data Checking Routine
    def data_checking_routine():
        company.load_data()
        company.generate_signals()
        company.save_data()

    # Daily Investment Routine
    def daily_investment_routine():
        company.load_data()

        for i in range(len(company.data)):
            if company.data['Signals'][i] == 'Buy':
                print(f"Buy {ticker} at {company.data['Close'][i]} on {company.data.index[i]}")
                # Replace this with your buy order execution logic
            elif company.data['Signals'][i] == 'Sell':
                print(f"Sell {ticker} at {company.data['Close'][i]} on {company.data.index[i]}")
                # Replace this with your sell order execution logic

        company.plot_technical_indicators()

    # Execute routines for each company
    # data_checking_routine()
    # daily_investment_routine()

def calculate_roi(ticker):
    file_name = f'datas/{ticker}_data.csv'
    company = Company(ticker, file_name)

    # Load data for the past year
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    company.data = yf.download(ticker, start=start_date, end=end_date)

    # Generate signals
    company.generate_signals()

    # Simulate buying and selling based on signals
    initial_balance = 10000  # Initial balance in dollars
    balance = initial_balance
    shares = 0
    buy_price = 0
    sell_price = 0

    for i in range(len(company.data)):
        if company.data['Signals'][i] == 'Buy' and balance > 0:
            shares = balance / company.data['Close'][i]
            buy_price = company.data['Close'][i]
            balance = 0
        elif company.data['Signals'][i] == 'Sell' and shares > 0:
            sell_price = company.data['Close'][i]
            balance = shares * sell_price
            shares = 0

    if shares > 0:
        balance = shares * company.data['Close'][-1]

    # Calculate Return on Investment (ROI)
    final_balance = balance
    roi = (final_balance - initial_balance) / initial_balance * 100  # ROI as percentage

    return {
        'Ticker': ticker,
        'ROI': roi
    }

roi_results = {}  # Initialize roi_results dictionary

for ticker in paris_companies:
    roi_result = calculate_roi(ticker)
    roi_results[ticker] = roi_result['ROI']

print("ROI for each company:")
for ticker, roi in roi_results.items():
    print(f"{ticker}: {roi:.2f}%")
