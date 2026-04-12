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
st.title("🚀 AI TRADING TERMINAL — MARKET SENTIMENT ENGINE")

# ================= STOCK UNIVERSE =================
ALL_STOCKS = [
    "RELIANCE.NS","SBIN.NS","ICICIBANK.NS","HDFCBANK.NS",
    "AXISBANK.NS","KOTAKBANK.NS","INFY.NS","TCS.NS",
    "WIPRO.NS","LT.NS","TATASTEEL.NS","HINDALCO.NS",
    "JSWSTEEL.NS","ONGC.NS","BPCL.NS","ITC.NS",
    "BHARTIARTL.NS","ADANIENT.NS","ADANIPORTS.NS",
    "POWERGRID.NS","NTPC.NS","ULTRACEMCO.NS"
]

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

# ================= NEWS SENTIMENT =================
def get_news_sentiment(stock):
    try:
        name = stock.replace(".NS", "")
        url = f"https://news.google.com/rss/search?q={name}+stock"

        r = requests.get(url, timeout=5)
        text = r.text[:2000]

        sentiment = TextBlob(text).sentiment.polarity

        return round(sentiment * 10, 2)  # scale
    except:
        return 0

# ================= SENTIMENT SCORE =================
def sentiment_score(df, news_score):

    if df is None or len(df) < 50:
        return 0

    l = df.iloc[-1]
    score = 0

    # Trend
    if l["MA20"] > l["MA50"] > l["MA200"]:
        score += 3

    # Momentum
    if 50 < l["RSI"] < 70:
        score += 2

    if df["RSI"].iloc[-1] > df["RSI"].iloc[-5]:
        score += 1

    # Volume
    if df["OBV"].iloc[-1] > df["OBV"].iloc[-10]:
        score += 2

    # Breakout
    prev_high = df["High"].rolling(5).max().iloc[-2]
    if l["Close"] > prev_high:
        score += 2

    # 🔥 NEWS IMPACT
    score += news_score

    return round(score, 2)

# ================= TRADE PLAN =================
def trade_plan(df):
    l = df.iloc[-1]

    entry = round(l["Close"], 2)
    sl = round(entry - (1.5 * l["ATR"]), 2)

    risk = entry - sl
    target = round(entry + risk * 2, 2)

    return entry, sl, target

# ================= MAIN ENGINE =================
def generate_signals():

    results = []

    for stock in ALL_STOCKS:

        st.write(f"📡 {stock}")

        df = load_data(stock)

        if df is None or df.empty:
            continue

        news = get_news_sentiment(stock)

        score = sentiment_score(df, news)

        if score < 6:
            continue

        entry, sl, target = trade_plan(df)
        price = round(df["Close"].iloc[-1], 2)

        results.append({
            "Stock": stock,
            "Sentiment Score": score,
            "News": news,
            "Price": price,
            "Entry": entry,
            "Stop Loss": sl,
            "Target": target
        })

    df_out = pd.DataFrame(results)

    if not df_out.empty:
        df_out = df_out.sort_values("Sentiment Score", ascending=False).head(10)

    return df_out

# ================= UI =================
run = st.button("▶ Generate Top 10 Trades")

if run:

    df_signals = generate_signals()

    if df_signals.empty:
        st.warning("No strong sentiment today")
    else:
        st.subheader("🔥 TOP 10 MARKET SENTIMENT TRADES")
        st.dataframe(df_signals, use_container_width=True)

        st.success("✅ Ready for Trading")

        st.markdown("""
        ### 📌 HOW TO TRADE

        🟢 Enter only on breakout with volume  
        🔴 Always use stop-loss  
        🎯 Exit at target or same day  
        ⚠️ Avoid overtrading (pick best 3–5)
        """)
