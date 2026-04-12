import streamlit as st
import pandas as pd
import yfinance as yf
import time
import requests
from ta.momentum import RSIIndicator
from ta.volume import OnBalanceVolumeIndicator
from ta.volatility import AverageTrueRange
from textblob import TextBlob

st.set_page_config(layout="wide")
st.title("🚀 AI TRADING TERMINAL — SMART MONEY TRACKER")

# ================= STOCK UNIVERSE =================
ALL_STOCKS = {
    "RELIANCE.NS":"ENERGY","ONGC.NS":"ENERGY","BPCL.NS":"ENERGY",
    "SBIN.NS":"BANK","TANLA.NS":"BANK","HDFCBANK.NS":"BANK",
    "AXISBANK.NS":"BANK","KOTAKBANK.NS":"BANK",
    "INFY.NS":"IT","TCS.NS":"IT","WIPRO.NS":"IT",
    "LT.NS":"INFRA","ULTRACEMCO.NS":"INFRA",
    "TATASTEEL.NS":"METAL","HINDALCO.NS":"METAL","JSWSTEEL.NS":"METAL",
    "ITC.NS":"FMCG","HINDUNILVR.NS":"FMCG",
    "BHARTIARTL.NS":"TELECOM",
    "ADANIENT.NS":"ADANI","ADANIPORTS.NS":"ADANI",
    "POWERGRID.NS":"POWER","NTPC.NS":"POWER"
}

# ================= DATA =================
@st.cache_data(ttl=300)
def load_data(stock):
    for _ in range(3):
        try:
            df = yf.download(stock, period="6mo", interval="1d", progress=False)

            if df is None or df.empty:
                time.sleep(1)
                continue

            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

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
            time.sleep(1)

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

    if df["RSI"].iloc[-1] > df["RSI"].iloc[-5]:
        s += 1

    if df["OBV"].iloc[-1] > df["OBV"].iloc[-10]:
        s += 2

    prev_high = df["High"].rolling(5).max().iloc[-2]
    if l["Close"] > prev_high:
        s += 2

    s += news

    return round(s,2)

# ================= TRADE =================
def trade_plan(df):
    l = df.iloc[-1]

    entry = round(l["Close"], 2)
    sl = round(entry - (1.5 * l["ATR"]), 2)

    risk = entry - sl
    target = round(entry + risk * 2, 2)

    return entry, sl, target

# ================= MAIN =================
run = st.button("▶ Scan Market")

if run:

    results = []
    sector_power = {}

    for stock, sector in ALL_STOCKS.items():

        st.write(f"📡 {stock}")

        df = load_data(stock)

        if df is None or df.empty:
            continue

        news = news_sentiment(stock)
        s = score(df, news)

        entry, sl, target = trade_plan(df)
        price = round(df["Close"].iloc[-1],2)

        results.append({
            "Stock": stock,
            "Sector": sector,
            "Score": s,
            "Price": price,
            "Entry": entry,
            "SL": sl,
            "Target": target
        })

        # Sector strength
        sector_power[sector] = sector_power.get(sector, 0) + s

    df_out = pd.DataFrame(results)

    # 🔥 ALWAYS SHOW TOP 10
    df_top = df_out.sort_values("Score", ascending=False).head(10)

    # 🔥 TOP SECTORS
    sector_df = pd.DataFrame(
        list(sector_power.items()),
        columns=["Sector","Strength"]
    ).sort_values("Strength", ascending=False)

    # ================= DISPLAY =================

    st.subheader("🚀 TOP 10 STOCKS (SMART MONEY)")
    st.dataframe(df_top, use_container_width=True)

    st.subheader("🏭 SECTOR STRENGTH")
    st.dataframe(sector_df, use_container_width=True)

    st.success("✅ Market Scan Complete")

    st.markdown("""
    ### 📌 HOW TO TRADE

    🟢 Focus on TOP 3 stocks from TOP sector  
    🟢 Enter on breakout + volume  
    🔴 Always use stop loss  
    🎯 Target = 2x risk  
    ⛔ Avoid weak sectors  
    """)
