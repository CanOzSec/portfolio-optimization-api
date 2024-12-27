from db import Database
import json
from core import Analysis, AdvancedAnalysis
from symbols import categoriesAndSymbols
import pandas as pd


class Test:
    def __init__(self):
        pass


    def test_stock(self, analysis, testTime):
        waybackAnalysis = Analysis(analysis.sma[:-testTime], analysis.ema[:-testTime], analysis.bbs[:-testTime], analysis.rsi[:-testTime], analysis.macd[:-testTime], analysis.soc[:-testTime], analysis.st[:-testTime], analysis.adx[:-testTime], analysis.raw[:-testTime])
        waybackAAnalysis = AdvancedAnalysis(waybackAnalysis)
        waybackAAnalysis.do_analysis()
        signal = waybackAAnalysis.fuzzySignal
        oldPrice = waybackAnalysis.raw['CLOSING_TL'].iloc[-1]
        curPrice = analysis.raw['CLOSING_TL'].iloc[-1]
        change = ((curPrice - oldPrice) / oldPrice) * 100  
        return signal, change


    def test_profits(self, testTime=60):
        db = Database()
        analyzedSymbols = []
        boughtSymbols = []
        soldSymbols = []
        holdSymbols = []
        positivePredictions = []
        negativePredictions = []
        truePositive = 0
        falsePositive = 0
        trueNegative = 0
        falseNegative = 0

        for category in categoriesAndSymbols:
            for symbol in categoriesAndSymbols[category]:
                if symbol not in analyzedSymbols:
                    try:
                        stock = db.selectStock([symbol])
                        if float(json.loads(stock.financialStatement)['value'][0]['value2']) > 7000000000:
                            analysis = db.selectAnalysis([symbol])
                            signal, change = self.test_stock(analysis, testTime)
                            print(signal, change)
                            if signal > 0.4:
                                boughtSymbols.append(symbol)
                                if change > 0:
                                    truePositive += 1
                                    positivePredictions.append({symbol:change, "signal":signal})
                                else:
                                    falsePositive += 1
                                    negativePredictions.append({symbol:change, "signal":signal})
                            if signal < 0.3:
                                soldSymbols.append(symbol)
                                if change > 0:
                                    falseNegative += 1
                                    negativePredictions.append({symbol:change, "signal":signal})
                                else:
                                    trueNegative += 1
                                    positivePredictions.append({symbol:change, "signal":signal})
                            else:
                                holdSymbols.append(symbol)
                    except:
                        pass
        print(len(positivePredictions), positivePredictions)
        print("------------------\n"*4)
        print(len(negativePredictions), negativePredictions)

        import seaborn as sns
        import matplotlib.pyplot as plt 
        cm = [[truePositive, falseNegative], [falsePositive, trueNegative]]
        sns.heatmap(cm, annot=True, cmap='Blues')
        plt.show()




t = Test()
t.test_profits()