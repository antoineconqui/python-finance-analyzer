from datetime import datetime

from pandas import Series
from ta.momentum import RSIIndicator
from ta.trend import MACD
from ta.volatility import BollingerBands

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

paris_companies = ['ML.PA', 'DG.PA', 'AI.PA', 'SU.PA', 'CAP.PA', 'EN.PA', 'RI.PA', 'SW.PA', 'AIR.PA', 'WLN.PA', 'OR.PA',
                   'HO.PA', 'MC.PA', 'CA.PA', 'BN.PA', 'KER.PA', 'LR.PA', 'FP.PA', 'ACA.PA', 'ATO.PA', 'VIE.PA',
                   'SAN.PA',
                   'GLE.PA', 'ORA.PA', 'SGO.PA', 'VIV.PA', 'AC.PA', 'ENGI.PA', 'BNP.PA']


def serie_from_datas(datas):
    index, data = [], []
    for item in datas:
        index.append(datetime.strptime(item['date'], '%Y-%m-%d'))
        data.append(float(item['price']))
    return Series(data, index)


def datas_from_serie(serie):
    return [{"date": datetime.strftime(serie.index[i], '%Y-%m-%d'), "price": serie.iloc[i]} for i in range(len(serie))]


def generate_buy_sell_signals(condition_buy, condition_sell, prices):
    last_signal = None
    indicators = []
    signals = []
    for i in range(0, len(prices)):
        if condition_buy(i) and last_signal != 'Buy':
            last_signal = 'Buy'
            indicators.append(last_signal)
            signals.append({"signal" : last_signal, "date" : prices[i]['date'], "price" : float(prices[i]['price'])})
        elif condition_sell(i) and last_signal == 'Buy':
            last_signal = 'Sell'
            indicators.append(last_signal)
            signals.append({"signal" : last_signal, "date" : prices[i]['date'], "price" : float(prices[i]['price'])})
    return signals


# Function to generate buy/sell signals
def generate_signals(data):
    # Calculate indicators (RSI, MACD, Bollinger Bands)
    data['RSI'] = RSIIndicator(data['Close'], window=14).rsi()
    data['MACD'] = MACD(data['Close']).macd()
    data['MACD_Signal'] = MACD(data['Close']).macd_signal()
    data['BollingerB_High'] = BollingerBands(data['Close']).bollinger_hband()
    data['BollingerB_Low'] = BollingerBands(data['Close']).bollinger_lband()

    signals = []
    for i in range(len(data)):
        # Conditions for buy/sell signals
        if data['RSI'][i] < 30 and data['MACD'][i] > data['MACD_Signal'][i] and data['Close'][i] < data['BollingerB_Low'][i]:
            signals.append('Buy')
        elif data['RSI'][i] > 70 and data['MACD'][i] < data['MACD_Signal'][i] and data['Close'][i] > data['BollingerB_High'][i]:
            signals.append('Sell')
        else:
            signals.append('Hold')
    
    data['Signals'] = signals
    return data

def get_macd(company):
    macd = MACD(serie_from_datas(company.prices))
    return datas_from_serie(macd.macd()), datas_from_serie(macd.macd_diff()), datas_from_serie(macd.macd_signal()), generate_buy_sell_signals(
        lambda x: macd.macd().values[x] < macd.macd_signal().iloc[x],
        lambda x: macd.macd().values[x] > macd.macd_signal().iloc[x],
        company.prices[:-1])


def get_rsi(company):
    rsi_time_period = 20
    low_rsi = 40
    high_rsi = 70

    rsi_indicator = RSIIndicator(serie_from_datas(company.prices), rsi_time_period)

    return datas_from_serie(rsi_indicator.rsi()), generate_buy_sell_signals(
        lambda x: rsi_indicator.rsi().values[x] < low_rsi,
        lambda x: rsi_indicator.rsi().values[x] > high_rsi,
        company.prices)


def get_bollinger_bands(company):
    indicator_bb = BollingerBands(serie_from_datas(company.prices))

    return datas_from_serie(indicator_bb.bollinger_lband()), datas_from_serie(indicator_bb.bollinger_mavg()), datas_from_serie(indicator_bb.bollinger_hband()), generate_buy_sell_signals(
        lambda x: float(company.prices[x]['price']) < indicator_bb.bollinger_lband().values[x],
        lambda x: float(company.prices[x]['price']) > indicator_bb.bollinger_hband().values[x],
        company.prices)
