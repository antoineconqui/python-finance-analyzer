import os
from datetime import datetime
from pandas import Series

from matplotlib import pyplot as plt

def serie_from_datas(datas):
    index, data = [], []
    for item in datas:
        index.append(datetime.strptime(item['date'], '%Y-%m-%d'))
        data.append(float(item['price']))
    return Series(data, index)


def arrays_from_datas(datas):
    index = [datetime.strptime(e['date'], '%Y-%m-%d').date() for e in datas]
    data = [float(e['price']) for e in datas]
    return index, data


def index_from_datas(datas):
    return [e['date'] for e in datas]


def plot_price_and_signals(fig, company, data, strategy, axs):
    fig.suptitle(f'Top: {company.symbol} Stock Price. Bottom: {strategy}')

    serie = serie_from_datas([e for e in data if e['signal'] == 'Buy'])
    axs[0].scatter(serie.index, serie, color='green', label='Buy Signal', marker='^', alpha=1)

    serie = serie_from_datas([e for e in data if e['signal'] == 'Sell'])
    axs[0].scatter(serie.index, serie, color='red', label='Sell Signal', marker='v', alpha=1)

    index, datas = arrays_from_datas(company.prices)
    axs[0].plot(index, datas, label='Close Price', color='blue', alpha=0.35)

    axs[0].set_title(f'Close Price Buy/Sell Signals using {strategy}.')
    axs[0].set_xlabel('Date', fontsize=18)
    axs[0].set_ylabel('Close Price', fontsize=18)
    axs[0].legend(loc='upper left')
    axs[0].grid()


def plot_macd(company):
    fig, axs = plt.subplots(2, sharex=True, figsize=(13, 9))
    plot_price_and_signals(fig, company, company.technical_indicators['macd'], 'MACD', axs)

    index, macd = arrays_from_datas(company.signals['macd'])
    axs[1].plot(index, macd, label=company.symbol + ' MACD', color='green')

    index, macd = arrays_from_datas(company.signals['macd_signal'])
    axs[1].plot(index, macd, label='Signal Line', color='orange')

    positive = serie_from_datas([e for e in company.signals['macd_diff'] if e['price'] >= 0])
    negative = serie_from_datas([e for e in company.signals['macd_diff'] if e['price'] < 0])

    axs[1].bar(positive.index, positive, color='green')
    axs[1].bar(negative.index, negative, color='red')
    axs[1].legend(loc='upper left')
    axs[1].grid()
    plt.show()


def plot_rsi(company):
    low_rsi = 40
    high_rsi = 70

    fig, axs = plt.subplots(2, sharex=True, figsize=(13, 9))
    plot_price_and_signals(fig, company, company.technical_indicators['rsi'], 'RSI', axs)

    index, rsi = arrays_from_datas(company.signals['rsi'])
    axs[1].plot(index, rsi, label='RSI', color='blue', alpha=0.35)
    axs[1].fill_between(index, y1=low_rsi, y2=high_rsi, color='#adccff', alpha=0.3)
    axs[1].legend(loc='upper left')
    axs[1].grid()

    plt.show()


def plot_boll(company):
    image = f'images/{company.symbol}_bb.png'
    bollinger_bands = company.technical_indicators

    fig, axs = plt.subplots(2, sharex=True, figsize=(13, 9))

    plot_price_and_signals(fig, company, bollinger_bands, 'Bollinger_Bands', axs)

    axs[1].plot(bollinger_bands['Bollinger_Bands_Middle'], label='Middle', color='blue', alpha=0.35)
    axs[1].plot(bollinger_bands['Bollinger_Bands_Upper'], label='Upper', color='green', alpha=0.35)
    axs[1].plot(bollinger_bands['Bollinger_Bands_Lower'], label='Lower', color='red', alpha=0.35)
    axs[1].fill_between(bollinger_bands.index, bollinger_bands['Bollinger_Bands_Lower'],
                        bollinger_bands['Bollinger_Bands_Upper'], alpha=0.1)
    axs[1].legend(loc='upper left')
    axs[1].grid()

    plt.show()


def save_macd(company):
    fig, axs = plt.subplots(2, sharex=True, figsize=(13, 9))
    plot_price_and_signals(fig, company, company.technical_indicators['macd'], 'MACD', axs)

    index, macd = arrays_from_datas(company.signals['macd'])
    axs[1].plot(index, macd, label=company.symbol + ' MACD', color='green')

    index, macd = arrays_from_datas(company.signals['macd_signal'])
    axs[1].plot(index, macd, label='Signal Line', color='orange')

    positive = serie_from_datas([e for e in company.signals['macd_diff'] if e['price'] >= 0])
    negative = serie_from_datas([e for e in company.signals['macd_diff'] if e['price'] < 0])

    axs[1].bar(positive.index, positive, color='green')
    axs[1].bar(negative.index, negative, color='red')
    axs[1].legend(loc='upper left')
    axs[1].grid()

    plt.savefig('./'+datetime.strftime(datetime.today(), '%Y-%m-%d')+' (macd)/'+company.symbol+'.png')


def save_rsi(company):
    low_rsi = 40
    high_rsi = 70

    fig, axs = plt.subplots(2, sharex=True, figsize=(13, 9))
    plot_price_and_signals(fig, company, company.technical_indicators['rsi'], 'RSI', axs)

    index, rsi = arrays_from_datas(company.signals['rsi'])
    axs[1].plot(index, rsi, label='RSI', color='blue', alpha=0.35)
    axs[1].fill_between(index, y1=low_rsi, y2=high_rsi, color='#adccff', alpha=0.3)
    axs[1].legend(loc='upper left')
    axs[1].grid()

    plt.savefig('./'+datetime.strftime(datetime.today(), '%Y-%m-%d')+' (rsi)/'+company.symbol+'.png')


def save_boll(company):
    image = f'images/{company.symbol}_bb.png'
    bollinger_bands = company.technical_indicators

    fig, axs = plt.subplots(2, sharex=True, figsize=(13, 9))

    plot_price_and_signals(fig, company, bollinger_bands, 'Bollinger_Bands', axs)

    axs[1].plot(bollinger_bands['Bollinger_Bands_Middle'], label='Middle', color='blue', alpha=0.35)
    axs[1].plot(bollinger_bands['Bollinger_Bands_Upper'], label='Upper', color='green', alpha=0.35)
    axs[1].plot(bollinger_bands['Bollinger_Bands_Lower'], label='Lower', color='red', alpha=0.35)
    axs[1].fill_between(bollinger_bands.index, bollinger_bands['Bollinger_Bands_Lower'],
                        bollinger_bands['Bollinger_Bands_Upper'], alpha=0.1)
    axs[1].legend(loc='upper left')
    axs[1].grid()

    plt.savefig('./'+datetime.strftime(datetime.today(), '%Y-%m-%d')+' (boll)/'+company.symbol+'.png')