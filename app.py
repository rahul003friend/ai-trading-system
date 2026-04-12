import streamlit as st
import pandas as pd
import yfinance as yf
import time
from ta.momentum import RSIIndicator
from ta.volume import OnBalanceVolumeIndicator

st.set_page_config(layout="wide")
st.title("🚀 PRO AI TRADING TERMINAL (STABLE VERSION)")

# ================= STOCK LIST =================
ALL_STOCKS = [
    "RELIANCE.NS","SBIN.NS","ICICIBANK.NS",
    "TATASTEEL.NS","INFY.NS"
]

# ================= DATA LOADER =================
@st.cache_data(ttl=300)
def load_data(stock):
    for attempt in range(3):
        try:
            df = yf.download(
                stock,
                period="6mo",
                interval="1d",
                progress=False,
                threads=False
            )

            if df is None or df.empty:
                time.sleep(1)
                continue

            # Fix multi-index issue
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            if "Close" not in df:
                continue

            close = df["Close"]

            if isinstance(close, pd.DataFrame):
                close = close.squeeze()

            df["MA20"] = close.rolling(20).mean()
            df["MA50"] = close.rolling(50).mean()
            df["MA200"] = close.rolling(200).mean()

            df["RSI"] = RSIIndicator(close).rsi()
            df["OBV"] = OnBalanceVolumeIndicator(close, df["Volume"]).on_balance_volume()

            return df

        except Exception as e:
            time.sleep(1)

    return None

# ================= LOGIC =================

def calculate_score(df):
    if df is None or len(df) < 50:
        return 0

    l = df.iloc[-1]
    score = 0

    if l["MA20"] > l["MA50"] > l["MA200"]:
        score += 3

    if l["RSI"] > 50:
        score += 2

    if df["OBV"].iloc[-1] > df["OBV"].iloc[-10]:
        score += 2

    return score


def breakout_signal(df):
    try:
        prev_high = df["High"].rolling(10).max().iloc[-2]
        return df["Close"].iloc[-1] > prev_high
    except:
        return False


def trade_plan(df):
    l = df.iloc[-1]

    entry = round(l["Close"], 2)
    sl = round(df["Low"].rolling(10).min().iloc[-1], 2)

    risk = entry - sl
    target = round(entry + (risk * 2), 2)

    return entry, sl, target


def decision(score, breakout):
    if breakout and score >= 6:
        return "🔥 BUY NOW"
    elif score >= 6:
        return "⏳ WAIT"
    else:
        return "❌ AVOID"

# ================= UI =================

run = st.button("▶ Run Scan")

# ================= MAIN =================

if run:

    results = []
    success_count = 0

    for stock in ALL_STOCKS:

        st.write(f"📡 Fetching: {stock}")  # debug

        df = load_data(stock)

        if df is None or df.empty:
            st.warning(f"❌ Failed: {stock}")
            continue

        success_count += 1

        score = calculate_score(df)
        breakout = breakout_signal(df)
        entry, sl, target = trade_plan(df)

        price = round(df["Close"].iloc[-1], 2)
        dec = decision(score, breakout)

        results.append({
            "Stock": stock,
            "Decision": dec,
            "Price": price,
            "Score": score,
            "Entry": entry,
            "SL": sl,
            "Target": target,
            "Breakout": breakout
        })

    st.write(f"✅ Stocks Loaded: {success_count}/{len(ALL_STOCKS)}")

    df_out = pd.DataFrame(results)

    if df_out.empty:
        st.error("🚨 No data fetched. Try again after 1 min.")
    else:
        df_out = df_out.sort_values("Score", ascending=False)

        st.subheader("🔥 TRADE SIGNALS")
        st.dataframe(df_out, use_container_width=True)

        buys = df_out[df_out["Decision"] == "🔥 BUY NOW"]

        st.subheader("🚀 IMMEDIATE BUYS")
        st.dataframe(buys, use_container_width=True)
