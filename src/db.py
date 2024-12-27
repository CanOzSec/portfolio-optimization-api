import sqlite3
import os
import json
from core import StockInfoScraper, Stock, Analysis, AdvancedAnalysis
from symbols import categoriesAndSymbols
import time


class Database:
    def __init__(self):
        srcPath = os.path.dirname(os.path.abspath(__file__))
        self.dbPath = os.path.abspath(os.path.join(srcPath, "..", "database.db"))
        self.connection = sqlite3.connect(self.dbPath)
        self.cursor = self.connection.cursor()


    def migrate(self):
        stocksCacheQ = "CREATE TABLE stocks(name, category, financialStatement, financialRatios, rawData)"
        analysisCacheQ = "CREATE TABLE analysis(stockName, sma, ema, bbs, rsi, macd, soc, st, adx)"
        aanalysisCacheQ = "CREATE TABLE advanced_analysis(stockName, fuzzySignal, linearPrediction)"
        self.cursor.execute(stocksCacheQ)
        self.cursor.execute(analysisCacheQ)
        self.cursor.execute(aanalysisCacheQ)


    def insertData(self, stock, analysis, advancedAnalysis):
        insertStockQ = "INSERT INTO stocks VALUES(?, ?, ?, ?, ?)"
        insertAnalysisQ = "INSERT INTO analysis VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)"
        insertAAnalysisQ = "INSERT INTO advanced_analysis VALUES(?, ?, ?)"
        self.cursor.execute(insertStockQ, (stock.name, stock.category, stock.financialStatement, stock.financialRatios, stock.rawData.to_json()))
        self.cursor.execute(insertAnalysisQ, (stock.name, analysis.sma.to_json(), analysis.ema.to_json(), analysis.bbs.to_json(), analysis.rsi.to_json(), analysis.macd.to_json(), analysis.soc.to_json(), analysis.st.to_json(), analysis.adx.to_json()))
        self.cursor.execute(insertAAnalysisQ, (stock.name, advancedAnalysis.fuzzySignal, advancedAnalysis.linearPrediction))
        self.connection.commit()


    def updateData(self, stock, analysis, advancedAnalysis):
        updateStockQ = "UPDATE FROM stocks SET financialStatement=?, financialRatios=?, rawData=? WHERE name=?"
        updateAnalysisQ = "UPDATE FROM analysis SET sma=?, ema=?, bbs=?, rsi=?, macd=?, soc=?, st=?, adx=? WHERE stockName=?"
        updateAAnalysisQ = "UPDATE FROM advanced_analysis SET fuzzySignal=?, linearPrediction=? WHERE stockName=?"
        self.cursor.execute(updateStockQ, (stock.financialStatement, stock.financialRatios, stock.rawData.to_json(), stock.name))
        self.cursor.execute(updateAnalysisQ, (analysis.sma.to_json(), analysis.ema.to_json(), analysis.bbs.to_json(), analysis.rsi.to_json(), analysis.macd.to_json(), analysis.soc.to_json(), analysis.st.to_json(), analysis.adx.to_json(), stock.name))
        self.cursor.execute(updateAAnalysisQ, (advancedAnalysis.fuzzySignal, advancedAnalysis.linearPrediction, stock.name))
        self.connection.commit()


    def selectStock(self, symbol):
        selectStockQ = "SELECT * FROM stocks WHERE name = ?"
        self.cursor.execute(selectStockQ, symbol)
        res = self.cursor.fetchall()
        stock = Stock(res[0][0], res[0][1], res[0][2], res[0][3], res[0][4])
        return stock


    def selectAnalysis(self, symbol):
        selectAnalysisQ = "SELECT * FROM analysis WHERE stockName = ?"
        self.cursor.execute(selectAnalysisQ, symbol)
        res = self.cursor.fetchall()
        stock = self.selectStock(symbol)
        analysis = Analysis(res[0][1], res[0][2], res[0][3], res[0][4], res[0][5], res[0][6], res[0][7], res[0][8], stock.rawData)
        return analysis


    def selectAAnalysis(self, symbol):
        selectAAnalysisQ = "SELECT * FROM advanced_analysis WHERE stockName = ?"
        self.cursor.execute(selectAAnalysisQ, symbol)
        res = self.cursor.fetchall()
        advancedAnalysis = AdvancedAnalysis(None, res[0][1], res[0][2])
        return advancedAnalysis

    def selectSymbols(self):
        selectSymbolsQ = "SELECT name, financialRatios, rawData FROM stocks"
        self.cursor.execute(selectSymbolsQ)
        res = self.cursor.fetchall()
        return [[res[i][0], json.loads(res[i][1]), json.loads(res[i][2])['CLOSING_TL'].popitem()[1]] for i in range(len(res))]


class StockDbOperations:
    def __init__(self):
        self.db = Database()


    def prepare_stock(self, name, category):
        scraper = StockInfoScraper()
        rawData = scraper.get_stock_info(symbol = name, start_date="01-01-2024")
        financialStatement = scraper.get_financial_statement(name)
        financialRatios = scraper.get_financial_ratios(name)
        finalStock = Stock(name, category, json.dumps(financialStatement), json.dumps(financialRatios), rawData)
        finalAnalysis = Analysis()
        finalAnalysis.do_analysis(rawData)
        finalAAnalysis = AdvancedAnalysis(finalAnalysis)
        finalAAnalysis.do_analysis()
        self.db.insertData(finalStock, finalAnalysis, finalAAnalysis)


    def update_stock(self, name, category):
        scraper = StockInfoScraper()
        rawData = scraper.get_stock_info(symbol = name, start_date="01-01-2024")
        financialStatement = scraper.get_financial_statement(name)
        financialRatios = scraper.get_financial_ratios(name)
        finalStock = Stock(name, category, json.dumps(financialStatement), json.dumps(financialRatios), rawData)
        finalAnalysis = Analysis()
        finalAnalysis.do_analysis(rawData)
        self.db.updataData(finalStock, finalAnalysis)


    def prepare_stocks(self):
        analyzedSymbols = []
        for category in categoriesAndSymbols:
            for symbol in categoriesAndSymbols[category]:
                if symbol not in analyzedSymbols:
                    try:
                        print(f"Sirket: {symbol}")
                        self.prepare_stock(symbol, category)
                    except:
                        time.sleep(5)
                        print(f"Sirket bilgileri getirilemiyor: {symbol}")
                    analyzedSymbols.append(symbol)


    def update_stocks(self):
        analyzedSymbols = []
        for category in categoriesAndSymbols:
            for symbol in categoriesAndSymbols[category]:
                if symbol not in analyzedSymbols:
                    try:
                        self.update_stock(symbol, category)
                    except:
                        time.sleep(5)
                        print(f"Sirket bilgileri getirilemiyor: {symbol}")
                    analyzedSymbols.append(symbol)


# db = Database()
# db.migrate()
# print(db.selectSymbols())
# StockDbOperations().prepare_stocks()

