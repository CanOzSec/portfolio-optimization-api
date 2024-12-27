from flask import Flask, jsonify
from db import Database


app = Flask(__name__)


@app.route("/")
def main_page():
    return "F to pay respects"


@app.route("/api/stock/<symbol>")
def get_stock_data(symbol):
    db = Database()
    stock = db.selectStock([symbol])
    return jsonify([stock.name, stock.category, stock.financialStatement, stock.financialRatios, stock.rawData])


@app.route("/api/analysis/<symbol>")
def get_analysis_data(symbol):
    db = Database()
    analysis = db.selectAnalysis([symbol])
    return jsonify([analysis.sma, analysis.ema, analysis.bbs, analysis.rsi, analysis.macd, analysis.soc, analysis.st, analysis.adx])


@app.route("/api/advanced-analysis/<symbol>")
def get_advanced_analysis(symbol):
    db = Database()
    analysis = db.selectAAnalysis([symbol])
    return jsonify([analysis.fuzzySignal, analysis.linearPrediction])


@app.route("/api/symbols")
def get_symbols():
    db = Database()
    return jsonify(db.selectSymbols())

