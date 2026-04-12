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
    "360ONE.NS",
"3MINDIA.NS",
"AARTIIND.NS",
"AAVAS.NS",
"ABB.NS",
"ABBOTINDIA.NS",
"ABCAPITAL.NS",
"ABFRL.NS",
"ACC.NS",
"ADANIENT.NS",
"ADANIGREEN.NS",
"ADANIPORTS.NS",
"ADANIPOWER.NS",
"ATGL.NS",
"ADANITRANS.NS",
"ADVENZYMES.NS",
"AEGISCHEM.NS",
"AFFLE.NS",
"AIAENG.NS",
"AIRTEL.NS",
"AJANTPHARM.NS",
"ALKEM.NS",
"ALKYLAMINE.NS",
"ALLCARGO.NS",
"ALOKINDS.NS",
"AMARAJABAT.NS",
"AMBER.NS",
"AMBUJACEM.NS",
"ANANDRATHI.NS",
"ANANTRAJ.NS",
"ANGELONE.NS",
"APARINDS.NS",
"APLAPOLLO.NS",
"APLLTD.NS",
"APOLLOHOSP.NS",
"APOLLOTYRE.NS",
"APTUS.NS",
"ASAHIINDIA.NS",
"ASHOKLEY.NS",
"ASIANPAINT.NS",
"ASTERDM.NS",
"ASTRAL.NS",
"ATUL.NS",
"AUBANK.NS",
"AUROPHARMA.NS",
"AVANTIFEED.NS",
"AXISBANK.NS",
"BAJAJ-AUTO.NS",
"BAJAJFINSV.NS",
"BAJFINANCE.NS",
"BALKRISIND.NS",
"BALRAMCHIN.NS",
"BANDHANBNK.NS",
"BANKBARODA.NS",
"BATAINDIA.NS",
"BAYERCROP.NS",
"BDL.NS",
"BEL.NS",
"BERGEPAINT.NS",
"BHARATFORG.NS",
"BHARTIARTL.NS",
"BHEL.NS",
"BIOCON.NS",
"BIRLACORPN.NS",
"BLUEDART.NS",
"BLUESTARCO.NS",
"BOSCHLTD.NS",
"BPCL.NS",
"BRIGADE.NS",
"BRITANNIA.NS",
"BSOFT.NS",
"CAMS.NS",
"CANBK.NS",
"CANFINHOME.NS",
"CAPLIPOINT.NS",
"CASTROLIND.NS",
"CDSL.NS",
"CEATLTD.NS",
"CESC.NS",
"CGPOWER.NS",
"CHALET.NS",
"CHAMBLFERT.NS",
"CHEMPLASTS.NS",
"CHOLAFIN.NS",
"CIPLA.NS",
"CLEAN.NS",
"COALINDIA.NS",
"COCHINSHIP.NS",
"COFORGE.NS",
"COLPAL.NS",
"CONCOR.NS",
"COROMANDEL.NS",
"CREDITACC.NS",
"CROMPTON.NS",
"CUB.NS",
"CUMMINSIND.NS",
"CYIENT.NS",
"DABUR.NS",
"DALBHARAT.NS",
"DEEPAKNTR.NS",
"DELTACORP.NS",
"DIVISLAB.NS",
"DIXON.NS",
"DLF.NS",
"DRREDDY.NS",
"EICHERMOT.NS",
"ESCORTS.NS",
"EXIDEIND.NS",
"FEDERALBNK.NS",
"FINEORG.NS",
"FINCABLES.NS",
"FINPIPE.NS",
"FORTIS.NS",
"FSL.NS",
"GAIL.NS",
"GLAND.NS",
"GLENMARK.NS",
"GMRINFRA.NS",
"GNFC.NS",
"GODREJAGRO.NS",
"GODREJCP.NS",
"GODREJIND.NS",
"GRANULES.NS",
"GRAPHITE.NS",
"GRASIM.NS",
"GRINDWELL.NS",
"GUJGASLTD.NS",
"HAL.NS",
"HAVELLS.NS",
"HCLTECH.NS",
"HDFC.NS",
"HDFCAMC.NS",
"HDFCBANK.NS",
"HDFCLIFE.NS",
"HEROMOTOCO.NS",
"HINDALCO.NS",
"HINDCOPPER.NS",
"HINDPETRO.NS",
"HINDUNILVR.NS",
"HONAUT.NS",
"HUDCO.NS",
"ICICIBANK.NS",
"ICICIGI.NS",
"ICICIPRULI.NS",
"IDBI.NS",
"IDFCFIRSTB.NS",
"IEX.NS",
"IGL.NS",
"INDHOTEL.NS",
"INDIAMART.NS",
"INDIGO.NS",
"INDUSINDBK.NS",
"INDUSTOWER.NS",
"INFY.NS",
"INTELLECT.NS",
"IOC.NS",
"IPCALAB.NS",
"IRCTC.NS",
"IRFC.NS",
"ISEC.NS",
"ITC.NS",
"JBCHEPHARM.NS",
"JBMA.NS",
"JINDALSTEL.NS",
"JKCEMENT.NS",
"JKLAKSHMI.NS",
"JKTYRE.NS",
"JMFINANCIL.NS",
"JSWENERGY.NS",
"JSWSTEEL.NS",
"JUBLFOOD.NS",
"JUBLINGREA.NS",
"KALYANKJIL.NS",
"KANSAINER.NS",
"KEI.NS",
"KNRCON.NS",
"KOTAKBANK.NS",
"LALPATHLAB.NS",
"LAURUSLABS.NS",
"LICHSGFIN.NS",
"LICI.NS",
"LT.NS",
"LTF.NS",
"LTIM.NS",
"LTTS.NS",
"LUPIN.NS",
"M&M.NS",
"M&MFIN.NS",
"MANAPPURAM.NS",
"MARICO.NS",
"MARUTI.NS",
"MAXHEALTH.NS",
"MCX.NS",
"METROPOLIS.NS",
"MFSL.NS",
"MGL.NS",
"MINDTREE.NS",
"MOTHERSUMI.NS",
"MPHASIS.NS",
"MRF.NS",
"MUTHOOTFIN.NS",
"NAM-INDIA.NS",
"NATIONALUM.NS",
"NAUKRI.NS",
"NAVINFLUOR.NS",
"NBCC.NS",
"NCC.NS",
"NHPC.NS",
"NLCINDIA.NS",
"NMDC.NS",
"NTPC.NS",
"OBEROIRLTY.NS",
"OFSS.NS",
"OIL.NS",
"ONGC.NS",
"PAGEIND.NS",
"PEL.NS",
"PERSISTENT.NS",
"PETRONET.NS",
"PFC.NS",
"PIDILITIND.NS",
"PIIND.NS",
"PNB.NS",
"POLYCAB.NS",
"POWERGRID.NS",
"PRAJIND.NS",
"PRESTIGE.NS",
"PTC.NS",
"RAMCOCEM.NS",
"RBLBANK.NS",
"RECLTD.NS",
"RELIANCE.NS",
"SAIL.NS",
"SANOFI.NS",
"SBICARD.NS",
"SBILIFE.NS",
"SBIN.NS",
"SHREECEM.NS",
"SIEMENS.NS",
"SJVN.NS",
"SRF.NS",
"SUNPHARMA.NS",
"SUNTV.NS",
"SYNGENE.NS",
"TATACHEM.NS",
"TATACOMM.NS",
"TATACONSUM.NS",
"TATAMOTORS.NS",
"TATAPOWER.NS",
"TATASTEEL.NS",
"TCS.NS",
"TECHM.NS",
"TITAN.NS",
"TORNTPHARM.NS",
"TORNTPOWER.NS",
"TRENT.NS",
"TVSMOTOR.NS",
"UBL.NS",
"ULTRACEMCO.NS",
"UNIONBANK.NS",
"UPL.NS",
"VEDL.NS",
"VOLTAS.NS",
"WIPRO.NS",
"ZEEL.NS",
"ZYDUSLIFE.NS":"ADANI","ADANIPORTS.NS":"ADANI",
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
