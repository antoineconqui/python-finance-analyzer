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


def plot_price_and_signals(company, datas, strategy, axs):
    signals = serie_from_datas([e for e in datas if e['signal'] == 'Buy'])
    axs[0].scatter(signals.index, signals, color='green', label='Buy Signal', marker='^', alpha=1)

    signals = serie_from_datas([e for e in datas if e['signal'] == 'Sell'])
    axs[0].scatter(signals.index, signals, color='red', label='Sell Signal', marker='v', alpha=1)

    for i in range(len(signals)):
        index = [data['date'] for data in datas].index(signals.index[i].strftime('%Y-%m-%d'))
        buy_price = serie_from_datas([e for e in datas]).iloc[index-1]
        sell_price = serie_from_datas([e for e in datas]).iloc[index]
        axs[0].annotate("{:.1f}".format((sell_price-buy_price)/buy_price*100)+'%', (signals.index[i], signals.iloc[i]))
     
    index, datas = arrays_from_datas(company.prices)
    axs[0].plot(index, datas, label='Close Price', color='blue', alpha=0.35)

    axs[0].set_title(f'Close Price Buy/Sell Signals using {strategy}.')
    axs[0].set_xlabel('Date', fontsize=18)
    axs[0].set_ylabel('Close Price', fontsize=18)
    axs[0].legend(loc='upper left')
    axs[0].grid()


def plot_indicator(company, indicator, save=False):
    fig, axs = plt.subplots(2, sharex=True, figsize=(13, 9))

    plot_price_and_signals(company, company.technical_indicators[indicator], indicator, axs)

    if indicator == 'macd':
        index, macd = arrays_from_datas(company.signals['macd'])
        axs[1].plot(index, macd, label=company.symbol + ' MACD', color='green')

        index, macd_signal = arrays_from_datas(company.signals['macd_signal'])
        axs[1].plot(index, macd_signal, label='Signal Line', color='orange')

        positive = serie_from_datas([e for e in company.signals['macd_diff'] if e['price'] >= 0])
        negative = serie_from_datas([e for e in company.signals['macd_diff'] if e['price'] < 0])

        axs[1].bar(positive.index, positive, color='green')
        axs[1].bar(negative.index, negative, color='red')
        axs[1].legend(loc='upper left')

    elif indicator == 'rsi':
        low_rsi = 40
        high_rsi = 70

        index, rsi = arrays_from_datas(company.signals['rsi'])
        axs[1].plot(index, rsi, label='RSI', color='blue', alpha=0.35)
        axs[1].fill_between(index, y1=low_rsi, y2=high_rsi, color='#adccff', alpha=0.3)
        axs[1].legend(loc='upper left')

    elif indicator == 'boll':
        index, boll_mavg = arrays_from_datas(company.signals['boll_mavg'])
        index, boll_hband = arrays_from_datas(company.signals['boll_hband'])
        index, boll_lband = arrays_from_datas(company.signals['boll_lband'])

        axs[1].plot(index, boll_mavg, label='Middle', color='blue', alpha=0.35)
        axs[1].plot(index, boll_hband, label='Upper', color='green', alpha=0.35)
        axs[1].plot(index, boll_lband, label='Lower', color='red', alpha=0.35)
        axs[1].fill_between(index, boll_lband, boll_hband, alpha=0.1)
        axs[1].legend(loc='upper left')

    axs[1].grid()

    if save:
        path = './datas/' + company.symbol
        if not os.path.isdir(path):
            os.makedirs(path)
        plt.savefig(path + '/' + indicator + '.png')
    else:
        plt.show()