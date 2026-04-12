import streamlit as st
import pandas as pd
import yfinance as yf
import time
from ta.momentum import RSIIndicator
from ta.volume import OnBalanceVolumeIndicator

st.set_page_config(layout="wide")
st.title("🚀 PRO AI TRADING TERMINAL (PRO LEVEL)")

# ================= SETTINGS =================

ALL_STOCKS = [
    "TATASTEEL.NS","HINDALCO.NS","SBIN.NS","ICICIBANK.NS",
    "RELIANCE.NS","INFY.NS","LT.NS","AXISBANK.NS","ITC.NS","ONGC.NS"
]

# ================= FUNCTIONS =================

@st.cache_data(ttl=300)
def load_data(stock):
    try:
        df = yf.download(stock, period="6mo", progress=False)
        if df is None or df.empty:
            return None

        close = df["Close"]

        df["MA20"] = close.rolling(20).mean()
        df["MA50"] = close.rolling(50).mean()
        df["MA200"] = close.rolling(200).mean()
        df["RSI"] = RSIIndicator(close).rsi()
        df["OBV"] = OnBalanceVolumeIndicator(close, df["Volume"]).on_balance_volume()

        return df
    except:
        return None


def calculate_score(df):
    if df is None or len(df) < 50:
        return 0

    s = 0
    l = df.iloc[-1]

    if l["MA20"] > l["MA50"] > l["MA200"]:
        s += 3

    if l["RSI"] > 50:
        s += 2

    if df["RSI"].iloc[-1] > df["RSI"].iloc[-5]:
        s += 1

    if df["OBV"].iloc[-1] > df["OBV"].iloc[-10]:
        s += 2

    return s


# 🔥 Breakout Detection
def breakout_signal(df):
    high_10 = df["High"].rolling(10).max().iloc[-2]
    today_close = df["Close"].iloc[-1]

    return today_close > high_10


# 🧠 Win Probability
def win_probability(score):
    return min(95, 40 + score * 5)


# 📊 Simple Backtest
def backtest(df):
    wins = 0
    total = 0

    for i in range(50, len(df)-5):
        window = df.iloc[:i]

        if breakout_signal(window):
            entry = window["Close"].iloc[-1]
            future = df.iloc[i:i+5]

            if future["Close"].max() > entry * 1.05:
                wins += 1
            total += 1

    if total == 0:
        return 0

    return round((wins / total) * 100, 2)


# 📈 Trade Plan
def trade_plan(df):
    l = df.iloc[-1]

    entry = round(l["Close"], 2)
    sl = round(df["Low"].rolling(10).min().iloc[-1], 2)

    risk = entry - sl
    target = round(entry + risk * 2, 2)

    return entry, sl, target


def decision(score, breakout):
    if breakout and score >= 8:
        return "🔥 BUY NOW"
    elif score >= 8:
        return "⏳ WAIT BREAKOUT"
    elif score >= 6:
        return "👀 WATCH"
    else:
        return "❌ AVOID"


# ================= UI =================

st.sidebar.header("⚙️ Controls")
selected_stocks = st.sidebar.multiselect("Stocks", ALL_STOCKS, default=ALL_STOCKS)
run = st.sidebar.button("▶ Run Scan")

# ================= MAIN =================

if run:

    results = []

    for stock in selected_stocks:
        df = load_data(stock)

        if df is None:
            continue

        score = calculate_score(df)
        breakout = breakout_signal(df)
        prob = win_probability(score)
        bt = backtest(df)

        entry, sl, target = trade_plan(df)
        price = round(df["Close"].iloc[-1], 2)

        dec = decision(score, breakout)

        results.append({
            "Stock": stock,
            "Decision": dec,
            "Price": price,
            "Score": score,
            "Win %": prob,
            "Backtest %": bt,
            "Entry": entry,
            "SL": sl,
            "Target": target,
            "Breakout": breakout
        })

    df_out = pd.DataFrame(results)

    if not df_out.empty:
        df_out = df_out.sort_values("Score", ascending=False)

        st.subheader("🔥 TRADE SIGNALS")
        st.dataframe(df_out, use_container_width=True)

        top = df_out[df_out["Decision"] == "🔥 BUY NOW"]

        st.subheader("🚀 IMMEDIATE BUYS")
        st.dataframe(top, use_container_width=True)

    else:
        st.warning("No data found")
