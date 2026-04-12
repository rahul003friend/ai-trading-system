import streamlit as st
import pandas as pd
import yfinance as yf
import time
import requests
import matplotlib.pyplot as plt

from ta.momentum import RSIIndicator
from ta.volume import OnBalanceVolumeIndicator
from ta.volatility import AverageTrueRange
from textblob import TextBlob

st.set_page_config(layout="wide")
st.title("🚀 PRO AI TRADING DASHBOARD")

# ================= STOCKS =================
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

# ================= TRADE =================
def trade_plan(df):
    l = df.iloc[-1]
    entry = round(l["Close"],2)
    sl = round(entry - (1.5 * l["ATR"]),2)
    target = round(entry + (entry-sl)*2,2)
    return entry, sl, target

# ================= BACKTEST =================
def backtest(df):
    trades = []

    for i in range(50, len(df)-5):
        sub = df.iloc[:i]
        l = sub.iloc[-1]

        if l["MA20"] > l["MA50"] > l["MA200"]:
            prev_high = sub["High"].rolling(5).max().iloc[-2]

            if l["Close"] > prev_high:
                entry = l["Close"]
                sl = entry - (1.5 * l["ATR"])
                target = entry + (entry-sl)*2

                future = df.iloc[i:i+5]
                result = 0

                for _, r in future.iterrows():
                    if r["Low"] <= sl:
                        result = -1
                        break
                    if r["High"] >= target:
                        result = 1
                        break

                trades.append(result)

    if len(trades) == 0:
        return 0,0

    wins = trades.count(1)
    acc = (wins/len(trades))*100
    return len(trades), round(acc,2)

# ================= TABS =================
tab1, tab2, tab3 = st.tabs(["📊 Market Scan", "📈 Charts", "📊 Backtest"])

# ================= TAB 1 =================
with tab1:

    if st.button("▶ Run Market Scan"):

        results = []
        sector_power = {}

        for stock, sector in ALL_STOCKS.items():

            df = load_data(stock)
            if df is None:
                continue

            news = news_sentiment(stock)
            s = score(df, news)

            entry, sl, target = trade_plan(df)

            results.append({
                "Stock": stock,
                "Sector": sector,
                "Score": s,
                "Entry": entry,
                "SL": sl,
                "Target": target
            })

            sector_power[sector] = sector_power.get(sector,0) + s

        df_out = pd.DataFrame(results)

        if not df_out.empty:
            top = df_out.sort_values("Score", ascending=False).head(10)

            st.subheader("🔥 Top 10 Stocks")
            st.dataframe(top, use_container_width=True)

            # Sector chart
            st.subheader("🏭 Sector Strength")
            sec_df = pd.DataFrame(list(sector_power.items()), columns=["Sector","Strength"])

            fig, ax = plt.subplots()
            ax.bar(sec_df["Sector"], sec_df["Strength"])
            plt.xticks(rotation=45)

            st.pyplot(fig)

# ================= TAB 2 =================
with tab2:

    stock_sel = st.selectbox("Select Stock", list(ALL_STOCKS.keys()))

    df = load_data(stock_sel)

    if df is not None:
        st.line_chart(df[["Close","MA20","MA50"]])

# ================= TAB 3 =================
with tab3:

    if st.button("📊 Run Backtest"):

        results = []

        for stock in ALL_STOCKS.keys():

            df = load_data(stock)
            if df is None:
                continue

            trades, acc = backtest(df)

            results.append({
                "Stock": stock,
                "Trades": trades,
                "Accuracy %": acc
            })

        df_bt = pd.DataFrame(results)

        if not df_bt.empty:

            st.dataframe(df_bt)

            # Accuracy chart
            fig, ax = plt.subplots()
            ax.bar(df_bt["Stock"], df_bt["Accuracy %"])
            plt.xticks(rotation=45)

            st.pyplot(fig)
