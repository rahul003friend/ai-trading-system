import streamlit as st
import pandas as pd
import yfinance as yf
import requests
import time
from ta.momentum import RSIIndicator
from ta.volume import OnBalanceVolumeIndicator

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

TELEGRAM_TOKEN = ""
CHAT_ID = ""

# ================= FUNCTIONS =================

def send_alert(msg):
    if TELEGRAM_TOKEN == "" or CHAT_ID == "":
        return
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg})
    except:
        pass


@st.cache_data(ttl=300)
def load_data(stock):
    for _ in range(2):  # retry twice
        try:
            df = yf.download(stock, period="6mo", progress=False)

            if df is None or df.empty or "Close" not in df:
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

        except:
            time.sleep(1)

    return None


def calculate_score(df):
    if df is None or len(df) < 50:
        return 0

    s = 0
    l = df.iloc[-1]

    # Trend
    if l["MA20"] > l["MA50"] > l["MA200"]:
        s += 3

    # Near high
    high = df["High"].rolling(252).max().iloc[-1]
    if l["Close"] > 0.75 * high:
        s += 2

    # RSI
    if 50 < l["RSI"] < 65:
        s += 1

    if df["RSI"].iloc[-1] > df["RSI"].iloc[-5]:
        s += 1

    # Volume
    avg_vol = df["Volume"].rolling(20).mean().iloc[-1]
    if l["Volume"] < avg_vol:
        s += 1

    # OBV
    if df["OBV"].iloc[-1] > df["OBV"].iloc[-10]:
        s += 2

    return s


# ================= UI =================

run = st.button("▶ Run Scan")
auto = st.checkbox("Auto Refresh (30s)")

if run or auto:

    results = []
    sector_count = {}

    for stock in STOCKS:
        st.write(f"Checking: {stock}")  # debug

        df = load_data(stock)

        if df is None or df.empty:
            continue

        score = calculate_score(df)
        price = round(df["Close"].iloc[-1], 2)

        sector = SECTORS.get(stock, "OTHER")
        if score >= 8:
            sector_count[sector] = sector_count.get(sector, 0) + 1

        if score >= 8:
            msg = f"🔥 {stock} | ₹{price} | Score: {score}"
            send_alert(msg)

        results.append({
            "Stock": stock,
            "Price": price,
            "Score": score,
            "Sector": sector
        })

    df_out = pd.DataFrame(results)

    if df_out.empty:
        st.error("⚠️ No data fetched. Try again.")
    else:
        df_out = df_out.sort_values("Score", ascending=False)

        st.subheader("📊 Scanner Results")
        st.dataframe(df_out, use_container_width=True)

        st.subheader("🏭 Sector Strength")
        st.write(sector_count)

        st.success("Scan Completed")

    if auto:
        time.sleep(30)
        st.rerun()
