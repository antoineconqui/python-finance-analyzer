from datetime import datetime, date, timedelta
from io import open
from json import loads, dumps
from os.path import isfile, isdir
from os import stat, makedirs
from time import time
from numpy import savetxt, mean
from yfinance import Ticker

from finance import *
from strategy_display import *
from email_sender import send_mail

class Company:

    def __init__(self, symbol):
        self.symbol = symbol
        if isfile('./datas/'+symbol+'/datas.json') and stat('./datas/'+symbol+'/datas.json').st_size != 0:
            with open('./datas/'+symbol+'/datas.json', encoding='utf-8-sig') as file:
                data = loads(file.read())
                self.data['Close'] = data['Close']
                self.data['technical_indicators'] = data['prices']
                self.data['Close'] = data['prices']
                self.technical_indicators = data['technical_indicators']
                self.signals = data['signals']
            self.update()
        else:
            if not isdir('./datas/'+self.symbol):
                makedirs('./datas/'+self.symbol)
            self.init_prices()
            self.update_technicals_indicators()
            self.save_to_file()

    def init_prices(self):
        self.data['Close'] = Ticker(self.symbol).history(period='1y')['Close']

    def update_prices(self):
        datas = Ticker(self.symbol).history(start=datetime.strptime(self.data['Close'][-1]['date'], '%Y-%m-%d') + timedelta(days=1))['Close']
        for i in range(len(datas)):
            self.prices.append({"date": str(datas.index[i]).split(' ')[0], "price": "%.2f" % datas.iloc[i]})

    def update_technicals_indicators(self):
        self.signals, self.technical_indicators = {}, {}
        signals = generate_signals(self.signals)
        self.signals["macd"], self.signals["macd_diff"], self.signals["macd_signal"], self.technical_indicators["macd"] = get_macd(self)
        self.signals["rsi"], self.technical_indicators["rsi"] = get_rsi(self)
        self.signals["boll_lband"], self.signals["boll_mavg"], self.signals["boll_hband"], self.technical_indicators["boll"] = get_bollinger_bands(self)

    def update(self):
        if len(self.prices) != 0 and self.prices[-1]['date'] != datetime.strftime(date.today(), '%Y-%m-%d'):
            self.update_prices()
            self.update_technicals_indicators()
            self.save_to_file()

    def save_to_file(self):
        file = open('./datas/'+self.symbol+'/datas.json', 'w')
        file.write(self.toJSON())
        file.close()

    def toJSON(self):
        return dumps(self, default=lambda o: o.__dict__)

def get_orders(strategy, companies, days):
    orders = []
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

    for company_symbol in companies:
        company = Company(company_symbol)
        for order in company.technical_indicators[strategy]:
            if datetime.strptime(order['date'], '%Y-%m-%d') > datetime.today() - timedelta(days=days):
                save[strategy](company)
                order['symbol'] = company_symbol
                order['image'] = './'+datetime.strftime(datetime.today(), '%Y-%m-%d')+' ('+strategy+')/'+company.symbol+'.png'
                orders.append(order)

    return orders

def compute_profit(company):

    profit = {"macd" : 0, "rsi" : 0, "boll" : 0}

    for strategy in profit.keys():
        capital, n_actions = 1, 0
        technical_indicators = company.technical_indicators[strategy]
        for signal in technical_indicators:
            if signal['signal']=='Buy':
                n_actions += capital / signal['price']
                capital = 0
            else:
                capital += n_actions * signal['price']
                n_actions = 0
        if capital == 0:
            capital = n_actions * float(company.prices[-1]['price'])
        profit[strategy] = capital - 1

    return profit

def compute_global_profit(company):
    capital, n_actions = 1, 0
    technical_indicators = (company.technical_indicators['macd']+company.technical_indicators['rsi']+company.technical_indicators['boll'])#.sort(key=lambda x: x['date'], reverse=True)
    technical_indicators.sort(key=lambda x: x['date'], reverse=True)
    for signal in technical_indicators:
        if signal['signal']=='Buy':
            n_actions += capital / signal['price']
            capital = 0
        else:
            capital += n_actions * signal['price']
            n_actions = 0
    if capital == 0:
        capital = n_actions * float(company.prices[-1]['price'])

    return capital - 1

def save_results():
    results = [[], [], []]
    for company in companies:
        for i in range(3):
            results[i].append(compute_profit(company, i))

    savetxt("macd.csv", results[0], delimiter=",", fmt='%f')
    savetxt("rsi.csv", results[1], delimiter=",", fmt='%f')
    savetxt("boll.csv", results[2], delimiter=",", fmt='%f')

# send_mail(get_orders('rsi', paris_companies + revolut_companies, 2))

companies = ['META', 'AMZN', 'MSFT', 'GOOGL', 'AI.PA']

paris_companies = ['ML.PA', 'DG.PA', 'AI.PA', 'SU.PA', 'CAP.PA', 'EN.PA', 'RI.PA', 'SW.PA', 'AIR.PA', 'WLN.PA', 'OR.PA','HO.PA', 'MC.PA', 'CA.PA', 'BN.PA', 'KER.PA', 'LR.PA', 'ACA.PA', 'ATO.PA', 'VIE.PA', 'SAN.PA', 'GLE.PA', 'ORA.PA', 'SGO.PA', 'VIV.PA', 'AC.PA', 'ENGI.PA', 'BNP.PA']
revolut_companies = ['A', 'AA', 'AAL', 'AAP', 'AAPL', 'ABBV', 'ABEV', 'ABNB', 'ABT', 'ADBE', 'ADI', 'ADM', 'ADP',
                     'ADSK', 'AEO', 'AEP', 'AES', 'AFL', 'AG', 'AGNC', 'AI', 'AIG', 'AKAM', 'AL', 'ALB', 'ALGN', 'ALL',
                     'ALLT', 'ALLY', 'ALXN', 'AMAT', 'AMC', 'AMD', 'AME', 'AMGN', 'AMH', 'AMRX', 'AMT', 'AMZN',
                     'ANET', 'ANF', 'ANGI', 'ANSS', 'ANTM', 'AOS', 'APA', 'APD', 'APH', 'APPN', 'APPS', 'AR', 'ARCC',
                     'ARCT', 'ARI', 'ARMK', 'ARNC', 'ARR', 'ASAN', 'ASML', 'ATHM', 'ATR', 'ATUS', 'ATVI', 'AU', 'AUY',
                     'AVB', 'AVGO', 'AVLR', 'AXL', 'AXON', 'AXP', 'AXTA', 'AYX', 'AZN', 'AZO', 'BA', 'BABA', 'BAC',
                     'BAH', 'BAM', 'BAP', 'BAX', 'BB', 'BBAR', 'BBD', 'BBY', 'BDC', 'BDX', 'BEN', 'BEP', 'BEPC',
                     'BG', 'BHC', 'BHP', 'BIDU', 'BIIB', 'BILI', 'BIO', 'BIP', 'BIPC', 'BJ', 'BK', 'BKNG',
                     'BKR', 'BLK', 'BLL', 'BMA', 'BMRN', 'BMY', 'BNTX', 'BOX', 'BP', 'BRFS', 'BRX', 'BSBR',
                     'BSMX', 'BSX', 'BTG', 'BUD', 'BVN', 'BWA', 'BX', 'BYND', 'BZUN', 'C', 'CABO', 'CAG', 'CAH', 'CAJ',
                     'CARR', 'CARS', 'CAT', 'CBOE', 'CBRE', 'CC', 'CCI', 'CCL', 'CDE', 'CDNS', 'CERN', 'CF', 'CFG',
                     'CG', 'CGNX', 'CHGG', 'CHKP', 'CHS', 'CHTR', 'CHWY', 'CI', 'CIEN', 'CIG', 'CIM', 'CL',
                     'CLDR', 'CLF', 'CLNY', 'CLR', 'CLVS', 'CLX', 'CMA', 'CMCSA', 'CME', 'CMG', 'CNC', 'CNDT', 'CNP',
                     'CNX', 'COF', 'COG', 'COLD', 'COMM', 'COP', 'COST', 'COTY', 'CRM', 'CROX', 'CRSP', 'CRWD', 'CSCO',
                     'CSGP', 'CSX', 'CTAS', 'CTSH', 'CTVA', 'CTXS', 'CVE', 'CVNA', 'CVS', 'CVX', 'CWEN', 'CX',
                     'CYH', 'CZR', 'D', 'DAL', 'DAN', 'DASH', 'DBX', 'DD', 'DDOG', 'DE', 'DELL', 'DFS', 'DG',
                     'DHC', 'DHI', 'DHR', 'DIN', 'DIS', 'DISCA', 'DISCK', 'DISH', 'DKNG', 'DLR', 'DLTR', 'DOCU',
                     'DOW', 'DPZ', 'DRE', 'DRI', 'DUK', 'DVA', 'DVN', 'DXC', 'DXCM', 'EA', 'EB', 'EBAY', 'ECL', 'ED',
                     'EDU', 'EFX', 'EGO', 'EIX', 'EL', 'ELAN', 'EMR', 'ENIA', 'ENLC', 'ENPH', 'EOG', 'EPAM', 'EPD',
                     'EQH', 'EQIX', 'EQNR', 'EQR', 'EQT', 'ERJ', 'ESI', 'ET', 'ETRN', 'ETSY', 'EVR', 'EW',
                     'EXAS', 'EXC', 'EXEL', 'EXPE', 'F', 'FANG', 'FAST', 'FB', 'FCX', 'FDS', 'FDX', 'FE', 'FEYE',
                     'FFIV', 'FHN', 'FIS', 'FISV', 'FITB', 'FL', 'FLEX', 'FLR', 'FLT', 'FOLD', 'FOXA', 'FREQ',
                     'FROG', 'FSK', 'FSLR', 'FSLY', 'FTI', 'FTNT', 'FTV', 'FVE', 'FVRR', 'FWONK', 'GD', 'GDDY', 'GDS',
                     'GE', 'GEO', 'GES', 'GFI', 'GGAL', 'GGB', 'GILD', 'GIS', 'GLUU', 'GLW', 'GM', 'GME', 'GMED', 'GNL',
                     'GNTX', 'GNW', 'GO', 'GOL', 'GOLD', 'GOOG', 'GOOGL', 'GPK', 'GPRO', 'GPS', 'GRPN', 'GRUB', 'GS',
                     'GSK', 'GT', 'GWPH', 'H', 'HAL', 'HAS', 'HBAN', 'HBI', 'HCA', 'HCM', 'HD', 'HDB', 'HEI', 'HES',
                     'HFC', 'HGV', 'HIG', 'HIMX', 'HL', 'HLF', 'HLT', 'HMC', 'HMY', 'HOG', 'HOLX', 'HOME', 'HON', 'HPE',
                     'HPQ', 'HRB', 'HRL', 'HSIC', 'HST', 'HTHT', 'HUBS', 'HUM', 'HUN', 'HUYA', 'HWM', 'IAG', 'IBKR',
                     'IBM', 'IBN', 'ICE', 'ICPT', 'IDXX', 'IGMS', 'IGT', 'IIPR', 'ILMN', 'IMGN', 'INCY', 'INFN', 'INFY',
                     'INO', 'INTC', 'INTU', 'INVH', 'IP', 'IPG', 'IQ', 'IRBT', 'IRM', 'ISBC', 'ISRG', 'IT', 'ITUB',
                     'ITW', 'IVR', 'IVZ', 'JBHT', 'JBLU', 'JD', 'JEF', 'JKHY', 'JKS', 'JMIA', 'JNJ', 'JNPR', 'JPM',
                     'JWN', 'K', 'KAR', 'KDP', 'KEY', 'KEYS', 'KGC', 'KHC', 'KIM', 'KKR', 'KMB', 'KMI', 'KNX', 'KO',
                     'KR', 'KSS', 'KT', 'KTOS', 'LB', 'LDOS', 'LEN', 'LESL', 'LEVI', 'LI', 'LKQ', 'LLY', 'LMND', 'LMT',
                     'LNG', 'LOGI', 'LOMA', 'LOW', 'LPL', 'LRCX', 'LSCC', 'LTC', 'LTHM', 'LULU', 'LUMN', 'LUV',
                     'LVS', 'LX', 'LXRX', 'LYFT', 'LYV', 'M', 'MA', 'MAR', 'MAS', 'MAT', 'MAXN', 'MBT', 'MCD',
                     'MCFE', 'MCHP', 'MCO', 'MDB', 'MDLZ', 'MDRX', 'MDT', 'MELI', 'MET', 'MFA', 'MFG', 'MGI', 'MGM',
                     'MIK', 'MKL', 'MLCO', 'MMC', 'MMM', 'MNST', 'MO', 'MOMO', 'MORN', 'MOS', 'MPC', 'MPLX', 'MPW',
                     'MRK', 'MRNA', 'MRO', 'MRVL', 'MS', 'MSFT', 'MSGS', 'MSI', 'MSP', 'MTCH', 'MTD', 'MTDR', 'MTG',
                     'MU', 'MUFG', 'MUR', 'MUX', 'MXIM', 'NAVI', 'NBEV', 'NBIX', 'NCLH', 'NDAQ', 'NEE', 'NEM',
                     'NET', 'NFLX', 'NICE', 'NIO', 'NKE', 'NKLA', 'NKTR', 'NLOK', 'NLY', 'NMR', 'NOAH', 'NOC', 'NOV',
                     'NOW', 'NPTN', 'NRG', 'NRZ', 'NSC', 'NTAP', 'NTCO', 'NTES', 'NTNX', 'NTRS', 'NUE', 'NUVA', 'NVAX',
                     'NVCR', 'NVDA', 'NVR', 'NVTA', 'NWL', 'NWSA', 'NYCB', 'NYMT', 'NYT', 'O', 'ODP', 'OKE',
                     'OKTA', 'OLN', 'OMC', 'ON', 'OPK', 'ORCL', 'ORLY', 'OSTK', 'OTIS', 'OVV', 'OXY', 'PAA', 'PAAS',
                     'PAM', 'PANW', 'PAYX', 'PBCT', 'PBF', 'PBH', 'PBI', 'PBR', 'PCAR', 'PCG', 'PD', 'PDCE', 'PDD',
                     'PEG', 'PENN', 'PEP', 'PFE', 'PFPT', 'PG', 'PGR', 'PH', 'PHM', 'PINS', 'PLAN', 'PLD', 'PLNT',
                     'PLTR', 'PLUG', 'PM', 'PNC', 'PPG', 'PPL', 'PRI', 'PRU', 'PS', 'PSA', 'PSTG', 'PSX', 'PTEN',
                     'PTON', 'PWR', 'PXD', 'PYPL', 'QCOM', 'QD', 'QLYS', 'QRTEA', 'QSR', 'QTWO', 'RACE', 'RAD', 'RCL',
                     'RDFN', 'REAL', 'REGI', 'REGN', 'RES', 'RF', 'RH', 'RKT', 'RL', 'RLGY', 'RMD', 'RNG', 'ROK',
                     'ROKU', 'ROOT', 'ROST', 'RRC', 'RTX', 'RUN', 'RXT', 'RY', 'SAVE', 'SBH', 'SBS', 'SBSW', 'SBUX',
                     'SCCO', 'SCHW', 'SE', 'SEB', 'SEDG', 'SFIX', 'SFM', 'SGMO', 'SHAK', 'SHOP', 'SHW', 'SID', 'SIRI',
                     'SKT', 'SKX', 'SLB', 'SLCA', 'SLM', 'SM', 'SMAR', 'SMFG', 'SMG', 'SNAP', 'SNE', 'SNOW', 'SNPS',
                     'SO', 'SOGO', 'SPCE', 'SPG', 'SPGI', 'SPLK', 'SPOT', 'SPWR', 'SQ', 'SQM', 'SRE', 'SSNC', 'SSSS',
                     'STAY', 'STLA', 'STLD', 'STNE', 'STT', 'STX', 'STZ', 'SU', 'SUMO', 'SUPV', 'SWK', 'SWKS', 'SWN',
                     'SYF', 'SYK', 'SYY', 'T', 'TAK', 'TAL', 'TCOM', 'TD', 'TDOC', 'TEAM', 'TECK', 'TER', 'TEVA', 'TFC',
                     'TFX', 'TGI', 'TGT', 'TIGR', 'TIMB', 'TJX', 'TM', 'TME', 'TMO', 'TMUS', 'TPR',
                     'TPX', 'TRGP', 'TRIP', 'TROW', 'TRV', 'TSLA', 'TSM', 'TSN', 'TTD', 'TTM', 'TTWO', 'TV', 'TW',
                     'TWLO', 'TWO', 'TWOU', 'TWTR', 'TXMD', 'TXN', 'U', 'UA', 'UAA', 'UAL', 'UBER', 'UCTT', 'UGP',
                     'ULTA', 'UMC', 'UNH', 'UNIT', 'UNM', 'UNP', 'UPS', 'URBN', 'USB', 'UXIN', 'V', 'VALE', 'VEEV',
                     'VER', 'VFC', 'VG', 'VGR', 'VIACA', 'VICI', 'VIPS', 'VIR', 'VIV', 'VLO', 'VMW', 'VRM', 'VRSK',
                     'VRSN', 'VRTX', 'VST', 'VTR', 'VTRS', 'VZ', 'W', 'WAB', 'WB', 'WBA', 'WDAY', 'WDC', 'WELL', 'WEN',
                     'WEX', 'WFC', 'WING', 'WIT', 'WIX', 'WKHS', 'WM', 'WMB', 'WMT', 'WORK', 'WRK', 'WTM', 'WU',
                      'WWE', 'WY', 'WYNN', 'X', 'XEC', 'XEL', 'XGN', 'XLNX', 'XOM', 'XPEV', 'XRX', 'YETI', 'YPF',
                     'YUM', 'YUMC', 'YY', 'Z', 'ZBH', 'ZBRA', 'ZEN', 'ZION', 'ZM', 'ZNGA', 'ZNH', 'ZS', 'ZTO', 'ZTS']


strategies = {"global" : [], "macd" : [], "rsi" : [], "boll" : []}

def test_strategy(company, strategy):
    
    return

for c in ['META']:
    company = Company(c)
    # save_signals(company)
    plot_indicator(company, 'macd', True)
    profit = compute_profit(company)
    global_profit = compute_global_profit(company)

    for strategy in profit.keys():
        if(strategy!='global'):
            strategies[strategy].append(profit[strategy])
    strategies['global'].append(global_profit)


for strategy in strategies.keys():
    strategies[strategy] = "{:.2f}".format(mean(strategies[strategy]))
    print(strategy,float(strategies[strategy])*100,'%')
    # print(strategy,"{:.0f}".format(strategies[strategy]*100),'%')