import streamlit as st
import pandas as pd
import yfinance as yf
import requests

from ta.momentum import RSIIndicator
from ta.volume import OnBalanceVolumeIndicator
from ta.volatility import AverageTrueRange
from textblob import TextBlob

# ================= SAFE HELPER =================
def safe_float(x):
    try:
        return float(x.item() if hasattr(x, "item") else x)
    except:
        return 0.0

# ================= PAGE =================
st.set_page_config(layout="wide")
st.title("🚀 AI TRADING DASHBOARD (FINAL STABLE BUILD)")

# ================= SIDEBAR =================
scan_btn = st.sidebar.button("📊 Swing Scan")
backtest_btn = st.sidebar.button("📈 Backtest")
intraday_btn = st.sidebar.button("⚡ Intraday 5m Scanner")

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
        if df is None or df.empty:
            return None

        df = df.copy()

        for col in ["Open","High","Low","Close","Volume"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        df = df.dropna()

        if len(df) < 60:
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
    if df is None or len(df) < 60:
        return 0

    l = df.iloc[-1]

    ma20 = safe_float(l["MA20"])
    ma50 = safe_float(l["MA50"])
    ma200 = safe_float(l["MA200"])
    rsi = safe_float(l["RSI"])

    s = 0

    if ma20 > ma50 > ma200:
        s += 3

    if 50 < rsi < 70:
        s += 2

    if df["OBV"].iloc[-1] > df["OBV"].iloc[-10]:
        s += 2

    prev_high = df["High"].rolling(5).max().iloc[-2]
    close = safe_float(l["Close"])

    if close > safe_float(prev_high):
        s += 2

    s += news

    return round(s, 2)

# ================= TRADE PLAN =================
def trade_plan(df):
    l = df.iloc[-1]

    entry = safe_float(l["Close"])
    atr = safe_float(l["ATR"])

    sl = entry - (1.5 * atr)
    target = entry + (entry - sl) * 2

    return round(entry,2), round(sl,2), round(target,2)

# ================= BACKTEST =================
def backtest(df):
    if df is None or len(df) < 100:
        return 0, 0

    trades = []

    for i in range(50, len(df) - 5):

        sub = df.iloc[:i]
        l = sub.iloc[-1]

        ma20 = safe_float(l["MA20"])
        ma50 = safe_float(l["MA50"])
        ma200 = safe_float(l["MA200"])

        if ma20 > ma50 > ma200:

            prev_high = sub["High"].rolling(5).max().iloc[-2]

            if safe_float(l["Close"]) > safe_float(prev_high):

                entry = safe_float(l["Close"])
                sl = entry - (1.5 * safe_float(l["ATR"]))
                target = entry + (entry - sl) * 2

                future = df.iloc[i:i+5]

                result = 0

                for _, r in future.iterrows():
                    if safe_float(r["Low"]) <= sl:
                        result = -1
                        break
                    if safe_float(r["High"]) >= target:
                        result = 1
                        break

                trades.append(result)

    if len(trades) == 0:
        return 0, 0

    wins = trades.count(1)
    acc = (wins / len(trades)) * 100

    return len(trades), round(acc, 2)

# ================= INTRADAY =================
def load_intraday(stock):
    try:
        df = yf.download(stock, period="1d", interval="5m", progress=False)
        if df is None or df.empty:
            return None

        df = df.copy()

        for col in ["Open","High","Low","Close","Volume"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        return df.dropna()

    except:
        return None

# ================= ORB =================
def intraday_breakout(df):

    if df is None or len(df) < 20:
        return None

    opening = df.iloc[:3]

    high = safe_float(opening["High"].max())
    low = safe_float(opening["Low"].min())

    last = df.iloc[-1]
    close = safe_float(last["Close"])

    signal = "NO TRADE"
    entry = sl = target = 0

    if close > high:
        signal = "BUY"
        entry = close
        sl = low
        target = entry + (entry - sl) * 1.5

    elif close < low:
        signal = "SELL"
        entry = close
        sl = high
        target = entry - (sl - entry) * 1.5

    return signal, round(entry,2), round(sl,2), round(target,2)

# ================= UI =================
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

if intraday_btn:

    st.subheader("⚡ INTRADAY ORB BREAKOUT")

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
