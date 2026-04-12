import streamlit as st
import pandas as pd
import yfinance as yf
import time
from ta.momentum import RSIIndicator
from ta.volume import OnBalanceVolumeIndicator
from ta.volatility import AverageTrueRange

st.set_page_config(layout="wide")
st.title("🚀 PRO AI TRADING TERMINAL (ELITE VERSION)")

# ================= STOCKS =================
ALL_STOCKS = [
    "RELIANCE.NS","SBIN.NS","ICICIBANK.NS",
    "TATASTEEL.NS","INFY.NS","HDFCBANK.NS","LT.NS"
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

            # ATR for stop loss
            atr = AverageTrueRange(df["High"], df["Low"], close)
            df["ATR"] = atr.average_true_range()

            return df
        except:
            time.sleep(1)

    return None

# ================= SIGNAL ENGINE =================

def breakout(df):
    try:
        prev_high = df["High"].rolling(10).max().iloc[-2]
        today = df.iloc[-1]
        avg_vol = df["Volume"].rolling(20).mean().iloc[-1]

        return (today["Close"] > prev_high) and (today["Volume"] > avg_vol)
    except:
        return False


def score(df):
    l = df.iloc[-1]
    s = 0

    if l["MA20"] > l["MA50"] > l["MA200"]:
        s += 3
    if l["RSI"] > 50:
        s += 2
    if df["OBV"].iloc[-1] > df["OBV"].iloc[-10]:
        s += 2

    return s


def trade_plan(df):
    l = df.iloc[-1]

    entry = round(l["Close"], 2)

    # ATR stop loss
    sl = round(entry - (1.5 * l["ATR"]), 2)

    risk = entry - sl
    target = round(entry + risk * 2, 2)

    return entry, sl, target


def decision(score, breakout):
    if breakout and score >= 6:
        return "🔥 BUY NOW"
    elif score >= 6:
        return "⏳ READY"
    else:
        return "❌ AVOID"

# ================= UI =================

st.sidebar.header("⚙️ Controls")
selected = st.sidebar.multiselect("Stocks", ALL_STOCKS, default=ALL_STOCKS)
run = st.sidebar.button("▶ Run Scan")

# ================= MAIN =================

if run:

    results = []

    for stock in selected:

        st.write(f"📡 Fetching {stock}")

        df = load_data(stock)

        if df is None or df.empty:
            st.warning(f"❌ Failed {stock}")
            continue

        s = score(df)
        b = breakout(df)
        entry, sl, target = trade_plan(df)

        price = round(df["Close"].iloc[-1], 2)
        dec = decision(s, b)

        results.append({
            "Stock": stock,
            "Decision": dec,
            "Price": price,
            "Score": s,
            "Entry": entry,
            "SL": sl,
            "Target": target,
            "Breakout": b
        })

        # 📊 CHART DISPLAY
        st.subheader(f"📈 {stock}")
        chart = df[["Close","MA20","MA50"]]
        st.line_chart(chart)

    df_out = pd.DataFrame(results)

    if not df_out.empty:
        df_out = df_out.sort_values("Score", ascending=False)

        st.subheader("🔥 TRADE SIGNALS")
        st.dataframe(df_out, use_container_width=True)

        buys = df_out[df_out["Decision"] == "🔥 BUY NOW"]

        st.subheader("🚀 IMMEDIATE BUYS")
        st.dataframe(buys, use_container_width=True)

    else:
        st.error("No data available")
