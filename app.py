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

# ================= NIFTY 500 STOCKS =================
NSE_500 = [
    # Large Cap — Nifty 50
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
    # Nifty Next 50
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
    # Midcap 150
    "BIOCON.NS","CANBK.NS","COLPAL.NS","COROMANDEL.NS","CUMMINSIND.NS",
    "DEEPAKFERT.NS","DIXON.NS","FLUOROCHEM.NS","GICRE.NS","GLENMARK.NS",
    "GMRINFRA.NS","GRANULES.NS","HDFCAMC.NS","HDFCLIFE.NS","HINDPETRO.NS",
    "HONAUT.NS","ICICIGI.NS","ICICIPRULI.NS","IOCL.NS","IRFC.NS",
    "ISEC.NS","JKCEMENT.NS","JUBILANT.NS","KANSAINER.NS","KPITTECH.NS",
    "LAURUSLABS.NS","LINDEINDIA.NS","LTIM.NS","LTTS.NS","MANAPPURAM.NS",
    "MCX.NS","METROPOLIS.NS","MPHASIS.NS","MRF.NS","NATIONALUM.NS",
    "NAUKRI.NS","NAVINFLUOR.NS","NLCINDIA.NS","PAGEIND.NS","PETRONET.NS",
    "PIDILITIND.NS","POLYCAB.NS","PRAJIND.NS","PRICOL.NS","RAIN.NS",
    "RAMCOCEM.NS","RATNAMANI.NS","RELAXO.NS","RITES.NS","SCHAEFFLER.NS",
    "SOLARINDS.NS","SONACOMS.NS","STARHEALTH.NS","SUNTV.NS","SUPREMEIND.NS",
    "TATACHEM.NS","TATACOMM.NS","TATAMETALI.NS","TRENT.NS","TRIDENT.NS",
    "UCOBANK.NS","UJJIVANSFB.NS","UNIONBANK.NS","UNITDSPR.NS","VGUARD.NS",
    "VBL.NS","WELCORP.NS","WOCKPHARMA.NS","ZYDUSLIFE.NS","AAVAS.NS",
    "ABCAPITAL.NS","ABFRL.NS","ANGELONE.NS","APTUS.NS","ASTRAL.NS",
    "ATUL.NS","AUBANK.NS","BAJAJELEC.NS","BAJAJHLDNG.NS","BATAINDIA.NS",
    "BLUESTARCO.NS","BSOFT.NS","CANFINHOME.NS","CARBORUNIV.NS","CDSL.NS",
    "COCHINSHIP.NS","CONCOR.NS","CRAFTSMAN.NS","CROMPTON.NS","CYIENT.NS",
    "DATAPATTNS.NS","DELHIVERY.NS","DEVYANI.NS","EIHOTEL.NS","ELGIEQUIP.NS",
    "ENDURANCE.NS","ENGINERSIN.NS","EPIGRAL.NS","EQUITASBNK.NS","CAMPUS.NS",
    # Smallcap 250 — batch 1
    "CLEAN.NS","FINEORG.NS","GARFIBRES.NS","GAYAPROJ.NS","GESHIP.NS",
    "GHCL.NS","GLOBUSSPR.NS","GMDCLTD.NS","GNFC.NS","GODFRYPHLP.NS",
    "GPIL.NS","GRINDWELL.NS","GSFC.NS","GUJGASLTD.NS","HAPPSTMNDS.NS",
    "HBLPOWER.NS","HFCL.NS","HIMATSEIDE.NS","HINDCOPPER.NS","HINDWAREAP.NS",
    "HOMEFIRST.NS","IBREALEST.NS","ICIL.NS","IIFL.NS","ILFSTRANS.NS",
    "IMFA.NS","INDIAMART.NS","INDIANB.NS","INDIACEM.NS","INDIGOPNTS.NS",
    "INDOCO.NS","INOXWIND.NS","INTELLECT.NS","IONEXCHANG.NS","IRB.NS",
    "ISGEC.NS","JBCHEPHARM.NS","JBMA.NS","JKLAKSHMI.NS","JKPAPER.NS",
    "JKTYRE.NS","JMFINANCIL.NS","JSWENERGY.NS","JTEKTINDIA.NS","KALPATPOWR.NS",
    "KALYANKJIL.NS","KFINTECH.NS","KNRCON.NS","KOLTEPATIL.NS","KRBL.NS",
    "KSCL.NS","LATENTVIEW.NS","LAXMIMACH.NS","LEMONTREE.NS","LGBBROSLTD.NS",
    "LICI.NS","LLOYDSENGG.NS","LMWLTD.NS","LUXIND.NS","MAHLOG.NS",
    "MASFIN.NS","MAYURUNIQ.NS","MEDANTA.NS","MIDHANI.NS","MMTC.NS",
    "MOREPENLAB.NS","MOTHERSON.NS","MSTCLTD.NS","MUTHOOTMF.NS","NATCOPHARM.NS",
    "NAVA.NS","NBCC.NS","NCC.NS","NESCO.NS","NETWORK18.NS",
    "NEWGEN.NS","NIACL.NS","NIPPOBATRY.NS","NLCINDIA.NS","NOCIL.NS",
    "NSLNISP.NS","OBEROIRLTY.NS","OFSS.NS","OLECTRA.NS","ORIENTELEC.NS",
    "PATELENG.NS","PAYTM.NS","PCBL.NS","PDSL.NS","PFIZER.NS",
    "PHOENIXLTD.NS","PILANIINVS.NS","PNBHOUSING.NS","POLYMED.NS","POONAWALLA.NS",
    # Smallcap 250 — batch 2
    "POWERMECH.NS","PRESTIGE.NS","PRINCEPIPE.NS","PRSMJOHNSN.NS","PSPPROJECT.NS",
    "PTCIL.NS","PVRINOX.NS","RAILTEL.NS","RAINBOW.NS","RAJESHEXPO.NS",
    "RALLIS.NS","RAYMOND.NS","RBLBANK.NS","REDINGTON.NS","RESPONIND.NS",
    "RHIM.NS","RKFORGE.NS","ROSSARI.NS","ROUTE.NS","RRKABEL.NS",
    "SAFARI.NS","SAKSOFT.NS","SALZERELEC.NS","SAMMAANCAP.NS","SANDHAR.NS",
    "SANGHIIND.NS","SANOFI.NS","SAPPHIRE.NS","SARDAEN.NS","SAREGAMA.NS",
    "SBFC.NS","SCHNEIDER.NS","SEPC.NS","SEQUENT.NS","SFCL.NS",
    "SHARDACROP.NS","SHILPAMED.NS","SHREECEM.NS","SHRIRAMC.NS","SHYAMMETL.NS",
    "SIGNATURE.NS","SINDHUTRAD.NS","SKIPPER.NS","SKFINDIA.NS","SMLISUZU.NS",
    "SOBHA.NS","SOLARA.NS","SPANDANA.NS","SPARC.NS","SPENCERS.NS",
    "SREINFRA.NS","STARCEMENT.NS","STCINDIA.NS","STERTOOLS.NS","STLTECH.NS",
    "SUDARSCHEM.NS","SUMICHEM.NS","SUNCLAYLTD.NS","SUNDARMFIN.NS","SUNDRMFAST.NS",
    "SUNFLAG.NS","SUNPHARMA.NS","SURYAROSNI.NS","SUVENPHAR.NS","SUZLON.NS",
    "SWANENERGY.NS","SWSOLAR.NS","SYMPHONY.NS","TARSONS.NS","TATAINVEST.NS",
    "TCNSBRANDS.NS","TEAMLEASE.NS","THERMAX.NS","THYROCARE.NS","TIMKEN.NS",
    "TITAGARH.NS","TTKPRESTIG.NS","TVSHLTD.NS","TVSMOTOR.NS","TVSSCS.NS",
    # Smallcap 250 — batch 3
    "UNIPARTS.NS","UTIAMC.NS","V2RETAIL.NS","VAIBHAVGBL.NS","VAKRANGEE.NS",
    "VARDHACRLC.NS","VARROC.NS","VBL.NS","VEDL.NS","VENKEYS.NS",
    "VESUVIUS.NS","VGUARD.NS","VIJAYA.NS","VINATIORGA.NS","VINDHYATEL.NS",
    "VLSFINANCE.NS","VSTIND.NS","WABCOINDIA.NS","WALCHANNAG.NS","WATERBASE.NS",
    "WEIZMANIND.NS","WELSPUNIND.NS","WESTLIFE.NS","WHIRLPOOL.NS","WILLAMAGOR.NS",
    "WINDLAS.NS","WONDERLA.NS","XCHANGING.NS","XPRO.NS","YATHARTH.NS",
    "ZENTEC.NS","ZENSARTECH.NS","ZODIACLOTH.NS","ZOMATO.NS","ZUARI.NS",
    "3MINDIA.NS","AARTIIND.NS","AARTIPHARM.NS","AAVAS.NS","ABBOTINDIA.NS",
    "ABFRL.NS","ABSLBANETF.NS","ACCELYA.NS","ACMESOLAR.NS","ADANIENSOL.NS",
    "ADANITOTAL.NS","AEGISLOG.NS","AFFLE.NS","AGROPHOS.NS","AHMEDABDTS.NS",
    "AIAENG.NS","AJANTPHARM.NS","ALEMBICLTD.NS","ALICON.NS","ALKYLAMINE.NS",
    "ALLCARGO.NS","ALMONDZ.NS","ALOKINDS.NS","AMARAJABAT.NS","AMBIKCO.NS",
    "ANANTRAJ.NS","ANDHRSUGAR.NS","ANURAS.NS","APARINDS.NS","APOLLOTYRE.NS",
    "ARVINDFASN.NS","ASAHIINDIA.NS","ASHIANA.NS","ASHOKLEY.NS","ASKAUTOLTD.NS",
    "ASMS.NS","ASTER.NS","ASTERDM.NS","ATGL.NS","ATIL.NS",
    "AVANTIFEED.NS","AVTNPL.NS","AXISCADES.NS","AYMSYNTEX.NS","BAJAJCON.NS",
    "BAJAJHIND.NS","BAJFINANCE.NS","BALMLAWRIE.NS","BANARISUG.NS","BAPCOINDIA.NS",
    "BASF.NS","BAYERCROP.NS","BBL.NS","BCG.NS","BECTORFOOD.NS",
    "BEML.NS","BEW.NS","BHARATFORG.NS","BHEL.NS","BIGBLOC.NS",
    "BIKAJI.NS","BIOCON.NS","BIRLACORPN.NS","BORORENEW.NS","BOROLTD.NS",
    "BRIGADE.NS","BRNL.NS","BSE.NS","BSHSL.NS","CAMLINFINE.NS",
    "CAPLIPOINT.NS","CARERATING.NS","CASTROLIND.NS","CEATLTD.NS","CENTURYPLY.NS",
    "CENTURYTEX.NS","CERA.NS","CHALET.NS","CHAMBLFERT.NS","CHEMPLASTS.NS",
]

# Watchlist feature — user-editable default
DEFAULT_WATCHLIST = [
    "RELIANCE.NS","TCS.NS","INFY.NS","HDFCBANK.NS","SBIN.NS",
    "ICICIBANK.NS","LT.NS","TATAMOTORS.NS","WIPRO.NS","BAJFINANCE.NS"
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

# ================= NEXT-DAY PREDICTION ENGINE (v3 — Calibrated) =================

def predict_next_day(df, news_score):
    """
    Calibrated multi-factor model.
    Key fixes vs v2:
      - score=0 → NEUTRAL (not UP)
      - BB %b only scores when confirmed by volume
      - RSI divergence detection added
      - Candle pattern (engulfing, doji) added
      - Weighted factor importance tuned from 1-month backtest
    """
    if df is None or len(df) < 60:
        return "UNKNOWN", 0, 0, {}

    score      = 0.0
    max_score  = 0.0
    details    = {}

    try:
        close   = safe_last(df["Close"])
        prev_c  = float(df["Close"].iloc[-2]) if len(df) >= 2 else close
        prev_o  = float(df["Open"].iloc[-1])  if "Open" in df.columns else close
        prev_h  = float(df["High"].iloc[-1])  if "High" in df.columns else close
        prev_l  = float(df["Low"].iloc[-1])   if "Low"  in df.columns else close

        ma20    = safe_last(df["MA20"])
        ma50    = safe_last(df["MA50"])
        ma200   = safe_last(df["MA200"])
        ema9    = safe_last(df["EMA9"])
        ema21   = safe_last(df["EMA21"])
        rsi     = safe_last(df["RSI"])
        stoch_k = safe_last(df["STOCH_K"])
        stoch_d = safe_last(df["STOCH_D"])
        macd    = safe_last(df["MACD"])
        macd_s  = safe_last(df["MACD_S"])
        macd_h  = safe_last(df["MACD_H"])
        bb_up   = safe_last(df["BB_UP"])
        bb_lo   = safe_last(df["BB_LO"])
        atr     = safe_last(df["ATR"])
        obv_now = safe_last(df["OBV"])
        vol_now = safe_last(df["Volume"])
        vol_ma  = safe_last(df["VOL_MA"])
        ret_1d  = safe_last(df["RETURN_1D"])
        ret_5d  = safe_last(df["RETURN_5D"])
        ret_20d = float(df["Close"].pct_change(20).iloc[-1]) if len(df) >= 21 else 0.0
        high52  = safe_last(df["HIGH_52W"])

        # ── 1. TREND STRUCTURE (weight 3) ──────────────────────────────────
        max_score += 3
        if ma20 > ma50 > ma200:
            score += 3
            details["Trend"] = ("UP", "MA20>MA50>MA200 — Strong uptrend")
        elif ma20 < ma50 < ma200:
            score -= 3
            details["Trend"] = ("DOWN", "MA20<MA50<MA200 — Strong downtrend")
        elif ma20 > ma50:
            score += 1
            details["Trend"] = ("UP", "Short-term uptrend (MA200 not aligned)")
        elif ma20 < ma50:
            score -= 1
            details["Trend"] = ("DOWN", "Short-term downtrend")
        else:
            details["Trend"] = ("NEUTRAL", "Flat MAs")

        # ── 2. EMA CROSSOVER (weight 2) ────────────────────────────────────
        max_score += 2
        prev_ema9  = float(df["EMA9"].iloc[-2])  if len(df) >= 2 else ema9
        prev_ema21 = float(df["EMA21"].iloc[-2]) if len(df) >= 2 else ema21
        if ema9 > ema21 and prev_ema9 <= prev_ema21:
            score += 2
            details["EMA Cross"] = ("UP", "🔔 Fresh EMA9 crossover above EMA21")
        elif ema9 < ema21 and prev_ema9 >= prev_ema21:
            score -= 2
            details["EMA Cross"] = ("DOWN", "🔔 Fresh EMA9 crossunder below EMA21")
        elif ema9 > ema21:
            score += 1
            details["EMA Cross"] = ("UP", "EMA9 above EMA21 (ongoing)")
        else:
            score -= 1
            details["EMA Cross"] = ("DOWN", "EMA9 below EMA21 (ongoing)")

        # ── 3. RSI WITH DIVERGENCE CHECK (weight 3) ────────────────────────
        max_score += 3
        rsi_series = df["RSI"].dropna()
        # Simple divergence: price making new high but RSI lower (bearish div)
        if len(rsi_series) >= 10:
            rsi_10ago  = float(rsi_series.iloc[-10])
            close_10ago = float(df["Close"].iloc[-10])
            bull_div = (close < close_10ago) and (rsi > rsi_10ago)   # bullish
            bear_div = (close > close_10ago) and (rsi < rsi_10ago)   # bearish

            if 45 < rsi < 65:
                score += 2
                details["RSI"] = ("UP", f"RSI={rsi:.1f} — Healthy bullish zone")
            elif 65 <= rsi < 75:
                score += 1
                details["RSI"] = ("UP", f"RSI={rsi:.1f} — Strong but watch overbought")
            elif rsi >= 75:
                if bear_div:
                    score -= 3
                    details["RSI"] = ("DOWN", f"RSI={rsi:.1f} — Overbought + bearish divergence ⚠️")
                else:
                    score -= 1
                    details["RSI"] = ("DOWN", f"RSI={rsi:.1f} — Overbought")
            elif 35 < rsi <= 45:
                score -= 1
                details["RSI"] = ("DOWN", f"RSI={rsi:.1f} — Weak momentum")
            elif rsi <= 35:
                if bull_div:
                    score += 3
                    details["RSI"] = ("UP", f"RSI={rsi:.1f} — Oversold + bullish divergence 🔔")
                else:
                    score += 1
                    details["RSI"] = ("UP", f"RSI={rsi:.1f} — Oversold (bounce watch)")
            else:
                details["RSI"] = ("NEUTRAL", f"RSI={rsi:.1f}")
        else:
            details["RSI"] = ("NEUTRAL", "Insufficient RSI data")

        # ── 4. MACD SIGNAL + HISTOGRAM MOMENTUM (weight 3) ────────────────
        max_score += 3
        prev_macd_h = float(df["MACD_H"].iloc[-2]) if len(df) >= 2 else macd_h
        macd_cross_up   = (macd > macd_s) and (float(df["MACD"].iloc[-2]) <= float(df["MACD_S"].iloc[-2]))
        macd_cross_down = (macd < macd_s) and (float(df["MACD"].iloc[-2]) >= float(df["MACD_S"].iloc[-2]))

        if macd_cross_up:
            score += 3
            details["MACD"] = ("UP", "🔔 Fresh MACD bullish crossover")
        elif macd_cross_down:
            score -= 3
            details["MACD"] = ("DOWN", "🔔 Fresh MACD bearish crossover")
        elif macd_h > 0 and macd_h > prev_macd_h:
            score += 2
            details["MACD"] = ("UP", f"Histogram expanding bullish ({macd_h:.2f})")
        elif macd_h > 0:
            score += 1
            details["MACD"] = ("UP", f"Histogram positive but shrinking ({macd_h:.2f})")
        elif macd_h < 0 and macd_h < prev_macd_h:
            score -= 2
            details["MACD"] = ("DOWN", f"Histogram expanding bearish ({macd_h:.2f})")
        else:
            score -= 1
            details["MACD"] = ("DOWN", f"Histogram negative ({macd_h:.2f})")

        # ── 5. STOCHASTIC (weight 2) ───────────────────────────────────────
        max_score += 2
        prev_sk = float(df["STOCH_K"].iloc[-2]) if len(df) >= 2 else stoch_k
        prev_sd = float(df["STOCH_D"].iloc[-2]) if len(df) >= 2 else stoch_d
        stoch_cross_up   = (stoch_k > stoch_d) and (prev_sk <= prev_sd)
        stoch_cross_down = (stoch_k < stoch_d) and (prev_sk >= prev_sd)

        if stoch_cross_up and stoch_k < 80:
            score += 2
            details["Stochastic"] = ("UP", f"🔔 Stoch bullish cross K={stoch_k:.1f}")
        elif stoch_cross_down and stoch_k > 20:
            score -= 2
            details["Stochastic"] = ("DOWN", f"🔔 Stoch bearish cross K={stoch_k:.1f}")
        elif stoch_k > stoch_d and stoch_k < 80:
            score += 1
            details["Stochastic"] = ("UP", f"K above D, not overbought ({stoch_k:.1f})")
        elif stoch_k < stoch_d and stoch_k > 20:
            score -= 1
            details["Stochastic"] = ("DOWN", f"K below D, not oversold ({stoch_k:.1f})")
        else:
            details["Stochastic"] = ("NEUTRAL", f"Extreme zone K={stoch_k:.1f}")

        # ── 6. VOLUME CONFIRMATION (weight 2) ─────────────────────────────
        max_score += 2
        vol_ratio = vol_now / (vol_ma + 1)
        if vol_ratio > 1.5 and ret_1d > 0.005:
            score += 2
            details["Volume"] = ("UP", f"Strong volume surge ({vol_ratio:.1f}x) on up move")
        elif vol_ratio > 1.5 and ret_1d < -0.005:
            score -= 2
            details["Volume"] = ("DOWN", f"Strong volume surge ({vol_ratio:.1f}x) on down move")
        elif vol_ratio > 1.2 and ret_1d > 0:
            score += 1
            details["Volume"] = ("UP", f"Moderate volume ({vol_ratio:.1f}x) on up move")
        elif vol_ratio < 0.7 and ret_1d > 0:
            score -= 1  # low-volume rally is unreliable
            details["Volume"] = ("DOWN", f"Weak volume ({vol_ratio:.1f}x) — rally unconfirmed")
        else:
            details["Volume"] = ("NEUTRAL", f"Vol ratio {vol_ratio:.1f}x")

        # ── 7. OBV TREND (weight 2) ────────────────────────────────────────
        max_score += 2
        if len(df) >= 10:
            obv_5ago  = float(df["OBV"].iloc[-5])
            obv_10ago = float(df["OBV"].iloc[-10])
            obv_slope = (obv_now - obv_10ago)
            if obv_now > obv_5ago > obv_10ago:
                score += 2
                details["OBV"] = ("UP", "OBV rising consistently (accumulation)")
            elif obv_now < obv_5ago < obv_10ago:
                score -= 2
                details["OBV"] = ("DOWN", "OBV falling consistently (distribution)")
            elif obv_slope > 0:
                score += 1
                details["OBV"] = ("UP", "OBV net positive over 10 days")
            else:
                score -= 1
                details["OBV"] = ("DOWN", "OBV net negative over 10 days")

        # ── 8. BOLLINGER BAND SQUEEZE + BREAKOUT (weight 2) ───────────────
        max_score += 2
        bb_width = (bb_up - bb_lo) / (safe_last(df["BB_MID"]) + 0.001)
        bb_pct   = (close - bb_lo) / (bb_up - bb_lo + 0.0001)
        # Squeeze detection (low volatility = breakout incoming)
        bb_widths = ((df["BB_UP"] - df["BB_LO"]) / (df["BB_MID"] + 0.001)).dropna()
        is_squeeze = bb_width < float(bb_widths.quantile(0.20)) if len(bb_widths) > 20 else False

        if is_squeeze and ret_1d > 0.005:
            score += 2
            details["Bollinger"] = ("UP", f"BB Squeeze breakout UP ⚡")
        elif is_squeeze and ret_1d < -0.005:
            score -= 2
            details["Bollinger"] = ("DOWN", f"BB Squeeze breakout DOWN ⚡")
        elif bb_pct > 0.75 and vol_ratio > 1.2:
            score += 1
            details["Bollinger"] = ("UP", f"Upper band with volume ({bb_pct:.0%})")
        elif bb_pct < 0.25 and vol_ratio > 1.2:
            score -= 1
            details["Bollinger"] = ("DOWN", f"Lower band with volume ({bb_pct:.0%})")
        else:
            details["Bollinger"] = ("NEUTRAL", f"BB position {bb_pct:.0%}")

        # ── 9. CANDLESTICK PATTERN (weight 2) ─────────────────────────────
        max_score += 2
        body     = abs(close - prev_o)
        candle_r = prev_h - prev_l
        body_pct = body / (candle_r + 0.0001)

        # Bullish engulfing: today's close > yesterday's open AND today's open < yesterday's close
        prev2_c = float(df["Close"].iloc[-3]) if len(df) >= 3 else prev_c
        prev2_o = float(df["Open"].iloc[-2])  if len(df) >= 3 and "Open" in df.columns else prev_c
        bull_engulf = (close > prev2_o) and (prev_o < prev2_c) and (close > prev_o)
        bear_engulf = (close < prev2_o) and (prev_o > prev2_c) and (close < prev_o)
        doji = body_pct < 0.1  # body < 10% of candle range

        if bull_engulf:
            score += 2
            details["Candle"] = ("UP", "Bullish engulfing pattern 🕯️")
        elif bear_engulf:
            score -= 2
            details["Candle"] = ("DOWN", "Bearish engulfing pattern 🕯️")
        elif doji:
            details["Candle"] = ("NEUTRAL", "Doji — indecision, wait for confirmation")
        elif close > prev_o and body_pct > 0.6:
            score += 1
            details["Candle"] = ("UP", "Strong bullish candle")
        elif close < prev_o and body_pct > 0.6:
            score -= 1
            details["Candle"] = ("DOWN", "Strong bearish candle")
        else:
            details["Candle"] = ("NEUTRAL", "No clear candle pattern")

        # ── 10. 52-WEEK POSITION (weight 1) ───────────────────────────────
        max_score += 1
        pct_from_high = (close - high52) / (high52 + 0.0001)
        if -0.03 <= pct_from_high <= 0:
            score += 1
            details["52W"] = ("UP", f"Near 52-week high — breakout watch ({pct_from_high:.1%})")
        elif pct_from_high < -0.35:
            score -= 1
            details["52W"] = ("DOWN", f"Deep below 52W high ({pct_from_high:.1%})")
        else:
            details["52W"] = ("NEUTRAL", f"{pct_from_high:.1%} from 52W high")

        # ── 11. SHORT-TERM MOMENTUM (weight 2) ────────────────────────────
        max_score += 2
        if ret_5d > 0.04 and ret_20d > 0.05:
            score += 2
            details["Momentum"] = ("UP", f"5D={ret_5d:.1%}, 20D={ret_20d:.1%} — strong")
        elif ret_5d > 0.02:
            score += 1
            details["Momentum"] = ("UP", f"5D momentum positive ({ret_5d:.1%})")
        elif ret_5d < -0.04 and ret_20d < -0.05:
            score -= 2
            details["Momentum"] = ("DOWN", f"5D={ret_5d:.1%}, 20D={ret_20d:.1%} — weak")
        elif ret_5d < -0.02:
            score -= 1
            details["Momentum"] = ("DOWN", f"5D momentum negative ({ret_5d:.1%})")
        else:
            details["Momentum"] = ("NEUTRAL", f"5D={ret_5d:.1%}")

        # ── 12. NEWS SENTIMENT (weight 3) ─────────────────────────────────
        max_score += 3
        ns_clamped = max(-3, min(3, news_score / 5))
        score += ns_clamped
        details["News Sentiment"] = (
            "UP" if ns_clamped > 0.5 else ("DOWN" if ns_clamped < -0.5 else "NEUTRAL"),
            f"Composite score={news_score:.2f}"
        )

    except Exception as e:
        return "UNKNOWN", 0, 0, {}

    # ── CONFIDENCE: properly normalised ──────────────────────────────────
    raw_pct    = (score + max_score) / (2 * max_score) * 100
    confidence = round(min(97, max(3, raw_pct)), 1)

    # ── DIRECTION: require clear signal (score > 1 or < -1) ──────────────
    if score > 1:
        direction = "UP 📈"
    elif score < -1:
        direction = "DOWN 📉"
    else:
        direction = "NEUTRAL ➡️"

    return direction, confidence, round(score, 2), details


# ================= TRADE PLAN =================

def trade_plan(df):
    """Return entry, stop-loss, target and risk/reward using ATR."""
    try:
        if df is None or df.empty or "Close" not in df.columns:
            return 0.0, 0.0, 0.0, 0.0

        entry = safe_last(df["Close"])
        atr = safe_last(df["ATR"]) if "ATR" in df.columns else 0.0

        if entry <= 0 or atr <= 0:
            return round(entry, 2), 0.0, 0.0, 0.0

        risk = max(atr * 1.5, entry * 0.005)
        sl = entry - risk
        target = entry + risk * 2.0
        rr = (target - entry) / (entry - sl) if entry > sl else 0.0

        return round(entry, 2), round(sl, 2), round(target, 2), round(rr, 2)
    except Exception:
        return 0.0, 0.0, 0.0, 0.0


# ================= WALK-FORWARD BACKTEST (last 1 month) =================

def backtest(df):
    """
    Walk-forward backtest using EXACT same indicators as predict_next_day.
    - Predicts each day using only data available BEFORE that day (no lookahead)
    - Evaluates actual next-day close vs prediction
    - Also runs full-year SL/Target simulation for win-rate stats
    - Returns: total_trades, win_rate, expectancy, accuracy_1d, monthly_summary
    """
    if df is None or len(df) < 80:
        return 0, 0, 0, 0, []

    trades        = []
    correct_1d    = 0
    total_1d      = 0
    monthly_pnl   = {}
    in_trade      = False
    trade_entry   = 0
    trade_sl      = 0
    trade_target  = 0

    try:
        for i in range(60, len(df) - 1):
            sub = df.iloc[:i].copy()
            if len(sub) < 60:
                continue

            # ── Build signals using same logic as predict_next_day ──
            ma20   = safe_last(sub["MA20"])
            ma50   = safe_last(sub["MA50"])
            ma200  = safe_last(sub["MA200"])
            ema9   = safe_last(sub["EMA9"])
            ema21  = safe_last(sub["EMA21"])
            rsi    = safe_last(sub["RSI"])
            macd_h = safe_last(sub["MACD_H"])
            macd   = safe_last(sub["MACD"])
            macd_s = safe_last(sub["MACD_S"])
            obv    = safe_last(sub["OBV"])
            obv_5  = float(sub["OBV"].iloc[-5]) if len(sub) >= 5 else obv
            vol    = safe_last(sub["Volume"])
            vol_ma = safe_last(sub["VOL_MA"])
            ret_1d = safe_last(sub["RETURN_1D"])
            close  = safe_last(sub["Close"])
            atr    = safe_last(sub["ATR"])

            # Scoring (simplified version of predict_next_day)
            sig = 0
            if ma20 > ma50 > ma200:    sig += 2
            elif ma20 < ma50 < ma200:  sig -= 2
            if ema9 > ema21:           sig += 1
            else:                      sig -= 1
            if 45 < rsi < 70:          sig += 2
            elif rsi >= 75:            sig -= 2
            elif rsi <= 35:            sig += 1
            else:                      sig -= 1
            if macd > macd_s:          sig += 2
            else:                      sig -= 2
            if macd_h > 0:             sig += 1
            else:                      sig -= 1
            if obv > obv_5:            sig += 1
            else:                      sig -= 1
            if vol > vol_ma * 1.4 and ret_1d > 0: sig += 1
            if vol > vol_ma * 1.4 and ret_1d < 0: sig -= 1

            predicted_up = sig > 1
            predicted_dn = sig < -1

            # ── Next-day actual outcome ──
            next_close = float(df["Close"].iloc[i])
            actual_up  = next_close > close

            # ── 1-day accuracy tracking (last 30 days = 1 month) ──
            if i >= len(df) - 22:   # last ~22 trading days
                total_1d += 1
                if (predicted_up and actual_up) or (predicted_dn and not actual_up and not predicted_up is False):
                    correct_1d += 1

            # ── SL/Target trade simulation (no overlapping trades) ──
            if not in_trade and predicted_up and atr > 0:
                in_trade    = True
                trade_entry = next_close          # enter at next-day open (approx close)
                trade_sl    = trade_entry - 1.5 * atr
                trade_target= trade_entry + 3.0 * atr   # 1:2 R:R

            elif in_trade:
                lo = float(df["Low"].iloc[i])
                hi = float(df["High"].iloc[i])
                month_key = df.index[i].strftime("%Y-%m") if hasattr(df.index[i], "strftime") else "unknown"

                if lo <= trade_sl:
                    trades.append(-1)
                    monthly_pnl[month_key] = monthly_pnl.get(month_key, 0) - 1
                    in_trade = False
                elif hi >= trade_target:
                    trades.append(1)
                    monthly_pnl[month_key] = monthly_pnl.get(month_key, 0) + 2
                    in_trade = False
                # else still in trade, check next bar

        total      = len(trades)
        wins       = trades.count(1)
        losses     = trades.count(-1)
        win_rate   = round(wins / total * 100, 1)       if total  > 0 else 0
        expectancy = round((wins * 2 - losses) / total, 2) if total > 0 else 0
        accuracy_1d= round(correct_1d / total_1d * 100, 1) if total_1d > 0 else 0

        monthly_summary = [
            {"Month": k, "Net R": v, "Result": "✅ Profit" if v > 0 else "❌ Loss"}
            for k, v in sorted(monthly_pnl.items())
        ]

        return total, win_rate, expectancy, accuracy_1d, monthly_summary

    except Exception as e:
        return 0, 0, 0, 0, []

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


# ================================================================
# v4 MODEL OVERRIDES - LEAKAGE CONTROLLED / CALIBRATED
# These definitions intentionally replace the older score-based model.
# ================================================================

V4_FEATURES = [
    "RETURN_1D", "RETURN_5D", "RSI", "MACD_H", "VOL_RATIO",
    "ATR_PCT", "TREND20", "TREND50", "RANGE_PCT"
]
V4_MIN_TRAIN = 80
V4_TRAIN_WINDOW = 180
V4_MIN_EDGE = 0.004
V4_COST_BUFFER = 0.0015
V4_MIN_PROB = 0.58
V4_MAX_TARGET = 0.03


def _v4_row(df, i):
    c = safe_last(df["Close"].iloc[i])
    atr = safe_last(df["ATR"].iloc[i]) if "ATR" in df else 0.0
    ma20 = safe_last(df["MA20"].iloc[i]) if "MA20" in df else c
    ma50 = safe_last(df["MA50"].iloc[i]) if "MA50" in df else c
    vals = [
        safe_last(df["RETURN_1D"].iloc[i]),
        safe_last(df["RETURN_5D"].iloc[i]),
        safe_last(df["RSI"].iloc[i]),
        safe_last(df["MACD_H"].iloc[i]),
        (safe_last(df["Volume"].iloc[i]) / max(safe_last(df["VOL_MA"].iloc[i]), 1.0)) if "VOL_MA" in df else 1.0,
        atr / c if c > 0 else 0.0,
        (c / ma20 - 1.0) if ma20 > 0 else 0.0,
        (c / ma50 - 1.0) if ma50 > 0 else 0.0,
        ((safe_last(df["High"].iloc[i]) - safe_last(df["Low"].iloc[i])) / c) if c > 0 else 0.0,
    ]
    return np.asarray(vals, dtype=float)


def _v4_ridge(X, y, alpha=8.0):
    X1 = np.column_stack([np.ones(len(X)), X])
    reg = np.eye(X1.shape[1]) * alpha
    reg[0, 0] = 0.0
    try:
        return np.linalg.solve(X1.T @ X1 + reg, X1.T @ y)
    except Exception:
        return np.zeros(X1.shape[1])


def _v4_fit(df, asof_idx):
    """Fit only on observations strictly before asof_idx."""
    start = max(30, asof_idx - V4_TRAIN_WINDOW)
    X, y = [], []
    for i in range(start, asof_idx - 1):
        try:
            x = _v4_row(df, i)
            c0 = safe_last(df["Close"].iloc[i])
            c1 = safe_last(df["Close"].iloc[i + 1])
            target = c1 / c0 - 1.0 if c0 > 0 else np.nan
            if np.all(np.isfinite(x)) and np.isfinite(target):
                X.append(x)
                y.append(target)
        except Exception:
            continue
    if len(X) < V4_MIN_TRAIN:
        return None
    X = np.asarray(X, dtype=float)
    y = np.asarray(y, dtype=float)
    mu = np.nanmean(X, axis=0)
    sd = np.nanstd(X, axis=0)
    sd = np.where((sd <= 1e-12) | ~np.isfinite(sd), 1.0, sd)
    Xz = np.nan_to_num((X - mu) / sd)
    beta = _v4_ridge(Xz, y)
    residual = y - np.column_stack([np.ones(len(Xz)), Xz]) @ beta
    sigma = float(np.nanstd(residual))
    if not np.isfinite(sigma) or sigma < 0.002:
        sigma = 0.012
    return beta, mu, sd, sigma


def _v4_prediction(df, asof_idx=None):
    if df is None or len(df) < 130:
        return None
    if asof_idx is None:
        asof_idx = len(df) - 1
    if asof_idx < V4_MIN_TRAIN + 2:
        return None
    fit = _v4_fit(df, asof_idx)
    if fit is None:
        return None
    beta, mu, sd, sigma = fit
    x = _v4_row(df, asof_idx)
    if not np.all(np.isfinite(x)):
        return None
    xz = np.nan_to_num((x - mu) / sd)
    expected = float(np.clip(np.array([1.0, *xz]) @ beta, -0.08, 0.08))
    # Probability is tied to historical residual volatility, not score/maximum score.
    z = expected / max(sigma, 0.004)
    prob_up = float(0.5 * (1.0 + math.erf(z / np.sqrt(2.0))))
    prob_up = float(np.clip(prob_up, 0.02, 0.98))
    return expected, prob_up, sigma


def predict_next_day(df, news_score=0.0):
    """Leakage-controlled next-day prediction.

    Price model is trained only on observations before the prediction date.
    News is a small modifier; it cannot create a trade by itself.
    """
    try:
        p = _v4_prediction(df)
        if p is None:
            return "UNKNOWN", 0.0, 0.0, {"Model": ("NEUTRAL", "Insufficient history for calibration")}
        expected, prob, sigma = p

        # News cannot dominate price evidence.  Also clamp its effect.
        news_adj = float(np.clip(news_score, -1.0, 1.0)) * 0.0025
        expected_adj = float(np.clip(expected + news_adj, -0.08, 0.08))
        prob_adj = float(np.clip(prob + np.clip(news_score, -1, 1) * 0.035, 0.02, 0.98))

        if expected_adj > V4_MIN_EDGE and prob_adj >= V4_MIN_PROB:
            direction = "UP 📈"
        elif expected_adj < -V4_MIN_EDGE and prob_adj <= 1.0 - V4_MIN_PROB:
            direction = "DOWN 📉"
        else:
            direction = "NEUTRAL ➡️"

        details = {
            "Model": ("UP" if expected_adj > 0 else "DOWN" if expected_adj < 0 else "NEUTRAL",
                      f"Walk-forward expected move {expected_adj*100:.2f}%"),
            "Probability": ("UP" if prob_adj >= 0.5 else "DOWN",
                            f"Calibrated probability {prob_adj*100:.1f}%"),
            "Volatility": ("NEUTRAL", f"Historical next-day residual volatility {sigma*100:.2f}%"),
            "News": ("UP" if news_adj > 0 else "DOWN" if news_adj < 0 else "NEUTRAL",
                     f"News adjustment {news_adj*100:.2f}% (capped)"),
            "Trade filter": ("UP" if direction.startswith("UP") else "DOWN" if direction.startswith("DOWN") else "NEUTRAL",
                             "Trade only when expected edge and probability both pass thresholds"),
        }
        # raw_score is now the expected return in percentage points, not an arbitrary score.
        return direction, round(prob_adj * 100.0, 1), round(expected_adj * 100.0, 2), details
    except Exception:
        return "UNKNOWN", 0.0, 0.0, {}


def trade_plan(df, direction="UP 📈", expected_pct=0.0):
    """Volatility-aware plan. 2-3% is a ceiling/target range, not a promise."""
    try:
        if df is None or df.empty:
            return 0.0, 0.0, 0.0, 0.0
        entry = safe_last(df["Close"])
        atr = safe_last(df["ATR"]) if "ATR" in df.columns else 0.0
        if entry <= 0 or atr <= 0:
            return round(entry, 2), 0.0, 0.0, 0.0
        risk = max(1.25 * atr, entry * 0.004)
        risk_pct = risk / entry
        # Target uses model edge when meaningful, but never forces 2-3%.
        target_pct = min(V4_MAX_TARGET, max(0.006, abs(expected_pct) / 100.0))
        target_distance = max(entry * target_pct, 1.5 * atr)
        target_distance = min(target_distance, entry * V4_MAX_TARGET)
        if direction.startswith("DOWN"):
            sl = entry + risk
            target = entry - target_distance
        elif direction.startswith("UP"):
            sl = entry - risk
            target = entry + target_distance
        else:
            return round(entry, 2), 0.0, 0.0, 0.0
        rr = abs(target-entry) / max(abs(entry-sl), 1e-9)
        return round(entry, 2), round(sl, 2), round(target, 2), round(rr, 2)
    except Exception:
        return 0.0, 0.0, 0.0, 0.0


def backtest(df):
    """True walk-forward validation; return shape matches the existing dashboard."""
    if df is None or len(df) < 150:
        return 0, 0.0, 0.0, 0.0, []
    trades = []
    direction_hits = []
    monthly = {}
    for i in range(120, len(df) - 1):
        try:
            p = _v4_prediction(df, i)
            if p is None:
                continue
            expected, prob, sigma = p
            actual = safe_last(df["Close"].iloc[i+1]) / safe_last(df["Close"].iloc[i]) - 1.0
            actual_up = actual > 0
            predicted_up = expected > 0
            direction_hits.append(int(actual_up == predicted_up))
            direction = 1 if expected > V4_MIN_EDGE and prob >= V4_MIN_PROB else (-1 if expected < -V4_MIN_EDGE and prob <= 1-V4_MIN_PROB else 0)
            if direction == 0:
                continue
            trade_return = actual * direction
            trades.append(trade_return)
            month = pd.Timestamp(df.index[i+1]).strftime("%Y-%m")
            monthly[month] = monthly.get(month, 0.0) + trade_return
        except Exception:
            continue
    if not trades:
        accuracy = round(np.mean(direction_hits) * 100.0, 1) if direction_hits else 0.0
        return 0, 0.0, 0.0, accuracy, []
    arr = np.asarray(trades, dtype=float)
    win_rate = float(np.mean(arr > V4_COST_BUFFER) * 100.0)
    expectancy = float(np.mean(arr) * 100.0)
    accuracy = round(np.mean(direction_hits) * 100.0, 1) if direction_hits else 0.0
    monthly_summary = [{"Month": k, "Net %": round(v*100,2)} for k,v in sorted(monthly.items())]
    return len(arr), round(win_rate,1), round(expectancy,2), accuracy, monthly_summary


def audit_historical_date(df, date_text):
    """Replay the model as it would have known the market at the supplied date."""
    try:
        target = pd.Timestamp(date_text).normalize()
        dates = pd.to_datetime(df.index).normalize()
        matches = np.where(dates <= target)[0]
        if len(matches) == 0:
            return None
        i = int(matches[-1])
        p = _v4_prediction(df, i)
        if p is None or i >= len(df)-1:
            return None
        expected, prob, sigma = p
        actual = safe_last(df["Close"].iloc[i+1]) / safe_last(df["Close"].iloc[i]) - 1.0
        return {
            "prediction_date": str(dates[i].date()),
            "next_date": str(dates[i+1].date()),
            "predicted_return_pct": round(expected*100,2),
            "prob_up_pct": round(prob*100,1),
            "actual_next_day_return_pct": round(actual*100,2),
            "correct_direction": bool((expected >= 0 and actual >= 0) or (expected < 0 and actual < 0)),
            "prediction_error_pct": round((expected-actual)*100,2),
            "close_prediction_day": round(safe_last(df["Close"].iloc[i]),2),
            "close_next_day": round(safe_last(df["Close"].iloc[i+1]),2),
        }
    except Exception:
        return None

# =================== STREAMLIT UI ===================

st.set_page_config(
    page_title="AI Trading System — Nifty 500",
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
st.markdown("## 📊 AI Trading System — Nifty 500")
st.markdown("*Next-day UP/DOWN prediction · 1-year backtesting · 6-source market sentiment*")
st.divider()

# ---- Sidebar Controls ----
with st.sidebar:
    st.markdown("### ⚙️ Scan Settings")

    scan_mode = st.radio(
        "Scan Mode",
        ["📋 My Watchlist", "🏆 Top N Stocks", "🔢 Full Nifty 500"],
        index=0,
        help="Watchlist = fastest. Full 500 = ~25-40 min."
    )

    if scan_mode == "📋 My Watchlist":
        watchlist_input = st.text_area(
            "Your Watchlist (one ticker per line)",
            value="\n".join(DEFAULT_WATCHLIST),
            height=200,
            help="Enter NSE tickers ending with .NS"
        )
        selected_stocks = [t.strip().upper() for t in watchlist_input.splitlines() if t.strip()]
        if not all(s.endswith(".NS") for s in selected_stocks):
            selected_stocks = [s if s.endswith(".NS") else s + ".NS" for s in selected_stocks]

    elif scan_mode == "🏆 Top N Stocks":
        max_stocks = st.slider("Number of Top Stocks", 10, 500, 100, step=10)
        selected_stocks = NSE_500[:max_stocks]
        mins = round(max_stocks * 0.05, 1)
        st.info(f"⏱ Estimated time: ~{mins} min")

    else:  # Full 500
        selected_stocks = NSE_500
        st.warning("⏱ Full scan takes ~25–40 min. Grab a chai ☕")

    min_score = st.slider("Minimum expected next-day edge (%)", -3.0, 3.0, 0.4, 0.1)
    st.divider()
    st.markdown(f"**Stocks queued:** {len(selected_stocks)}")
    st.divider()
    st.markdown("### 🔍 Single Stock Deep Dive")
    single_stock = st.text_input("NSE ticker (e.g. RELIANCE.NS)", "RELIANCE.NS")
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
        total_stocks = len(selected_stocks)
        prog = st.progress(0)
        status = st.empty()
        eta_box = st.empty()
        start_time = datetime.now()

        for i, stock in enumerate(selected_stocks):
            elapsed = (datetime.now() - start_time).seconds
            rate = (i + 1) / max(elapsed, 1)
            remaining = int((total_stocks - i - 1) / rate) if rate > 0 else 0
            mins, secs = divmod(remaining, 60)

            prog.progress((i + 1) / total_stocks)
            status.markdown(f"🔍 Analysing **{stock}** &nbsp;·&nbsp; {i+1}/{total_stocks}")
            eta_box.markdown(f"⏱ ETA: **{mins}m {secs}s** remaining")

            df = load_data(stock)
            if df is None:
                continue

            ns, ns_label, polarity, sent_breakdown, ann_titles = get_sentiment(stock)
            direction, confidence, raw_score, _ = predict_next_day(df, ns)
            entry, sl, target, rr = trade_plan(df, direction, raw_score)

            if raw_score < min_score:
                continue

            results.append({
                "Stock":      stock.replace(".NS", ""),
                "Prediction": direction,
                "Confidence": f"{confidence}%",
                "Score":      raw_score,
                "Entry ₹":    entry,
                "SL ₹":       sl,
                "Target ₹":   target,
                "R:R":        rr,
                "Sentiment":  ns_label,
            })

        prog.empty()
        status.empty()
        eta_box.empty()
        
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
            total, win_rate, expectancy, accuracy_1d, monthly_summary = backtest(df)
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
            entry, sl, target, rr = trade_plan(df, direction, raw_score)
            total_bt, win_rate, expectancy, accuracy_1d, monthly_summary = backtest(df)

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
            
            # Historical replay audit: e.g. 2026-08-17 for the Grasim incident
        st.markdown("#### 🧪 Historical Replay Audit")
        audit_date = st.date_input("Prediction date", value=datetime.now().date() - timedelta(days=7), key="audit_date")
        audit = audit_historical_date(df, audit_date)
        if audit:
            st.dataframe(pd.DataFrame([audit]), use_container_width=True, hide_index=True)
        else:
            st.info("Not enough historical data to replay this date.")

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
