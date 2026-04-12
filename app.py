import streamlit as st
import pandas as pd
import yfinance as yf
import requests
from ta.momentum import RSIIndicator
from ta.volume import OnBalanceVolumeIndicator
from ta.volatility import AverageTrueRange
from textblob import TextBlob

# ================= PAGE =================
st.set_page_config(layout="wide")
st.title("🚀 AI TRADING DASHBOARD (PRO SYSTEM)")

# ================= SIDEBAR =================
st.sidebar.header("⚙️ Controls")

scan_btn = st.sidebar.button("📊 Swing Scan")
backtest_btn = st.sidebar.button("📈 Backtest")
intraday_btn = st.sidebar.button("⚡ Intraday 5m Scanner")

# ================= STOCK UNIVERSE =================
ALL_STOCKS = {
    "RELIANCE.NS":"ENERGY","ONGC.NS":"ENERGY",
    "SBIN.NS":"BANK","ICICIBANK.NS":"BANK","HDFCBANK.NS":"BANK",
    "INFY.NS":"IT","TCS.NS":"IT",
    "LT.NS":"INFRA","ULTRACEMCO.NS":"INFRA",
    "TATASTEEL.NS":"METAL","HINDALCO.NS":"METAL",
    "ITC.NS":"FMCG","HINDUNILVR.NS":"FMCG"
}

# ================= DATA =================
@st.cache_data(ttl=300)
def load_data(stock):
    try:
        df = yf.download(stock, period="6mo", progress=False)
        if df.empty:
            return None

        close = df["Close"]

        df["MA20"] = close.rolling(20).mean()
        df["MA50"] = close.rolling(50).mean()
        df["MA200"] = close.rolling(200).mean()

        df["RSI"] = RSIIndicator(close).rsi()
        df["OBV"] = OnBalanceVolumeIndicator(close, df["Volume"]).on_balance_volume()

        atr = AverageTrueRange(df["High"], df["Low"], close)
        df["ATR"] = atr.average_true_range()

        return df
    except:
        return None

# ================= NEWS =================
def news_sentiment(stock):
    try:
        name = stock.replace(".NS","")
        url = f"https://news.google.com/rss/search?q={name}+stock"
        r = requests.get(url, timeout=5)
        text = r.text[:1500]
        return TextBlob(text).sentiment.polarity * 10
    except:
        return 0

# ================= SCORE =================
def score(df, news):
    if df is None or len(df) < 50:
        return 0

    l = df.iloc[-1]
    s = 0

    if l["MA20"] > l["MA50"] > l["MA200"]:
        s += 3
    if 50 < l["RSI"] < 70:
        s += 2
    if df["OBV"].iloc[-1] > df["OBV"].iloc[-10]:
        s += 2

    prev_high = df["High"].rolling(5).max().iloc[-2]
    if l["Close"] > prev_high:
        s += 2

    s += news
    return round(s,2)

# ================= TRADE PLAN =================
def trade_plan(df):
    l = df.iloc[-1]
    entry = round(l["Close"],2)
    sl = round(entry - (1.5 * l["ATR"]),2)
    target = round(entry + (entry - sl) * 2,2)
    return entry, sl, target

# ================= BACKTEST =================
def backtest(df):
    trades = []

    for i in range(50, len(df)-5):
        sub = df.iloc[:i]
        l =
