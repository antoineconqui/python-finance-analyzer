from datetime import datetime, date, timedelta
from io import open
from json import loads, dumps
from os.path import isfile, isdir
from os import stat, makedirs
from time import time
from numpy import savetxt
from yfinance import Ticker

from finance import *
from strategy_display import plot_macd, plot_rsi, plot_boll, save_macd, save_rsi, save_boll
from email_sender import send_mail


class Company:

    def __init__(self, symbol):
        self.symbol = symbol
        if ('./datas/' + symbol + '.json') and stat('./datas/' + symbol + '.json').st_size != 0:
            with open('./datas/' + symbol + '.json', encoding='utf-8-sig') as file:
                data = loads(file.read())
                self.prices = data['prices']
                self.technical_indicators = data['technical_indicators']
                self.signals = data['signals']
        else:
            self.init_prices()
        self.update()

    def init_prices(self):
        self.prices = []
        datas = Ticker(self.symbol).history(period='1y')['Close']
        for i in range(len(datas)):
            self.prices.append({"date": str(datas.index[i]).split(' ')[0], "price": "%.2f" % datas[i]})

    def update_prices(self):
        datas = \
        Ticker(self.symbol).history(start=datetime.strptime(self.prices[-1]['date'], '%Y-%m-%d') + timedelta(days=1))[
            'Close']
        for i in range(len(datas)):
            self.prices.append({"date": str(datas.index[i]).split(' ')[0], "price": "%.2f" % datas[i]})

    def update_technicals_indicators(self):
        self.signals, self.technical_indicators = {}, {}
        self.signals["macd"], self.signals["macd_diff"], self.signals["macd_signal"], self.technical_indicators["macd"] = get_macd(self)
        self.signals["rsi"], self.technical_indicators["rsi"] = get_rsi(self)
        self.signals["boll_lband"], self.signals["boll_mavg"], self.signals["boll_hband"], self.technical_indicators["boll"] = get_bollinger_bands(self)

    def update(self):
        if len(self.prices) != 0 and self.prices[-1]['date'] != datetime.strftime(date.today(), '%Y-%m-%d'):
            self.update_prices()
            self.update_technicals_indicators()
            self.save_to_file()

    def save_to_file(self):
        file = open('./datas/' + self.symbol + '.json', 'w')
        file.write(self.toJSON())
        file.close()

    def toJSON(self):
        return dumps(self, default=lambda o: o.__dict__)


def main(strategy, days):
    ts = time()

    plot = {
        "macd" : lambda c : plot_macd(c),
        "rsi" : lambda c : plot_rsi(c),
        "boll" : lambda c : plot_boll(c)
    }
    save = {
        "macd" : lambda c : save_macd(c),
        "rsi" : lambda c : save_rsi(c),
        "boll" : lambda c : save_boll(c)
    }

    if not isdir('./' + datetime.strftime(datetime.today(), '%Y-%m-%d') + ' ('+strategy+')'):
        makedirs('./' + datetime.strftime(datetime.today(), '%Y-%m-%d') + ' ('+strategy+')')

    for company_symbol in revolut_companies:
    # for company_symbol in ['OTIS']:
        company = Company(company_symbol)
        # company.update()

        for order in company.technical_indicators[strategy]:
            if datetime.strptime(order['date'], '%Y-%m-%d') > datetime.today() - timedelta(days=days):
                print(company_symbol,order)
                save[strategy](company)

    print(int(time() - ts),' secondes')


def compute_profit(company):
    profit = {"macd" : 0, "rsi" : 0, "boll" : 0}
    capital = 1
    n_actions = 0

    macd = company.technical_indicators['macd']
    rsi = company.technical_indicators['rsi']
    boll = company.technical_indicators['boll']

    for signal in [macd, rsi, boll]:
        print
        if signal[0]:
            n_actions += capital / signal[2]
            capital = 0
        else:
            capital += n_actions * signal[2]
            n_actions = 0
    if capital == 0:
        capital = n_actions * company.prices[-1]
    return capital - 1


def save_results():
    results = [[], [], []]
    for company in companies:
        for i in range(3):
            results[i].append(compute_profit(company, i))

    savetxt("macd.csv", results[0], delimiter=",", fmt='%f')
    savetxt("rsi.csv", results[1], delimiter=",", fmt='%f')
    savetxt("boll.csv", results[2], delimiter=",", fmt='%f')


# save_results()
# send_mail(get_orders())

# sum = 0
# for company in nasdaq_companies:
#     profit = compute_profit(company,0)
#     sum += profit
#     print(company, profit)
# print(sum/6)

main('rsi', 2)

# company = Company('OTIS')
# save_macd(company)
# plot_rsi(company)