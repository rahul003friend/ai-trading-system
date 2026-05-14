import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import requests
from bs4 import BeautifulSoup
from ta.momentum import RSIIndicator, StochasticOscillator
from ta.volume import OnBalanceVolumeIndicator
from ta.volatility import AverageTrueRange, BollingerBands
from ta.trend import MACD, EMAIndicator
from textblob import TextBlob
from datetime import datetime, timedelta
import feedparser
import re
import warnings
warnings.filterwarnings("ignore")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# ================= TOP 200 NSE STOCKS =================
NSE_200 = [
    "RELIANCE.NS","TCS.NS","HDFCBANK.NS","INFY.NS","ICICIBANK.NS",
    "HINDUNILVR.NS","ITC.NS","SBIN.NS","BHARTIARTL.NS","KOTAKBANK.NS",
    "LT.NS","AXISBANK.NS","ASIANPAINT.NS","MARUTI.NS","TITAN.NS",
    "SUNPHARMA.NS","WIPRO.NS","ULTRACEMCO.NS","NESTLEIND.NS","BAJFINANCE.NS",
    "HCLTECH.NS","TATAMOTORS.NS","TATASTEEL.NS","NTPC.NS","POWERGRID.NS",
    "BAJAJFINSV.NS","TECHM.NS","ADANIENT.NS","ADANIPORTS.NS","JSWSTEEL.NS",
    "GRASIM.NS","CIPLA.NS","DIVISLAB.NS","DRREDDY.NS","EICHERMOT.NS",
    "BPCL.NS","COALINDIA.NS","HEROMOTOCO.NS","HINDALCO.NS","ONGC.NS",
    "M&M.NS","APOLLOHOSP.NS","BRITANNIA.NS","DABUR.NS","GODREJCP.NS",
    "HAVELLS.NS","INDUSINDBK.NS","LUPIN.NS","MARICO.NS","MCDOWELL-N.NS",
    "PIIND.NS","SHREECEM.NS","SIEMENS.NS","TORNTPHARM.NS","VEDL.NS",
    "ZOMATO.NS","NYKAA.NS","DMART.NS","PAYTM.NS","IRCTC.NS",
    "TATACONSUM.NS","BAJAJ-AUTO.NS","BOSCHLTD.NS","CHOLAFIN.NS","DLF.NS",
    "FEDERALBNK.NS","GAIL.NS","GODREJPROP.NS","IDFCFIRSTB.NS","INDUSTOWER.NS",
    "INDIGO.NS","IOC.NS","JUBLFOOD.NS","LICHSGFIN.NS","MUTHOOTFIN.NS",
    "NMDC.NS","OFSS.NS","PERSISTENT.NS","PNB.NS","RECLTD.NS",
    "SAIL.NS","SBICARD.NS","SBILIFE.NS","TATAPOWER.NS","TORNTPOWER.NS",
    "UPL.NS","VOLTAS.NS","WHIRLPOOL.NS","ZEEL.NS","ABB.NS",
    "ACC.NS","ADANIGREEN.NS","ADANITRANS.NS","ALKEM.NS","AMBUJACEM.NS",
    "AUROPHARMA.NS","BALKRISIND.NS","BANDHANBNK.NS","BANKBARODA.NS","BERGEPAINT.NS",
    "BIOCON.NS","CANBK.NS","COLPAL.NS","COROMANDEL.NS","CUMMINSIND.NS",
    "DEEPAKFERT.NS","DIXON.NS","FLUOROCHEM.NS","GICRE.NS","GLENMARK.NS",
    "GMRINFRA.NS","GRANULES.NS","HDFCAMC.NS","HDFCLIFE.NS","HINDPETRO.NS",
    "HONAUT.NS","ICICIGI.NS","ICICIPRULI.NS","IOCL.NS","IRFC.NS",
    "ISEC.NS","JKCEMENT.NS","JUBILANT.NS","KANSAINER.NS","KPITTECH.NS",
    "LAURUSLABS.NS","LINDEINDIA.NS","LTIM.NS","LTTS.NS","MANAPPURAM.NS",
    "MCX.NS","METROPOLIS.NS","MINDTREE.NS","MPHASIS.NS","MRF.NS",
    "NATIONALUM.NS","NAUKRI.NS","NAVINFLUOR.NS","NLCINDIA.NS","PAGEIND.NS",
    "PETRONET.NS","PIDILITIND.NS","POLYCAB.NS","PRAJIND.NS","PRICOL.NS",
    "RAIN.NS","RAMCOCEM.NS","RATNAMANI.NS","RELAXO.NS","RITES.NS",
    "SCHAEFFLER.NS","SEQUENT.NS","SHYAMMETL.NS","SOLARINDS.NS","SONACOMS.NS",
    "STARHEALTH.NS","SUNTV.NS","SUPREMEIND.NS","TATACHEM.NS","TATACOMM.NS",
    "TATAMETALI.NS","TRENT.NS","TRIDENT.NS","UCOBANK.NS","UJJIVANSFB.NS",
    "UNIONBANK.NS","UNITDSPR.NS","VGUARD.NS","VBL.NS","WELCORP.NS",
    "WOCKPHARMA.NS","ZYDUSLIFE.NS","AAVAS.NS","ABCAPITAL.NS","ABFRL.NS",
    "ANGELONE.NS","APTUS.NS","ASTRAL.NS","ATUL.NS","AUBANK.NS",
    "AWHCL.NS","BAJAJELEC.NS","BAJAJHLDNG.NS","BATAINDIA.NS","BLUESTARCO.NS",
    "BSOFT.NS","CAMPUS.NS","CANFINHOME.NS","CARBORUNIV.NS","CDSL.NS",
    "CLEAN.NS","COCHINSHIP.NS","CONCOR.NS","CRAFTSMAN.NS","CROMPTON.NS",
    "CYIENT.NS","DATAPATTNS.NS","DELHIVERY.NS","DEVYANI.NS","EIHOTEL.NS",
    "ELGIEQUIP.NS","ENDURANCE.NS","ENGINERSIN.NS","EPIGRAL.NS","EQUITASBNK.NS"
]

# ================= SAFE HELPERS =================

def safe_last(x):
    try:
        if x is None: return 0.0
        if isinstance(x, pd.DataFrame): x = x.iloc[:, 0]
        if isinstance(x, pd.Series):
            x = x.dropna()
            if len(x) == 0: return 0.0
            return float(x.iloc[-1])
        return float(x)
    except:
        return 0.0

def safe_df(df, min_rows=60):
    if df is None or df.empty: return None
    df = df.copy()
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    for col in ["Open", "High", "Low", "Close", "Volume"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=["Close"])
    return df if len(df) >= min_rows else None

# ================= DATA LOADER (1 YEAR) =================

def load_data(stock):
    try:
        df = yf.download(stock, period="1y", progress=False, auto_adjust=True)
        df = safe_df(df)
        if df is None: return None

        close = df["Close"]
        vol   = df["Volume"]

        # Trend indicators
        df["MA20"]  = close.rolling(20).mean()
        df["MA50"]  = close.rolling(50).mean()
        df["MA200"] = close.rolling(200).mean()
        df["EMA9"]  = EMAIndicator(close, window=9).ema_indicator()
        df["EMA21"] = EMAIndicator(close, window=21).ema_indicator()

        # Momentum
        df["RSI"]   = RSIIndicator(close).rsi()
        stoch       = StochasticOscillator(df["High"], df["Low"], close)
        df["STOCH_K"] = stoch.stoch()
        df["STOCH_D"] = stoch.stoch_signal()

        # MACD
        macd        = MACD(close)
        df["MACD"]  = macd.macd()
        df["MACD_S"]= macd.macd_signal()
        df["MACD_H"]= macd.macd_diff()

        # Volatility
        atr         = AverageTrueRange(df["High"], df["Low"], close)
        df["ATR"]   = atr.average_true_range()
        bb          = BollingerBands(close)
        df["BB_UP"] = bb.bollinger_hband()
        df["BB_LO"] = bb.bollinger_lband()
        df["BB_MID"]= bb.bollinger_mavg()

        # Volume
        df["OBV"]   = OnBalanceVolumeIndicator(close, vol).on_balance_volume()
        df["VOL_MA"]= vol.rolling(20).mean()

        # Price derived
        df["RETURN_1D"] = close.pct_change()
        df["RETURN_5D"] = close.pct_change(5)
        df["HIGH_52W"]  = close.rolling(252).max()
        df["LOW_52W"]   = close.rolling(252).min()

        return df
    except:
        return None

# ================= MULTI-SOURCE SENTIMENT ENGINE =================

def _polarity(text):
    """Return TextBlob polarity for a chunk of text."""
    try:
        return TextBlob(str(text)[:3000]).sentiment.polarity
    except:
        return 0.0


def _fetch_dsc_india(ticker):
    """
    Scrape DSCIndia.com for news/announcements related to the stock.
    Returns polarity score (-1 to +1).
    """
    try:
        q = ticker.replace(".NS", "").replace("-", "").replace("&", "")
        url = f"https://www.dscindia.com/search?q={q}"
        r = requests.get(url, timeout=7, headers=HEADERS)
        soup = BeautifulSoup(r.text, "html.parser")
        texts = " ".join(t.get_text(" ", strip=True) for t in soup.find_all(["p", "h2", "h3", "li"])[:30])
        return _polarity(texts)
    except:
        return 0.0


def _fetch_nse_announcements(ticker):
    """
    Pull corporate announcements from NSE India corporate filings RSS/API.
    Returns polarity score and list of announcement titles.
    """
    try:
        symbol = ticker.replace(".NS", "").replace("-", "").replace("&", "")
        url = (
            f"https://www.nseindia.com/api/corp-info?symbol={symbol}"
            f"&corpType=announcements&market=equities"
        )
        r = requests.get(url, timeout=7, headers={
            **HEADERS,
            "Referer": "https://www.nseindia.com/",
            "Accept": "application/json",
        })
        data = r.json()
        items = data.get("data", [])[:10]
        titles = [item.get("subject", "") + " " + item.get("desc", "") for item in items]
        combined = " ".join(titles)
        polarity = _polarity(combined)

        # Keyword boosting for corporate events
        positive_kw = ["dividend", "bonus", "buyback", "profit", "record high",
                       "expansion", "order win", "partnership", "acquisition"]
        negative_kw = ["loss", "penalty", "litigation", "default", "downgrade",
                       "fraud", "investigation", "delay", "shutdown"]
        boost = sum(0.15 for kw in positive_kw if kw in combined.lower())
        boost -= sum(0.15 for kw in negative_kw if kw in combined.lower())
        polarity = max(-1.0, min(1.0, polarity + boost))
        return polarity, titles[:5]
    except:
        return 0.0, []


def _fetch_google_news(ticker):
    """Google News RSS — broad market sentiment."""
    try:
        q = ticker.replace(".NS", "").replace("-", "").replace("&", "")
        url = f"https://news.google.com/rss/search?q={q}+NSE+India+stock&hl=en-IN&gl=IN&ceid=IN:en"
        feed = feedparser.parse(url)
        texts = " ".join(
            entry.get("title", "") + " " + entry.get("summary", "")
            for entry in feed.entries[:15]
        )
        return _polarity(texts)
    except:
        return 0.0


def _fetch_moneycontrol(ticker):
    """MoneyControl news RSS for the stock."""
    try:
        q = ticker.replace(".NS", "").replace("-", "").replace("&", "").lower()
        url = f"https://www.moneycontrol.com/rss/results.xml?search={q}"
        feed = feedparser.parse(url)
        texts = " ".join(
            entry.get("title", "") + " " + entry.get("summary", "")
            for entry in feed.entries[:10]
        )
        return _polarity(texts)
    except:
        return 0.0


def _fetch_economic_times(ticker):
    """Economic Times Markets RSS."""
    try:
        q = ticker.replace(".NS", "").replace("-", "")
        url = f"https://economictimes.indiatimes.com/rssfeedsdefault.cms"
        feed = feedparser.parse(url)
        q_clean = q.lower()
        texts = " ".join(
            entry.get("title", "") + " " + entry.get("summary", "")
            for entry in feed.entries
            if q_clean in (entry.get("title", "") + entry.get("summary", "")).lower()
        )
        return _polarity(texts) if texts else 0.0
    except:
        return 0.0


def _fetch_reddit_stockmarket(ticker):
    """
    Reddit r/IndiaInvestments and r/StockMarketIndia via public JSON.
    No API key needed.
    """
    try:
        symbol = ticker.replace(".NS", "").replace("-", "")
        scores = []
        for sub in ["IndiaInvestments", "StockMarketIndia", "IndianStreetBets"]:
            url = f"https://www.reddit.com/r/{sub}/search.json?q={symbol}&sort=new&limit=10&restrict_sr=1"
            r = requests.get(url, timeout=6, headers={**HEADERS, "Accept": "application/json"})
            posts = r.json().get("data", {}).get("children", [])
            texts = " ".join(
                p["data"].get("title", "") + " " + p["data"].get("selftext", "")
                for p in posts
            )
            if texts.strip():
                scores.append(_polarity(texts))
        return float(np.mean(scores)) if scores else 0.0
    except:
        return 0.0


def get_sentiment(stock):
    """
    Aggregate sentiment from 6 sources with weighted scoring.

    Sources & weights:
      NSE Corporate Announcements  → 35%  (official, highest signal)
      DSC India                    → 20%  (Indian financial portal)
      Economic Times               → 15%  (mainstream financial media)
      MoneyControl                 → 15%  (retail investor media)
      Google News                  → 10%  (broad coverage)
      Reddit India                 →  5%  (social/retail sentiment)

    Returns: composite_score (±15), label, breakdown dict
    """
    weights = {
        "NSE Announcements": 0.35,
        "DSC India":         0.20,
        "Economic Times":    0.15,
        "MoneyControl":      0.15,
        "Google News":       0.10,
        "Reddit":            0.05,
    }

    nse_pol, ann_titles = _fetch_nse_announcements(stock)
    raw = {
        "NSE Announcements": nse_pol,
        "DSC India":         _fetch_dsc_india(stock),
        "Economic Times":    _fetch_economic_times(stock),
        "MoneyControl":      _fetch_moneycontrol(stock),
        "Google News":       _fetch_google_news(stock),
        "Reddit":            _fetch_reddit_stockmarket(stock),
    }

    composite = sum(raw[src] * weights[src] for src in weights)
    composite_score = round(composite * 15, 2)   # scale to ±15

    label = (
        "🟢 Positive" if composite_score > 2
        else "🔴 Negative" if composite_score < -2
        else "🟡 Neutral"
    )

    breakdown = {
        src: {
            "polarity": round(raw[src], 3),
            "weight":   f"{int(weights[src]*100)}%",
            "signal":   "🟢" if raw[src] > 0.05 else ("🔴" if raw[src] < -0.05 else "🟡"),
        }
        for src in weights
    }

    return composite_score, label, round(composite, 3), breakdown, ann_titles

# ================= NEXT-DAY PREDICTION ENGINE =================

def predict_next_day(df, news_score):
    """
    Multi-factor scoring system predicting UP / DOWN for next day.
    Returns: direction, confidence (%), score, details dict
    """
    if df is None or len(df) < 60:
        return "UNKNOWN", 0, 0, {}

    score = 0
    max_score = 0
    details = {}

    try:
        close   = safe_last(df["Close"])
        ma20    = safe_last(df["MA20"])
        ma50    = safe_last(df["MA50"])
        ma200   = safe_last(df["MA200"])
        ema9    = safe_last(df["EMA9"])
        ema21   = safe_last(df["EMA21"])
        rsi     = safe_last(df["RSI"])
        stoch_k = safe_last(df["STOCH_K"])
        stoch_d = safe_last(df["STOCH_D"])
        macd_h  = safe_last(df["MACD_H"])
        bb_up   = safe_last(df["BB_UP"])
        bb_lo   = safe_last(df["BB_LO"])
        bb_mid  = safe_last(df["BB_MID"])
        atr     = safe_last(df["ATR"])
        obv_now = safe_last(df["OBV"])
        vol_now = safe_last(df["Volume"])
        vol_ma  = safe_last(df["VOL_MA"])
        ret_1d  = safe_last(df["RETURN_1D"])
        ret_5d  = safe_last(df["RETURN_5D"])
        high52  = safe_last(df["HIGH_52W"])
        low52   = safe_last(df["LOW_52W"])

        # --- TREND ALIGNMENT (±3) ---
        max_score += 3
        if ma20 > ma50 > ma200:
            score += 3
            details["Trend"] = ("UP", "MA20>MA50>MA200 — Strong uptrend")
        elif ma20 < ma50 < ma200:
            score -= 3
            details["Trend"] = ("DOWN", "MA20<MA50<MA200 — Strong downtrend")
        else:
            details["Trend"] = ("NEUTRAL", "Mixed MA alignment")

        # --- EMA CROSSOVER (±2) ---
        max_score += 2
        if ema9 > ema21:
            score += 2
            details["EMA Cross"] = ("UP", "EMA9 above EMA21")
        else:
            score -= 2
            details["EMA Cross"] = ("DOWN", "EMA9 below EMA21")

        # --- RSI ZONE (±2) ---
        max_score += 2
        if 50 < rsi < 70:
            score += 2
            details["RSI"] = ("UP", f"RSI={rsi:.1f} — Bullish zone")
        elif 30 < rsi <= 50:
            score -= 1
            details["RSI"] = ("DOWN", f"RSI={rsi:.1f} — Bearish zone")
        elif rsi <= 30:
            score += 1  # oversold bounce
            details["RSI"] = ("UP", f"RSI={rsi:.1f} — Oversold (bounce likely)")
        elif rsi >= 70:
            score -= 1  # overbought
            details["RSI"] = ("DOWN", f"RSI={rsi:.1f} — Overbought (pullback risk)")

        # --- STOCHASTIC (±2) ---
        max_score += 2
        if stoch_k > stoch_d and stoch_k < 80:
            score += 2
            details["Stochastic"] = ("UP", f"K={stoch_k:.1f} crossed above D")
        elif stoch_k < stoch_d and stoch_k > 20:
            score -= 2
            details["Stochastic"] = ("DOWN", f"K={stoch_k:.1f} crossed below D")
        else:
            details["Stochastic"] = ("NEUTRAL", "Extreme zone — cautious")

        # --- MACD HISTOGRAM (±2) ---
        max_score += 2
        if macd_h > 0:
            score += 2
            details["MACD"] = ("UP", f"Histogram positive ({macd_h:.2f})")
        else:
            score -= 2
            details["MACD"] = ("DOWN", f"Histogram negative ({macd_h:.2f})")

        # --- BOLLINGER BAND POSITION (±2) ---
        max_score += 2
        bb_pct = (close - bb_lo) / (bb_up - bb_lo + 0.0001)
        if bb_pct > 0.6:
            score += 2
            details["Bollinger"] = ("UP", f"Price in upper band ({bb_pct:.0%})")
        elif bb_pct < 0.4:
            score -= 2
            details["Bollinger"] = ("DOWN", f"Price in lower band ({bb_pct:.0%})")
        else:
            details["Bollinger"] = ("NEUTRAL", "Price mid-band")

        # --- VOLUME SURGE (±2) ---
        max_score += 2
        if vol_now > vol_ma * 1.5 and ret_1d > 0:
            score += 2
            details["Volume"] = ("UP", "High volume with positive move")
        elif vol_now > vol_ma * 1.5 and ret_1d < 0:
            score -= 2
            details["Volume"] = ("DOWN", "High volume with negative move")
        else:
            details["Volume"] = ("NEUTRAL", "Normal volume")

        # --- OBV TREND (±2) ---
        max_score += 2
        if len(df) >= 10:
            obv_old = safe_last(df["OBV"].iloc[-10:-1])
            if obv_now > obv_old:
                score += 2
                details["OBV"] = ("UP", "On-Balance Volume rising")
            else:
                score -= 2
                details["OBV"] = ("DOWN", "On-Balance Volume falling")

        # --- 52W POSITION (±1) ---
        max_score += 1
        pct_from_high = (close - high52) / (high52 + 0.0001)
        if pct_from_high > -0.05:
            score += 1
            details["52W"] = ("UP", f"Near 52-week high ({pct_from_high:.1%})")
        elif pct_from_high < -0.30:
            score -= 1
            details["52W"] = ("DOWN", f"Far from 52W high ({pct_from_high:.1%})")
        else:
            details["52W"] = ("NEUTRAL", f"{pct_from_high:.1%} from 52W high")

        # --- NEWS SENTIMENT (±3) ---
        max_score += 3
        ns = max(-3, min(3, news_score / 5))
        score += ns
        sentiment_label = "UP" if ns > 0 else ("DOWN" if ns < 0 else "NEUTRAL")
        details["News Sentiment"] = (sentiment_label, f"Score={news_score:.2f}")

        # --- RECENT MOMENTUM (±2) ---
        max_score += 2
        if ret_5d > 0.03:
            score += 2
            details["5D Momentum"] = ("UP", f"+{ret_5d:.1%} in 5 days")
        elif ret_5d < -0.03:
            score -= 2
            details["5D Momentum"] = ("DOWN", f"{ret_5d:.1%} in 5 days")
        else:
            details["5D Momentum"] = ("NEUTRAL", f"{ret_5d:.1%} in 5 days")

    except Exception as e:
        return "UNKNOWN", 0, 0, {}

    # Normalize confidence
    confidence = (score + max_score) / (2 * max_score) * 100
    confidence = round(min(99, max(1, confidence)), 1)
    direction  = "UP 📈" if score >= 0 else "DOWN 📉"

    return direction, confidence, round(score, 2), details

# ================= TRADE PLAN =================

def trade_plan(df):
    try:
        entry = safe_last(df["Close"])
        atr   = safe_last(df["ATR"])
        sl     = round(entry - 1.5 * atr, 2)
        target = round(entry + (entry - sl) * 2, 2)
        rr     = round((target - entry) / (entry - sl), 2) if entry != sl else 0
        return round(entry, 2), sl, target, rr
    except:
        return 0, 0, 0, 0

# ================= BACKTEST =================

def backtest(df):
    if df is None or len(df) < 100:
        return 0, 0, 0

    trades, wins, losses = [], 0, 0
    try:
        for i in range(60, len(df) - 5):
            sub = df.iloc[:i]
            ma20  = safe_last(sub["MA20"])
            ma50  = safe_last(sub["MA50"])
            ma200 = safe_last(sub["MA200"])
            rsi   = safe_last(sub["RSI"])
            macd_h= safe_last(sub["MACD_H"])

            # Entry condition: trend + momentum
            if ma20 > ma50 and rsi > 50 and macd_h > 0:
                entry = safe_last(sub["Close"])
                atr   = safe_last(sub["ATR"])
                if atr == 0: continue
                sl     = entry - 1.5 * atr
                target = entry + (entry - sl) * 2
                future = df.iloc[i:i+5]
                result = 0
                for _, r in future.iterrows():
                    if isinstance(r, pd.Series):
                        lo = safe_last(r.get("Low", 0))
                        hi = safe_last(r.get("High", 0))
                    else:
                        lo = hi = 0
                    if lo <= sl:   result = -1; break
                    if hi >= target: result = 1; break
                trades.append(result)
                if result == 1: wins += 1
                elif result == -1: losses += 1

        total = len(trades)
        if total == 0: return 0, 0, 0
        win_rate = round(wins / total * 100, 1)
        expectancy = round((wins - losses) / total * 100, 1)
        return total, win_rate, expectancy
    except:
        return 0, 0, 0

# ================= INTRADAY =================

def load_intraday(stock):
    try:
        df = yf.download(stock, period="1d", interval="5m", progress=False, auto_adjust=True)
        return safe_df(df, min_rows=10)
    except:
        return None

def intraday_signal(df):
    try:
        if df is None or len(df) < 15: return None
        opening = df.iloc[:3]
        open_high = safe_last(opening["High"].max())
        open_low  = safe_last(opening["Low"].min())
        close = safe_last(df["Close"])
        vol_recent = safe_last(df["Volume"].iloc[-3:].sum())
        vol_total  = safe_last(df["Volume"].sum())
        vol_surge = vol_recent / (vol_total / len(df)) if vol_total > 0 else 1

        if close > open_high and vol_surge > 1.3:
            sl     = round(open_low, 2)
            tgt    = round(close + (close - sl) * 1.5, 2)
            return "BUY 🟢", round(close, 2), sl, tgt
        if close < open_low and vol_surge > 1.3:
            sl     = round(open_high, 2)
            tgt    = round(close - (sl - close) * 1.5, 2)
            return "SELL 🔴", round(close, 2), sl, tgt
        return "WAIT ⏳", round(close, 2), 0, 0
    except:
        return None

# =================== STREAMLIT UI ===================

st.set_page_config(
    page_title="AI Trading System — NSE 200",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---- Custom CSS ----
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Syne:wght@400;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Syne', sans-serif;
    background: #0a0e1a;
    color: #e0e6f0;
}
.stApp { background: #0a0e1a; }

h1, h2, h3 { font-family: 'Syne', sans-serif; font-weight: 800; }

.metric-card {
    background: linear-gradient(135deg, #111827, #1a2235);
    border: 1px solid #2a3550;
    border-radius: 12px;
    padding: 16px 20px;
    margin: 6px 0;
}

.up-badge {
    background: #0d3b2a;
    color: #00e676;
    border: 1px solid #00e676;
    border-radius: 6px;
    padding: 2px 10px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 13px;
    font-weight: 700;
}

.down-badge {
    background: #3b0d0d;
    color: #ff5252;
    border: 1px solid #ff5252;
    border-radius: 6px;
    padding: 2px 10px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 13px;
    font-weight: 700;
}

.neutral-badge {
    background: #1a1a2e;
    color: #ffd740;
    border: 1px solid #ffd740;
    border-radius: 6px;
    padding: 2px 10px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 13px;
    font-weight: 700;
}

.stDataFrame { font-family: 'JetBrains Mono', monospace; font-size: 12px; }
.stButton > button {
    background: linear-gradient(135deg, #1565c0, #0d47a1);
    color: white;
    border: none;
    border-radius: 8px;
    font-family: 'Syne', sans-serif;
    font-weight: 700;
    padding: 10px 24px;
    transition: all 0.2s;
}
.stButton > button:hover { background: linear-gradient(135deg, #1976d2, #1565c0); }
</style>
""", unsafe_allow_html=True)

# ---- Header ----
st.markdown("## 📊 AI Trading System — NSE Top 200")
st.markdown("*Next-day UP/DOWN prediction · 1-year backtesting · Market sentiment*")
st.divider()

# ---- Sidebar Controls ----
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    max_stocks = st.slider("Stocks to Scan", 10, 200, 50, step=10)
    min_score  = st.slider("Min Prediction Score Filter", -20, 20, 2)
    st.divider()
    selected_stocks = NSE_200[:max_stocks]
    st.markdown(f"**Scanning:** {len(selected_stocks)} stocks")
    st.divider()
    st.markdown("### 🔍 Single Stock Deep Dive")
    single_stock = st.text_input("Enter NSE ticker (e.g. RELIANCE.NS)", "RELIANCE.NS")
    deep_dive_btn = st.button("🔬 Analyse Stock")

# ---- TABS ----
tab1, tab2, tab3, tab4 = st.tabs([
    "🔮 Next-Day Prediction",
    "📈 Backtest Results",
    "⚡ Intraday Signals",
    "🔬 Deep Dive"
])

# ===== TAB 1: NEXT-DAY PREDICTION =====
with tab1:
    st.markdown("### 🔮 Next-Day Movement Prediction (Top NSE Stocks)")
    st.markdown("Multi-factor scoring: trend, RSI, MACD, Bollinger, volume, news sentiment")
    
    if st.button("▶️ Run Prediction Scan"):
        results = []
        prog = st.progress(0, text="Scanning stocks...")
        
        for i, stock in enumerate(selected_stocks):
            prog.progress((i + 1) / len(selected_stocks), text=f"Analysing {stock}...")
            
            df = load_data(stock)
            if df is None:
                continue
            
            ns, ns_label, polarity, sent_breakdown, ann_titles = get_sentiment(stock)
            direction, confidence, raw_score, _ = predict_next_day(df, ns)
            entry, sl, target, rr = trade_plan(df)
            
            if raw_score < min_score:
                continue
            
            results.append({
                "Stock":       stock.replace(".NS", ""),
                "Prediction":  direction,
                "Confidence":  f"{confidence}%",
                "Score":       raw_score,
                "Entry ₹":     entry,
                "SL ₹":        sl,
                "Target ₹":    target,
                "R:R":         rr,
                "Sentiment":   ns_label,
            })
        
        prog.empty()
        
        if results:
            df_res = pd.DataFrame(results)
            df_res = df_res.sort_values("Score", ascending=False)
            
            col1, col2, col3 = st.columns(3)
            up_count   = sum(1 for r in results if "UP" in r["Prediction"])
            down_count = sum(1 for r in results if "DOWN" in r["Prediction"])
            col1.metric("✅ Bullish Picks", up_count)
            col2.metric("❌ Bearish Picks", down_count)
            col3.metric("📋 Total Scanned", len(results))
            
            st.dataframe(
                df_res,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Confidence": st.column_config.ProgressColumn("Confidence", min_value=0, max_value=100),
                    "Score": st.column_config.NumberColumn("Score", format="%.2f"),
                }
            )
            
            # Top 5 picks
            st.markdown("#### 🏆 Top 5 Bullish Picks")
            top5 = df_res[df_res["Prediction"].str.contains("UP")].head(5)
            st.dataframe(top5, use_container_width=True, hide_index=True)
        else:
            st.warning("No stocks matched the criteria. Try lowering the score filter.")

# ===== TAB 2: BACKTEST =====
with tab2:
    st.markdown("### 📈 1-Year Backtest Results")
    st.markdown("Strategy: MA trend + RSI>50 + MACD histogram positive. Hold up to 5 days.")
    
    if st.button("▶️ Run Backtest"):
        bt_results = []
        prog = st.progress(0, text="Backtesting...")
        
        for i, stock in enumerate(selected_stocks):
            prog.progress((i + 1) / len(selected_stocks), text=f"Backtesting {stock}...")
            df = load_data(stock)
            if df is None: continue
            total, win_rate, expectancy = backtest(df)
            if total > 0:
                bt_results.append({
                    "Stock":      stock.replace(".NS", ""),
                    "Trades":     total,
                    "Win Rate %": win_rate,
                    "Expectancy": expectancy,
                    "Grade": "⭐ Excellent" if win_rate >= 60 else ("✅ Good" if win_rate >= 50 else "⚠️ Weak"),
                })
        
        prog.empty()
        
        if bt_results:
            df_bt = pd.DataFrame(bt_results).sort_values("Win Rate %", ascending=False)
            avg_win = round(df_bt["Win Rate %"].mean(), 1)
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Avg Win Rate", f"{avg_win}%")
            col2.metric("Best Performer", df_bt.iloc[0]["Stock"])
            col3.metric("Total Backtests", len(bt_results))
            
            st.dataframe(df_bt, use_container_width=True, hide_index=True)

# ===== TAB 3: INTRADAY =====
with tab3:
    st.markdown("### ⚡ Intraday Breakout Signals (Today)")
    st.markdown("Opening range breakout with volume confirmation")
    
    if st.button("▶️ Scan Intraday"):
        intra = []
        prog = st.progress(0, text="Scanning intraday...")
        
        for i, stock in enumerate(selected_stocks):
            prog.progress((i + 1) / len(selected_stocks), text=f"Intraday: {stock}...")
            df = load_intraday(stock)
            if df is None: continue
            sig = intraday_signal(df)
            if sig and "WAIT" not in sig[0]:
                intra.append({
                    "Stock":  stock.replace(".NS", ""),
                    "Signal": sig[0],
                    "Entry ₹": sig[1],
                    "SL ₹":   sig[2],
                    "Target ₹": sig[3],
                })
        
        prog.empty()
        
        if intra:
            st.dataframe(pd.DataFrame(intra), use_container_width=True, hide_index=True)
        else:
            st.info("No strong intraday breakouts found right now. Run during market hours (9:15 AM – 3:30 PM IST).")

# ===== TAB 4: DEEP DIVE =====
with tab4:
    st.markdown("### 🔬 Single Stock Deep Dive")
    
    if deep_dive_btn and single_stock:
        ticker = single_stock.upper().strip()
        if not ticker.endswith(".NS"): ticker += ".NS"
        
        with st.spinner(f"Analysing {ticker}..."):
            df = load_data(ticker)

        if df is None:
            st.error(f"Could not fetch data for {ticker}. Check ticker symbol.")
        else:
            ns, ns_label, polarity, sent_breakdown, ann_titles = get_sentiment(ticker)
            direction, confidence, raw_score, details = predict_next_day(df, ns)
            entry, sl, target, rr = trade_plan(df)
            total_bt, win_rate, expectancy = backtest(df)

            # Summary row
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("📌 Ticker", ticker.replace(".NS", ""))
            col2.metric("🔮 Prediction", direction)
            col3.metric("💯 Confidence", f"{confidence}%")
            col4.metric("📰 Sentiment", ns_label)

            st.divider()

            # Trade plan
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Entry ₹", entry)
            col2.metric("Stop Loss ₹", sl)
            col3.metric("Target ₹", target)
            col4.metric("Risk:Reward", f"1:{rr}")

            st.divider()

            # ---- SENTIMENT BREAKDOWN ----
            st.markdown("#### 📰 Sentiment Breakdown by Source")
            sent_rows = []
            for src, info in sent_breakdown.items():
                sent_rows.append({
                    "Source": src,
                    "Signal": info["signal"],
                    "Polarity": info["polarity"],
                    "Weight": info["weight"],
                })
            st.dataframe(pd.DataFrame(sent_rows), use_container_width=True, hide_index=True)

            # Corporate announcements
            if ann_titles:
                st.markdown("#### 📢 Latest NSE Corporate Announcements")
                for t in ann_titles:
                    st.markdown(f"- {t}")

            st.divider()
            
            # Factor breakdown
            st.markdown("#### 🧠 Factor-by-Factor Breakdown")
            for factor, (signal, reason) in details.items():
                badge = "up-badge" if signal == "UP" else ("down-badge" if signal == "DOWN" else "neutral-badge")
                st.markdown(
                    f'<div class="metric-card"><b>{factor}</b>: '
                    f'<span class="{badge}">{signal}</span> &nbsp; {reason}</div>',
                    unsafe_allow_html=True
                )
            
            st.divider()
            
            # Backtest results
            st.markdown("#### 📈 Historical Strategy Performance (1 Year)")
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Trades", total_bt)
            col2.metric("Win Rate", f"{win_rate}%")
            col3.metric("Expectancy", f"{expectancy}%")
            
            # Price chart
            st.markdown("#### 📊 Price + MA Chart (Last 6 Months)")
            chart_df = df[["Close", "MA20", "MA50", "MA200"]].tail(180).dropna()
            st.line_chart(chart_df)

# ---- Footer ----
st.divider()
st.markdown(
    "<small>⚠️ **Disclaimer**: This tool is for educational purposes only. "
    "Stock predictions involve significant risk. Always consult a SEBI-registered advisor before investing. "
    "Past backtest performance does not guarantee future results.</small>",
    unsafe_allow_html=True
)
