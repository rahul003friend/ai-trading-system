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
st.title("🚀 AI TRADING DASHBOARD (FINAL STABLE VERSION)")

# ================= STOCK UNIVERSE =================
ALL_STOCKS = {
    "RELIANCE.NS":"ENERGY","ONGC.NS":"ENERGY",
    "SBIN.NS":"BANK","ICICIBANK.NS":"BANK","HDFCBANK.NS":"BANK",
    "INFY.NS":"IT","TCS.NS":"IT",
    "LT.NS":"INFRA","ULTRACEMCO.NS":"INFRA",
    "TATASTEEL.NS":"METAL","HINDALCO.NS":"METAL",
    "ITC.NS":"FMCG","HINDUNILVR.NS":"FMCG"
}

# ================= SIDEBAR (IMPORTANT ORDER FIX) =================
st.sidebar.header("⚙️ Controls")

scan_btn = st.sidebar.button("📊 Swing Scan")
backtest_btn = st.sidebar.button("📈 Backtest")
intraday_btn = st.sidebar.button("⚡ Intraday 5m Scanner")

# ================= DATA =================
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
        return TextBlob(r.text[:1500]).sentiment.polarity * 10
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
    return round(s, 2)

# ================= TRADE PLAN =================
def trade_plan(df):
    l = df.iloc[-1]
    entry = round(l["Close"], 2)
    sl = round(entry - (1.5 * l["ATR"]), 2)
    target = round(entry + (entry - sl) * 2, 2)
    return entry, sl, target

# ================= BACKTEST =================
def backtest(df):
    if df is None or len(df) < 100:
        return 0, 0

    trades = []

    for i in range(50, len(df) - 5):

        sub = df.iloc[:i]
        l = sub.iloc[-1]

        if l["MA20"] > l["MA50"] > l["MA200"]:

            prev_high = sub["High"].rolling(5).max().iloc[-2]

            if l["Close"] > prev_high:

                entry = l["Close"]
                sl = entry - (1.5 * l["ATR"])
                target = entry + (entry - sl) * 2

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
        return 0, 0

    wins = trades.count(1)
    acc = (wins / len(trades)) * 100

    return len(trades), round(acc, 2)

# ================= INTRADAY DATA =================
def load_intraday(stock):
    try:
        df = yf.download(stock, period="1d", interval="5m", progress=False)
        if df is None or df.empty:
            return None
        return df
    except:
        return None

def intraday_breakout(df):
    if df is None or len(df) < 20:
        return None

    opening = df.iloc[:3]

    high = opening["High"].max()
    low = opening["Low"].min()

    last = df.iloc[-1]

    signal = "NO TRADE"
    entry = sl = target = 0

    if last["Close"] > high:
        signal = "BUY"
        entry = last["Close"]
        sl = low
        target = entry + (entry - sl) * 1.5

    elif last["Close"] < low:
        signal = "SELL"
        entry = last["Close"]
        sl = high
        target = entry - (sl - entry) * 1.5

    return signal, round(entry,2), round(sl,2), round(target,2)

# ================= MAIN UI =================

# ================= SWING SCAN =================
if scan_btn:

    results = []
    sector_power = {}

    for stock, sector in ALL_STOCKS.items():

        df = load_data(stock)
        if df is None:
            continue

        s = score(df, news_sentiment(stock))
        entry, sl, target = trade_plan(df)

        results.append({
            "Stock": stock,
            "Sector": sector,
            "Score": s,
            "Entry": entry,
            "SL": sl,
            "Target": target
        })

        sector_power[sector] = sector_power.get(sector, 0) + s

    df_out = pd.DataFrame(results)

    if not df_out.empty:
        st.subheader("🔥 TOP 10 STOCKS")
        st.dataframe(df_out.sort_values("Score", ascending=False).head(10),
                     use_container_width=True)

        st.subheader("🏭 SECTOR STRENGTH")
        st.bar_chart(pd.DataFrame(list(sector_power.items()),
                                  columns=["Sector","Strength"]).set_index("Sector"))

# ================= BACKTEST =================
if backtest_btn:

    st.subheader("📊 BACKTEST RESULTS")

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
        st.dataframe(df_bt, use_container_width=True)
        st.bar_chart(df_bt.set_index("Stock"))

# ================= INTRADAY =================
if intraday_btn:

    st.subheader("⚡ INTRADAY 5-MIN BREAKOUT (ORB)")

    results = []

    for stock in ALL_STOCKS.keys():

        df = load_intraday(stock)
        if df is None:
            continue

        res = intraday_breakout(df)
        if res is None:
            continue

        signal, entry, sl, target = res

        if signal != "NO TRADE":
            results.append({
                "Stock": stock,
                "Signal": signal,
                "Entry": entry,
                "SL": sl,
                "Target": target
            })

    df_intra = pd.DataFrame(results)

    if not df_intra.empty:
        st.dataframe(df_intra, use_container_width=True)
    else:
        st.warning("No breakout signals right now")
