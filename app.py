import streamlit as st
import pandas as pd
import yfinance as yf
import datetime
import requests
from ta.momentum import RSIIndicator
from ta.volume import OnBalanceVolumeIndicator
from textblob import TextBlob

st.set_page_config(layout="wide")
st.title("🚀 PRO AI TRADING TERMINAL")

# ================= SETTINGS =================
STOCKS = [
    "TATASTEEL.NS","HINDALCO.NS","SBIN.NS",
    "ICICIBANK.NS","RELIANCE.NS","INFY.NS"
]

SECTORS = {
    "TATASTEEL.NS": "METAL",
    "HINDALCO.NS": "METAL",
    "SBIN.NS": "BANK",
    "ICICIBANK.NS": "BANK",
    "RELIANCE.NS": "ENERGY",
    "INFY.NS": "IT"
}

TELEGRAM_TOKEN = "YOUR_TOKEN"
CHAT_ID = "YOUR_CHAT_ID"

# ================= FUNCTIONS =================

def send_alert(msg):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg})
    except:
        pass


@st.cache_data(ttl=300)
def load_data(stock):
    df = yf.download(stock, period="6mo", progress=False)

    df["MA20"] = df["Close"].rolling(20).mean()
    df["MA50"] = df["Close"].rolling(50).mean()
    df["MA200"] = df["Close"].rolling(200).mean()

    df["RSI"] = RSIIndicator(df["Close"]).rsi()
    df["OBV"] = OnBalanceVolumeIndicator(df["Close"], df["Volume"]).on_balance_volume()

    return df


def news_sentiment(stock):
    try:
        text = stock.replace(".NS", "")
        analysis = TextBlob(text)
        return analysis.sentiment.polarity
    except:
        return 0


def calculate_score(df, stock):
    s = 0
    l = df.iloc[-1]

    # Trend alignment
    if l["MA20"] > l["MA50"] > l["MA200"]:
        s += 3

    # Near high
    high = df["High"].rolling(252).max().iloc[-1]
    if l["Close"] > 0.75 * high:
        s += 2

    # RSI sweet spot
    if 50 < l["RSI"] < 65:
        s += 1

    # RSI rising
    if df["RSI"].iloc[-1] > df["RSI"].iloc[-5]:
        s += 1

    # Volume contraction
    avg_vol = df["Volume"].rolling(20).mean().iloc[-1]
    if l["Volume"] < avg_vol:
        s += 1

    # OBV rising
    if df["OBV"].iloc[-1] > df["OBV"].iloc[-10]:
        s += 2

    # News boost
    sentiment = news_sentiment(stock)
    if sentiment > 0:
        s += 1

    return s


# ================= UI =================

run = st.button("▶ Run Scan")
auto = st.checkbox("Auto Refresh (30s)")

if run or auto:
    results = []
    sector_count = {}

    for stock in STOCKS:
        df = load_data(stock)
        s = calculate_score(df, stock)
        price = round(df["Close"].iloc[-1], 2)

        sector = SECTORS.get(stock, "OTHER")
        sector_count[sector] = sector_count.get(sector, 0) + (1 if s >= 8 else 0)

        if s >= 8:
            msg = f"🔥 {stock} | ₹{price} | Score: {s}"
            send_alert(msg)

        results.append({
            "Stock": stock,
            "Price": price,
            "Score": s,
            "Sector": sector
        })

    df_out = pd.DataFrame(results).sort_values("Score", ascending=False)

    st.subheader("📊 Scanner Results")
    st.dataframe(df_out, use_container_width=True)

    st.subheader("🏭 Sector Strength")
    st.write(sector_count)

    st.success("Scan Completed")

    if auto:
        import time
        time.sleep(30)
        st.rerun()
