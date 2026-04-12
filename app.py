import streamlit as st
import pandas as pd
import yfinance as yf
import time
from ta.momentum import RSIIndicator
from ta.volume import OnBalanceVolumeIndicator
from ta.volatility import AverageTrueRange

st.set_page_config(layout="wide")
st.title("🚀 AI TRADING TERMINAL — 9:30 AM SIGNAL ENGINE")

# ================= STOCK LIST =================
ALL_STOCKS = [
    "RELIANCE.NS","SBIN.NS","ICICIBANK.NS",
    "TATASTEEL.NS","INFY.NS","HDFCBANK.NS",
    "LT.NS","AXISBANK.NS","ITC.NS","ONGC.NS"
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

# ================= LOGIC =================

def calculate_score(df):
    if df is None or len(df) < 50:
        return 0

    l = df.iloc[-1]
    score = 0

    if l["MA20"] > l["MA50"] > l["MA200"]:
        score += 3

    if 50 < l["RSI"] < 70:
        score += 2

    if df["OBV"].iloc[-1] > df["OBV"].iloc[-10]:
        score += 2

    return score


def breakout(df):
    try:
        prev_high = df["High"].rolling(5).max().iloc[-2]
        return df["Close"].iloc[-1] > prev_high
    except:
        return False


def trade_plan(df):
    l = df.iloc[-1]

    entry = round(l["Close"], 2)

    # ATR based SL
    sl = round(entry - (1.5 * l["ATR"]), 2)

    risk = entry - sl
    target = round(entry + (risk * 2), 2)

    return entry, sl, target


def generate_signals():

    results = []

    for stock in ALL_STOCKS:

        st.write(f"📡 Fetching {stock}")

        df = load_data(stock)

        if df is None or df.empty:
            continue

        score = calculate_score(df)

        if score < 6:
            continue

        b = breakout(df)

        entry, sl, target = trade_plan(df)
        price = round(df["Close"].iloc[-1], 2)

        results.append({
            "Stock": stock,
            "Price": price,
            "Score": score,
            "Breakout": b,
            "Entry": entry,
            "Stop Loss": sl,
            "Target": target
        })

    df_out = pd.DataFrame(results)

    if not df_out.empty:
        df_out = df_out.sort_values("Score", ascending=False).head(5)

    return df_out

# ================= UI =================

run = st.button("▶ Generate 9:30 Signals")

if run:

    signals = generate_signals()

    if signals.empty:
        st.warning("❌ No strong trades today")
    else:
        st.subheader("🚀 TOP 5 TRADES (9:30 AM PLAN)")
        st.dataframe(signals, use_container_width=True)

        st.success("✅ Trade Setup Ready")

        st.markdown("""
        ### 📌 HOW TO TRADE

        ✅ Buy only if price crosses Entry with volume  
        🔴 Stop Loss is mandatory  
        🎯 Exit at Target or same day close  
        ⛔ Avoid if market is weak
        """)
