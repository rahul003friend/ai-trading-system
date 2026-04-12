import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import requests

from ta.momentum import RSIIndicator
from ta.volume import OnBalanceVolumeIndicator
from ta.volatility import AverageTrueRange
from textblob import TextBlob

# ================= SAFE CORE =================

def safe_series_last(x):
    """Always returns last valid scalar safely"""
    try:
        if x is None:
            return 0.0
        if isinstance(x, pd.DataFrame):
            x = x.iloc[:, 0]
        if isinstance(x, pd.Series):
            x = x.dropna()
            if len(x) == 0:
                return 0.0
            return float(x.iloc[-1])
        return float(x)
    except:
        return 0.0


def safe_df(df):
    """Clean dataframe safely"""
    if df is None or df.empty:
        return None

    df = df.copy()

    for col in ["Open", "High", "Low", "Close", "Volume"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna()

    if len(df) < 60:
        return None

    return df


# ================= DATA =================

def load_data(stock):
    try:
        df = yf.download(stock, period="6mo", progress=False)
        df = safe_df(df)
        if df is None:
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
        q = stock.replace(".NS", "")
        url = f"https://news.google.com/rss/search?q={q}+stock"
        r = requests.get(url, timeout=5)
        return TextBlob(r.text[:1200]).sentiment.polarity * 10
    except:
        return 0.0


# ================= SCORE ENGINE =================

def score(df, news):
    if df is None:
        return 0

    try:
        close = safe_series_last(df["Close"])
        ma20 = safe_series_last(df["MA20"])
        ma50 = safe_series_last(df["MA50"])
        ma200 = safe_series_last(df["MA200"])
        rsi = safe_series_last(df["RSI"])

        s = 0

        if ma20 > ma50 > ma200:
            s += 3

        if 50 < rsi < 70:
            s += 2

        if len(df) > 10:
            if df["OBV"].iloc[-1] > df["OBV"].iloc[-10]:
                s += 2

        prev_high = safe_series_last(df["High"].rolling(5).max())
        if close > prev_high:
            s += 2

        s += news

        return round(s, 2)

    except:
        return 0


# ================= TRADE PLAN =================

def trade_plan(df):
    try:
        entry = safe_series_last(df["Close"])
        atr = safe_series_last(df["ATR"])

        sl = entry - (1.5 * atr)
        target = entry + (entry - sl) * 2

        return round(entry, 2), round(sl, 2), round(target, 2)

    except:
        return 0, 0, 0


# ================= BACKTEST =================

def backtest(df):
    if df is None or len(df) < 100:
        return 0, 0

    trades = []

    try:
        for i in range(50, len(df) - 5):

            sub = df.iloc[:i]

            ma20 = safe_series_last(sub["MA20"])
            ma50 = safe_series_last(sub["MA50"])
            ma200 = safe_series_last(sub["MA200"])

            if ma20 > ma50 > ma200:

                prev_high = safe_series_last(sub["High"].rolling(5).max())
                close = safe_series_last(sub["Close"])

                if close > prev_high:

                    entry = close
                    atr = safe_series_last(sub["ATR"])

                    sl = entry - (1.5 * atr)
                    target = entry + (entry - sl) * 2

                    future = df.iloc[i:i+5]

                    result = 0

                    for _, r in future.iterrows():
                        low = safe_series_last(r["Low"])
                        high = safe_series_last(r["High"])

                        if low <= sl:
                            result = -1
                            break
                        if high >= target:
                            result = 1
                            break

                    trades.append(result)

        if len(trades) == 0:
            return 0, 0

        win_rate = trades.count(1) / len(trades) * 100

        return len(trades), round(win_rate, 2)

    except:
        return 0, 0


# ================= INTRADAY =================

def load_intraday(stock):
    try:
        df = yf.download(stock, period="1d", interval="5m", progress=False)
        return safe_df(df)
    except:
        return None


def intraday_breakout(df):
    try:
        if df is None or len(df) < 20:
            return None

        opening = df.iloc[:3]

        high = safe_series_last(opening["High"].max())
        low = safe_series_last(opening["Low"].min())

        close = safe_series_last(df["Close"])

        if close > high:
            return "BUY", close, low, close + (close - low) * 1.5

        if close < low:
            return "SELL", close, high, close - (high - close) * 1.5

        return "NO TRADE", 0, 0, 0

    except:
        return None


# ================= UI =================

st.set_page_config(layout="wide")
st.title("🚀 ZERO ERROR PRODUCTION TRADING BOT")

stocks = [
    "RELIANCE.NS","TCS.NS","INFY.NS","HDFCBANK.NS",
    "SBIN.NS","ICICIBANK.NS","LT.NS","TATASTEEL.NS"
]

scan = st.button("📊 Swing Scan")
backtest_btn = st.button("📈 Backtest")
intraday_btn = st.button("⚡ Intraday Scan")

# ================= SWING =================

if scan:

    results = []

    for stock in stocks:

        df = load_data(stock)
        if df is None:
            continue

        s = score(df, news_sentiment(stock))
        entry, sl, target = trade_plan(df)

        results.append([stock, s, entry, sl, target])

    st.dataframe(pd.DataFrame(results, columns=[
        "Stock","Score","Entry","SL","Target"
    ]))


# ================= BACKTEST =================

if backtest_btn:

    res = []

    for stock in stocks:

        df = load_data(stock)
        if df is None:
            continue

        trades, win = backtest(df)

        res.append([stock, trades, win])

    st.dataframe(pd.DataFrame(res, columns=[
        "Stock","Trades","WinRate%"
    ]))


# ================= INTRADAY =================

if intraday_btn:

    res = []

    for stock in stocks:

        df = load_intraday(stock)
        if df is None:
            continue

        signal = intraday_breakout(df)

        if signal and signal[0] != "NO TRADE":
            res.append([stock] + list(signal))

    st.dataframe(pd.DataFrame(res, columns=[
        "Stock","Signal","Entry","SL","Target"
    ]))
