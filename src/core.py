import requests
import json
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
from datetime import datetime
from io import StringIO
import time


class Stock:
    def __init__(self, name, category, financialStatement, financialRatios, rawData):
        self.name = name
        self.category = category
        self.financialStatement = financialStatement
        self.financialRatios = financialRatios
        self.rawData = rawData


class StockInfoScraper:
    def __init__(self):
        pass


    def get_one_index(self, stockName):
        # return one index as a dict
        pass

    def get_financial_statement(self, stockName):
        # return financial statement as a dict
        pass


    def get_financial_ratios(self, stockName):
        # return financial ratios in following order in a list
        finalNames = ["Kapanis", "F/K", "FD/FAVOK", "FD/Satislar", "PD/DD"]
        pass
        

    def get_stock_info(self, symbol, startDate: str = None, endDate: str = None):
        # return stock information in a pandas dataframe with columns: 
        # CODE, DATE, CLOSING_TL, LOW_TL, HIGH_TL, VOLUME_TL, CLOSING_USD, LOW_USD, HIGH_USD, VOLUME_USD
        pass


class Analysis:
    def __init__(self, sma=None, ema=None, bbs=None, rsi=None, macd=None, soc=None, st=None, adx=None, raw=None):
        # Simple Moving Average (SMA)
        self.sma = sma if isinstance(sma, pd.core.frame.DataFrame) or sma == None else pd.read_json(StringIO(sma))
        # Exponential Moving Average (EMA)
        self.ema = ema if isinstance(ema, pd.core.frame.DataFrame) or ema == None else pd.read_json(StringIO(ema))
        # Bollinger Bands (BBS)
        self.bbs = bbs if isinstance(bbs, pd.core.frame.DataFrame) or bbs == None else pd.read_json(StringIO(bbs))
        # Relative Strength Index (RSI)
        self.rsi = rsi if isinstance(rsi, pd.core.frame.DataFrame) or rsi == None else pd.read_json(StringIO(rsi))
        # Moving Average Convergence Divergence (MACD)
        self.macd = macd if isinstance(macd, pd.core.frame.DataFrame) or macd == None else pd.read_json(StringIO(macd))
        # Stochastic Oscillator (SOC)
        self.soc = soc if isinstance(soc, pd.core.frame.DataFrame) or soc == None else pd.read_json(StringIO(soc))
        # SuperTrend (ST)
        self.st = st if isinstance(st, pd.core.frame.DataFrame) or st == None else pd.read_json(StringIO(st))
        # Average Directional Index (ADX)
        self.adx = adx if isinstance(adx, pd.core.frame.DataFrame) or adx == None else pd.read_json(StringIO(adx))
        # Raw data
        self.raw = raw if isinstance(raw, pd.core.frame.DataFrame) or raw == None else pd.read_json(StringIO(raw))


    def do_analysis(self, data):
        self.raw = data
        # Simple Moving Average (SMA)
        self.sma = self.get_sma(data)
        # Exponential Moving Average (EMA)
        self.ema = self.get_ema(data)
        # Bollinger Bands (BBS)
        self.bbs = self.get_bbs(data)
        # Relative Strength Index (RSI)
        self.rsi = self.get_rsi(data)
        # Moving Average Convergence Divergence (MACD)
        self.macd = self.get_macd(data)
        # Stochastic Oscillator (SOC)
        self.soc = self.get_soc(data)
        # SuperTrend (ST)
        self.st = self.get_st(data)
        # Average Directional Index (ADX)
        self.adx = self.get_adx(data)


    def get_sma(self, data, lookbackShort = 20, lookbackLong = 50):
        smaFrame = pd.DataFrame()
        smaFrame['SMA20'] = data['CLOSING_TL'].rolling(window=lookbackShort).mean()
        smaFrame['SMA50'] = data['CLOSING_TL'].rolling(window=lookbackLong).mean()
        smaFrame['SIGNAL+'] = np.where(smaFrame['SMA20'] > smaFrame['SMA50'], 1, 0)
        smaFrame['SIGNAL-'] = np.where(smaFrame['SMA50'] > smaFrame['SMA20'], 1, 0)
        return smaFrame


    def get_ema(self, data, lookbackShort = 20, lookbackLong = 50):
        emaFrame = pd.DataFrame()
        emaFrame['EMA20'] = data['CLOSING_TL'].ewm(span=lookbackShort, adjust=False).mean()
        emaFrame['EMA50'] = data['CLOSING_TL'].ewm(span=lookbackLong, adjust=False).mean()
        emaFrame['SIGNAL+'] = np.where(emaFrame['EMA20'] > emaFrame['EMA50'], 1, 0)
        emaFrame['SIGNAL-'] = np.where(emaFrame['EMA50'] > emaFrame['EMA20'], 1, 0)
        return emaFrame


    def get_bbs(self, data, lookback = 20):
        bollingerFrame = pd.DataFrame()
        # Calculate the 20-period Simple Moving Average (SMA)
        bollingerFrame['SMA'] = data['CLOSING_TL'].rolling(window=lookback).mean()
        # Calculate the 20-period Standard Deviation (SD)
        bollingerFrame['SD'] = data['CLOSING_TL'].rolling(window=lookback).std()
        # Calculate the Upper Bollinger Band (UB) and Lower Bollinger Band (LB)
        bollingerFrame['UB'] = bollingerFrame['SMA'] + 2 * bollingerFrame['SD']
        bollingerFrame['LB'] = bollingerFrame['SMA'] - 2 * bollingerFrame['SD']
        bollingerFrame['SIGNAL+'] = np.where(data['CLOSING_TL'] < bollingerFrame['LB'], 1, 0)
        bollingerFrame['SIGNAL-'] = np.where(data['CLOSING_TL'] > bollingerFrame['UB'], 1, 0)
        return bollingerFrame


    def get_rsi(self, data, lookback = 14):
        rsiFrame = pd.DataFrame()
        ret = data['CLOSING_TL'].diff()
        up = []
        down = []
        for i in range(len(ret)):
            if ret[i] < 0:
                up.append(0)
                down.append(ret[i])
            else:
                up.append(ret[i])
                down.append(0)
        ups = pd.Series(up)
        downs = pd.Series(down).abs()
        upsEwm = ups.ewm(com = lookback - 1, adjust=False).mean()
        downsEwm = downs.ewm(com = lookback - 1, adjust=False).mean()
        rs = upsEwm/downsEwm
        rsi = 100 - (100 / (1 + rs))
        rsiFrame["RSI"] = rsi
        rsiFrame["SIGNAL+"] = np.where(rsiFrame["RSI"] < 30, 1, 0)
        rsiFrame["SIGNAL-"] = np.where(rsiFrame["RSI"] > 70, 1, 0)
        return rsiFrame


    def get_macd(self, data):
        macdFrame = pd.DataFrame()
        ema12 = data["CLOSING_TL"].ewm(span=12, adjust=False).mean()
        ema26 = data["CLOSING_TL"].ewm(span=26, adjust=False).mean()
        macdFrame["MACD"] = ema12 - ema26
        macdFrame["SIGNAL_LINE"] = macdFrame["MACD"].ewm(span=9, adjust=False).mean()
        macdFrame["SIGNAL+"] = np.where(macdFrame["MACD"] > macdFrame["SIGNAL_LINE"], 1, 0)
        macdFrame["SIGNAL-"] = np.where(macdFrame["MACD"] < macdFrame["SIGNAL_LINE"], 1, 0)
        return macdFrame


    def get_soc(self, data, kperiod = 14, dperiod = 3):
        stochasticFrame = pd.DataFrame()
        nHigh = data["HIGH_TL"].rolling(kperiod).max()
        nLow = data["LOW_TL"].rolling(kperiod).min()
        percentK = 100 * ((data["CLOSING_TL"] - nLow) / (nHigh - nLow))
        percentD = percentK.rolling(dperiod).mean()
        stochasticFrame["%D"] = percentD
        stochasticFrame["%K"] = percentK
        # IPTALLLLL xd
        return stochasticFrame


    def get_st(self, data, lookback = 10, multiplier = 3):
        high = data["HIGH_TL"]
        low = data["LOW_TL"]
        close = data["CLOSING_TL"]

        m = close.size
        dirr, trend = [1] * m, [0] * m
        long, short = [np.nan] * m, [np.nan] * m

        tr1 = pd.DataFrame(high - low)
        tr2 = pd.DataFrame(abs(high - close.shift(1)))
        tr3 = pd.DataFrame(abs(low - close.shift(1)))
        frames = [tr1, tr2, tr3]
        tr = pd.concat(frames, axis = 1, join = 'inner').max(axis = 1)
        atr = tr.ewm(lookback).mean()

        hl2 = 0.5 * (high + low)
        mAtr = multiplier * atr
        upperBand = hl2 + mAtr
        lowerBand = hl2 - mAtr

        for i in range(1, m):
            if close.iloc[i] > upperBand.iloc[i - 1]:
                dirr[i] = 1
            elif close.iloc[i] < lowerBand.iloc[i - 1]:
                dirr[i] = -1
            else:
                dirr[i] = dirr[i - 1]
                if dirr[i] > 0 and lowerBand.iloc[i] < lowerBand.iloc[i - 1]:
                    lowerBand.iloc[i] = lowerBand.iloc[i - 1]
                if dirr[i] < 0 and upperBand.iloc[i] > upperBand.iloc[i - 1]:
                    upperBand.iloc[i] = upperBand.iloc[i - 1]
            if dirr[i] > 0:
                trend[i] = long[i] = lowerBand.iloc[i]
            else:
                trend[i] = short[i] = upperBand.iloc[i]

        supertrendFrame = pd.DataFrame()
        supertrendFrame["ST"] = trend
        supertrendFrame["SUPERTrendDirection"] = dirr
        supertrendFrame["SUPERTrendLong"] = long
        supertrendFrame["SUPERTrendShort"] = short
        supertrendFrame["SIGNAL+"] = np.where(supertrendFrame["SUPERTrendDirection"] == 1, 1, 0)
        supertrendFrame["SIGNAL-"] = np.where(supertrendFrame["SUPERTrendDirection"] == 0, 1, 0)
        return supertrendFrame


    def get_adx(self, data, lookback = 14):
        high = data["HIGH_TL"]
        low = data["LOW_TL"]
        close = data["CLOSING_TL"]

        plusDM = high.diff()
        minusDM = low.diff()
        plusDM[plusDM < 0] = 0
        minusDM[minusDM > 0] = 0
        
        tr1 = pd.DataFrame(high - low)
        tr2 = pd.DataFrame(abs(high - close.shift(1)))
        tr3 = pd.DataFrame(abs(low - close.shift(1)))
        frames = [tr1, tr2, tr3]
        tr = pd.concat(frames, axis = 1, join = 'inner').max(axis = 1)
        atr = tr.rolling(lookback).mean()
        
        plusDI = 100 * (plusDM.ewm(alpha = 1/lookback).mean() / atr)
        minusDI = abs(100 * (minusDM.ewm(alpha = 1/lookback).mean() / atr))
        dx = (abs(plusDI - minusDI) / abs(plusDI + minusDI)) * 100
        adx = ((dx.shift(1) * (lookback - 1)) + dx) / lookback
        adx_smooth = adx.ewm(alpha = 1/lookback).mean()
        adxFrame = pd.DataFrame()
        adxFrame["ADX"] = adx_smooth
        adxFrame["PLUS_DI"] = plusDI
        adxFrame["MINUS_DI"] = minusDI
        adxFrame["SIGNAL+"] = np.where(np.logical_and(adxFrame["PLUS_DI"] > adxFrame["MINUS_DI"], adxFrame["ADX"] < 25), 1, 0)
        adxFrame["SIGNAL-"] = np.where(np.logical_and(adxFrame["PLUS_DI"] < adxFrame["MINUS_DI"], adxFrame["ADX"] > 25), 1, 0)
        return adxFrame


class AdvancedAnalysis:
    def __init__(self, analysis=None, fuzzySignal=None, linearPrediction=None):
        self.analysis = analysis
        self.fuzzySignal = fuzzySignal
        self.linearPrediction = linearPrediction


    def do_analysis(self):
        self.fuzzySignal = self.fuzzy_logic_buy_signal()
        self.linearPrediction = self.linear_regression_signal()


    def deprecated_normalize(self, data):
        # --- (Deprecated min-max normalization) ---
        maxData = data.max(axis=0)
        minData = data.min(axis=0)
        return (data - minData) / (maxData - minData)


    def normalize(self, data):
        mean = np.mean(data)
        stdDev = np.std(data)
        return (data - mean) / stdDev


    def normalize_sma(self, sma):
        if sma['SIGNAL+'].diff().iloc[-1] == 1:
            return 1
        elif sma['SIGNAL-'].diff().iloc[-1] == 1:
            return 0
        else:
            return self.normalize(self.analysis.raw['CLOSING_TL'].sub(sma["SMA20"])).iloc[-1] - 0.3 # magic


    def normalize_ema(self, ema):
        if ema['SIGNAL+'].diff().iloc[-1] == 1:
            return 1
        elif ema['SIGNAL-'].diff().iloc[-1] == 1:
            return 0
        else:
            return self.normalize(self.analysis.raw['CLOSING_TL'].sub(ema["EMA20"])).iloc[-1]


    def normalize_bbs(self, bbs):
        if bbs['SIGNAL+'].diff().iloc[-1] == 1:
            return 1
        elif bbs['SIGNAL-'].diff().iloc[-1] == 1:
            return 0
        else:
            return 1 - self.normalize(self.analysis.raw['CLOSING_TL'].sub(bbs["LB"])).iloc[-1]


    def normalize_rsi(self, rsi):
        if rsi['SIGNAL+'].iloc[-1] == 1:
            return 1
        elif rsi['SIGNAL-'].iloc[-1] == 1:
            return 0
        else:
            return self.normalize(rsi['RSI']).iloc[-1]


    def normalize_macd(self, macd):
        if macd['SIGNAL+'].diff().iloc[-1] == 1:
            return 1
        elif macd['SIGNAL-'].diff().iloc[-1] == 1:
            return 0
        else:
            return self.normalize(macd['MACD'].sub(macd['SIGNAL_LINE'], axis=0)).iloc[-1]


    def normalize_st(self, st):
        if st['SIGNAL+'].diff().iloc[-1] == 1:
            return 1
        elif st['SIGNAL-'].diff().iloc[-1] == 1:
            return 0
        elif st['SIGNAL+'].iloc[-1] == 1:
            return 0.7
        else:
            return 0.3


    def normalize_adx(self, adx):
        if adx['SIGNAL+'].iloc[-1] == 1:
            return 1
        elif adx['SIGNAL-'].iloc[-1] == 1:
            return 0
        else:
            return self.normalize(adx['ADX']).iloc[-1]


    def fuzzy_logic_buy_signal(self):
        smaIndicator = self.normalize_sma(self.analysis.sma)
        emaIndicator = self.normalize_ema(self.analysis.ema)
        bbsIndicator = self.normalize_bbs(self.analysis.bbs)
        rsiIndicator = self.normalize_rsi(self.analysis.rsi)
        macdIndicator = self.normalize_macd(self.analysis.macd)
        stIndicator = self.normalize_st(self.analysis.st)
        adxIndicator = self.normalize_adx(self.analysis.adx)        
        
        finalResult = 0.10 * smaIndicator \
        + 0.15 * emaIndicator \
        + 0.10 * bbsIndicator \
        + 0.20 * rsiIndicator \
        + 0.20 * macdIndicator \
        + 0.15 * stIndicator \
        + 0.10 * adxIndicator

        return finalResult


    def linear_regression_signal(self):
        from sklearn.model_selection import train_test_split
        from sklearn.metrics import mean_absolute_error
        from sklearn.preprocessing import MinMaxScaler
        from sklearn.linear_model import LinearRegression

        prices = self.analysis.raw['CLOSING_TL']
        x_training, x_test, y_training, y_test = train_test_split(self.analysis.raw[["CLOSING_TL", "VOLUME_TL", "CLOSING_USD", "VOLUME_USD"]].values, prices, test_size=0.6)
        scaler = MinMaxScaler()
        scaler.fit(x_training)
        x_training = scaler.transform(x_training)
        scaler.fit(x_test)
        x_test = scaler.transform(x_test)

        model = LinearRegression()
        model.fit(x_training, y_training)
        # r_sq = model.score(x_test, y_test)

        b = scaler.transform(self.analysis.raw[["CLOSING_TL", "VOLUME_TL", "CLOSING_USD", "VOLUME_USD"]].values)
        
        prediction = model.predict(x_test)
        graph = pd.DataFrame(y_test, columns=["Reel Degerler"])
        graph['Tahmini Degerler'] = prediction

        # from matplotlib import pyplot as plt
        # plt.scatter(y_test, prediction, c=np.random.rand(143), alpha=0.5)
        # plt.show()
        return prediction[-1]










# scraper = StockInfoScraper()
# rawData = scraper.get_stock_info(symbol = "MGROS", start_date="01-01-2024", end_date="15-12-2024")
# analiz = Analysis()
# analiz.do_analysis(rawData)
# aanaliz = AdvancedAnalysis(analiz)
# print(aanaliz.fuzzySignal)
# print(aanaliz.linearPrediction)


# from matplotlib import pyplot as plt
# plt.plot(data["CLOSING_TL"], label="Fiyat", color="black")
# plt.plot(adxFrame['ADX'], label="ADX", color="yellow")
# plt.plot(adxFrame['PLUS_DI'], label="DI+", color="blue")
# plt.plot(adxFrame['MINUS_DI'], label="DI-", color="cyan")
# plt.plot(adxFrame["SIGNAL+"] * 100, label="Al  Sinyal", color="green", linewidth=2)
# plt.plot(adxFrame["SIGNAL-"] * 100, label="Sat Sinyal", color="red", linewidth=2)
# plt.legend(loc = 'upper left')
# plt.show()
# print(categoriesAndSymbols)


# print(analiz.sma['SIGNAL'])
# from matplotlib import pyplot as plt
# plt.plot(smaFrame['SMA20'], color='blue')
# plt.plot(smaFrame['SMA50'], color='red')
# plt.plot(smaFrame['SIGNAL'], color='black')
# plt.show()

# print(scrapedData.columns)
# print(analiz.sma)
# print(analiz.ema)
# print(analiz.bollinger)
# print(analiz.rsi)
# print(analiz.stochasticOscillator)
# print(analiz.st)
# print(analiz.adx)
# 
# import matplotlib.pyplot as plt
# plt.plot(analiz.st['CLOSING_TL'], linewidth = 2)
# plt.plot(analiz.st['ST'], color = 'green', linewidth = 2, label = 'ST UPTREND')
# plt.plot(analiz.st['SUPERTrendShort'], color = 'r', linewidth = 2, label = 'ST DOWNTREND')
# plt.legend(loc = 'upper left')
# plt.show()
# print(get_financial_ratios("GESAN"))
# print(stockData1.get_data(symbols=["THYAO"], start_date="01-01-2021", end_date="01-01-2022", save_to_excel=True))
# RSI, HARAKETLI ORTALAMA, HACIM, MAD ve BOLLINGER BANTLARI
# Trend grafigi -> linear regression for peaks and lows
