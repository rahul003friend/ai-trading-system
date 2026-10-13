"""
AI Trading System — Nifty 500
Order Block + Smart Money Concept (SMC) + Multi-indicator prediction
Targets: +1% to +2% next-day moves with real NSE data
"""

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
from datetime import datetime
import feedparser
import warnings
warnings.filterwarnings("ignore")

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

# ==================== NIFTY 500 ====================
NSE_500 = [
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
    "ZOMATO.NS","DMART.NS","IRCTC.NS","TATACONSUM.NS","BAJAJ-AUTO.NS",
    "BOSCHLTD.NS","CHOLAFIN.NS","DLF.NS","FEDERALBNK.NS","GAIL.NS",
    "GODREJPROP.NS","IDFCFIRSTB.NS","INDUSTOWER.NS","INDIGO.NS","IOC.NS",
    "JUBLFOOD.NS","LICHSGFIN.NS","MUTHOOTFIN.NS","NMDC.NS","OFSS.NS",
    "PERSISTENT.NS","PNB.NS","RECLTD.NS","SAIL.NS","SBICARD.NS",
    "SBILIFE.NS","TATAPOWER.NS","TORNTPOWER.NS","UPL.NS","VOLTAS.NS",
    "ABB.NS","ACC.NS","ADANIGREEN.NS","ALKEM.NS","AMBUJACEM.NS",
    "AUROPHARMA.NS","BALKRISIND.NS","BANDHANBNK.NS","BANKBARODA.NS","BERGEPAINT.NS",
    "BIOCON.NS","CANBK.NS","COLPAL.NS","COROMANDEL.NS","CUMMINSIND.NS",
    "DEEPAKFERT.NS","DIXON.NS","GLENMARK.NS","GRANULES.NS","HDFCAMC.NS",
    "HDFCLIFE.NS","HINDPETRO.NS","ICICIGI.NS","ICICIPRULI.NS","IRFC.NS",
    "ISEC.NS","JKCEMENT.NS","KPITTECH.NS","LAURUSLABS.NS","LTIM.NS",
    "LTTS.NS","MANAPPURAM.NS","MCX.NS","MPHASIS.NS","MRF.NS",
    "NAUKRI.NS","NAVINFLUOR.NS","PAGEIND.NS","PETRONET.NS","PIDILITIND.NS",
    "POLYCAB.NS","RAMCOCEM.NS","RATNAMANI.NS","SCHAEFFLER.NS","SOLARINDS.NS",
    "SONACOMS.NS","STARHEALTH.NS","SUNTV.NS","SUPREMEIND.NS","TATACHEM.NS",
    "TATACOMM.NS","TRENT.NS","TRIDENT.NS","UNIONBANK.NS","VBL.NS",
    "WELCORP.NS","ZYDUSLIFE.NS","AAVAS.NS","ABCAPITAL.NS","ANGELONE.NS",
    "ASTRAL.NS","ATUL.NS","AUBANK.NS","BAJAJELEC.NS","BAJAJHLDNG.NS",
    "BATAINDIA.NS","BLUESTARCO.NS","CANFINHOME.NS","CARBORUNIV.NS","CDSL.NS",
    "COCHINSHIP.NS","CONCOR.NS","CROMPTON.NS","CYIENT.NS","DATAPATTNS.NS",
    "DELHIVERY.NS","ELGIEQUIP.NS","ENDURANCE.NS","EQUITASBNK.NS","FINEORG.NS",
    "GHCL.NS","GMDCLTD.NS","GNFC.NS","GODFRYPHLP.NS","GPIL.NS",
    "GRINDWELL.NS","GSFC.NS","GUJGASLTD.NS","HAPPSTMNDS.NS","HFCL.NS",
    "HINDCOPPER.NS","HOMEFIRST.NS","INDIAMART.NS","INDIANB.NS","INTELLECT.NS",
    "IRB.NS","JBCHEPHARM.NS","JKLAKSHMI.NS","JKPAPER.NS","JKTYRE.NS",
    "JSWENERGY.NS","KALPATPOWR.NS","KALYANKJIL.NS","KFINTECH.NS","KNRCON.NS",
    "KRBL.NS","LATENTVIEW.NS","LEMONTREE.NS","LICI.NS","LUXIND.NS",
    "MASFIN.NS","MEDANTA.NS","MIDHANI.NS","MOTHERSON.NS","NATCOPHARM.NS",
    "NBCC.NS","NCC.NS","NEWGEN.NS","NIACL.NS","NOCIL.NS",
    "OBEROIRLTY.NS","OLECTRA.NS","PCBL.NS","PFIZER.NS","PHOENIXLTD.NS",
    "PNBHOUSING.NS","POLYMED.NS","POONAWALLA.NS","PRESTIGE.NS","PVRINOX.NS",
    "RAILTEL.NS","RAINBOW.NS","RALLIS.NS","RAYMOND.NS","RBLBANK.NS",
    "REDINGTON.NS","ROSSARI.NS","ROUTE.NS","SAFARI.NS","SAREGAMA.NS",
    "SBFC.NS","SCHNEIDER.NS","SEQUENT.NS","SHILPAMED.NS","SOBHA.NS",
    "SPANDANA.NS","SPARC.NS","STARCEMENT.NS","STLTECH.NS","SUDARSCHEM.NS",
    "SUMICHEM.NS","SUNDARMFIN.NS","SUNDRMFAST.NS","SUZLON.NS","SYMPHONY.NS",
    "TARSONS.NS","TEAMLEASE.NS","THERMAX.NS","THYROCARE.NS","TIMKEN.NS",
    "TITAGARH.NS","TVSMOTOR.NS","UTIAMC.NS","VAIBHAVGBL.NS","VINATIORGA.NS",
    "VSTIND.NS","WABCOINDIA.NS","WELSPUNIND.NS","WESTLIFE.NS","ZENSARTECH.NS",
    "AARTIIND.NS","ABBOTINDIA.NS","AIAENG.NS","AJANTPHARM.NS","ALKYLAMINE.NS",
    "ALLCARGO.NS","AMARAJABAT.NS","ANANTRAJ.NS","APARINDS.NS","APOLLOTYRE.NS",
    "ASHOKLEY.NS","ASTERDM.NS","AVANTIFEED.NS","BAJAJCON.NS","BALMLAWRIE.NS",
    "BASF.NS","BAYERCROP.NS","BEML.NS","BHARATFORG.NS","BHEL.NS",
    "BIKAJI.NS","BIRLACORPN.NS","BRIGADE.NS","BSE.NS","CAMLINFINE.NS",
    "CAPLIPOINT.NS","CARERATING.NS","CASTROLIND.NS","CEATLTD.NS","CENTURYPLY.NS",
    "CENTURYTEX.NS","CERA.NS","CHALET.NS","CHAMBLFERT.NS","CHEMPLASTS.NS",
    "CLEAN.NS","CRAFTSMAN.NS","DEVYANI.NS","EIHOTEL.NS","ENGINERSIN.NS",
    "GARFIBRES.NS","GLOBUSSPR.NS","GMRINFRA.NS","HBLPOWER.NS","HIMATSEIDE.NS",
    "HINDWAREAP.NS","IBREALEST.NS","IIFL.NS","IMFA.NS","INDIACEM.NS",
    "INDIGOPNTS.NS","INDOCO.NS","IONEXCHANG.NS","IRB.NS","ISGEC.NS",
    "JBMA.NS","JMFINANCIL.NS","JUBILANT.NS","KANSAINER.NS","KOLTEPATIL.NS",
    "KSCL.NS","LAXMIMACH.NS","LLOYDSENGG.NS","MAHLOG.NS","MAYURUNIQ.NS",
    "MMTC.NS","MOREPENLAB.NS","MUTHOOTMF.NS","NAVA.NS","NESCO.NS",
    "NETWORK18.NS","NIPPOBATRY.NS","ORIENTELEC.NS","PATELENG.NS","PILANIINVS.NS",
    "PRAJIND.NS","PRINCEPIPE.NS","PRSMJOHNSN.NS","PSPPROJECT.NS","RAIN.NS",
    "RAJESHEXPO.NS","RHIM.NS","RKFORGE.NS","RRKABEL.NS","SANDHAR.NS",
    "SANGHIIND.NS","SANOFI.NS","SAPPHIRE.NS","SARDAEN.NS","SKIPPER.NS",
    "SMLISUZU.NS","SOLARA.NS","SPENCERS.NS","STCINDIA.NS","SUNCLAYLTD.NS",
    "SUNFLAG.NS","SURYAROSNI.NS","SUVENPHAR.NS","SUZLON.NS","SWANENERGY.NS",
    "TCNSBRANDS.NS","UCOBANK.NS","UJJIVANSFB.NS","UNITDSPR.NS","VGUARD.NS",
    "VENKEYS.NS","VESUVIUS.NS","VINATIORGA.NS","VLSFINANCE.NS","WALCHANNAG.NS",
    "WEIZMANIND.NS","WONDERLA.NS","YATHARTH.NS","ZODIACLOTH.NS","ZUARI.NS",
]

DEFAULT_WATCHLIST = [
    "RELIANCE.NS","TCS.NS","INFY.NS","HDFCBANK.NS","SBIN.NS",
    "ICICIBANK.NS","LT.NS","TATAMOTORS.NS","WIPRO.NS","BAJFINANCE.NS"
]

# ==================== HELPERS ====================
def flt(x, idx=-1):
    try:
        if isinstance(x, (pd.DataFrame, pd.Series)):
            s = x.dropna()
            if isinstance(s, pd.DataFrame): s = s.iloc[:,0]
            return float(s.iloc[idx]) if len(s) > abs(idx) else 0.0
        return float(x)
    except: return 0.0

def prep(df, min_rows=60):
    if df is None or df.empty: return None
    df = df.copy()
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    for c in ["Open","High","Low","Close","Volume"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    df = df.dropna(subset=["Close"])
    return df if len(df) >= min_rows else None

# ==================== DATA LOADER ====================
@st.cache_data(ttl=3600, show_spinner=False)
def load_data(stock):
    try:
        df = yf.download(stock, period="1y", progress=False, auto_adjust=True)
        df = prep(df)
        if df is None: return None
        c = df["Close"]; v = df["Volume"]
        df["MA20"]   = c.rolling(20).mean()
        df["MA50"]   = c.rolling(50).mean()
        df["MA200"]  = c.rolling(200).mean()
        df["EMA9"]   = EMAIndicator(c, window=9).ema_indicator()
        df["EMA21"]  = EMAIndicator(c, window=21).ema_indicator()
        df["RSI"]    = RSIIndicator(c, window=14).rsi()
        st_          = StochasticOscillator(df["High"], df["Low"], c)
        df["SK"]     = st_.stoch()
        df["SD"]     = st_.stoch_signal()
        mc           = MACD(c)
        df["MACD"]   = mc.macd()
        df["MACDS"]  = mc.macd_signal()
        df["MACDH"]  = mc.macd_diff()
        df["ATR"]    = AverageTrueRange(df["High"], df["Low"], c).average_true_range()
        bb           = BollingerBands(c)
        df["BBU"]    = bb.bollinger_hband()
        df["BBL"]    = bb.bollinger_lband()
        df["BBM"]    = bb.bollinger_mavg()
        df["OBV"]    = OnBalanceVolumeIndicator(c, v).on_balance_volume()
        df["VMA"]    = v.rolling(20).mean()
        df["R1"]     = c.pct_change(1)
        df["R5"]     = c.pct_change(5)
        df["R20"]    = c.pct_change(20)
        df["H52"]    = c.rolling(252).max()
        df["L52"]    = c.rolling(252).min()
        return df
    except: return None

# ==================== ORDER BLOCK DETECTION ====================
# Based on Smart Money Concept (SMC) / ICT methodology:
# Bullish OB = last BEARISH candle before a strong BULLISH impulse (break of structure UP)
# Bearish OB = last BULLISH candle before a strong BEARISH impulse (break of structure DOWN)

def detect_order_blocks(df, lookback=50, impulse_threshold=0.015):
    """
    Detect the most recent valid bullish and bearish order blocks.
    Returns list of dicts with ob_type, ob_high, ob_low, ob_date, strength, tested
    """
    if df is None or len(df) < lookback + 5:
        return [], []

    obs_bull = []
    obs_bear = []

    try:
        recent = df.tail(lookback).copy()
        opens  = recent["Open"].values
        highs  = recent["High"].values
        lows   = recent["Low"].values
        closes = recent["Close"].values
        vols   = recent["Volume"].values
        vmean  = float(recent["VMA"].dropna().iloc[-1]) if "VMA" in recent.columns else 1
        dates  = recent.index

        for i in range(3, len(recent) - 3):
            # ── BULLISH ORDER BLOCK ──────────────────────────────────────────
            # Condition: candle i is BEARISH (close < open)
            # AND next 1-3 candles form a sharp impulse UP (break structure)
            if closes[i] < opens[i]:  # bearish candle
                # Check impulse: next candle(s) move > threshold up
                impulse_hi = max(highs[i+1:i+4])
                impulse_lo = min(lows[i+1:i+4])
                body_size  = opens[i] - closes[i]
                move_up    = (impulse_hi - highs[i]) / (closes[i] + 0.001)

                if move_up > impulse_threshold:
                    # Volume confirmation: OB candle should have above-average volume
                    vol_ratio = vols[i] / (vmean + 1)
                    strength  = round(min(100, move_up * 100 * vol_ratio * 10), 1)

                    ob_high = opens[i]    # OB zone: from candle open to high
                    ob_low  = closes[i]   # or low of the candle

                    # Check if current price is retesting the OB zone
                    curr_price = closes[-1]
                    tested = ob_low <= curr_price <= ob_high * 1.01

                    # Only keep if OB is above current price (demand zone) or being retested
                    if curr_price <= ob_high * 1.02:
                        obs_bull.append({
                            "type":     "Bullish OB 🟢",
                            "ob_high":  round(ob_high, 2),
                            "ob_low":   round(ob_low,  2),
                            "date":     str(dates[i].date()) if hasattr(dates[i], "date") else str(dates[i]),
                            "strength": strength,
                            "tested":   "✅ Retesting" if tested else "⏳ Awaiting retest",
                            "move_pct": round(move_up * 100, 2),
                            "vol_ratio":round(vol_ratio, 2),
                        })

            # ── BEARISH ORDER BLOCK ──────────────────────────────────────────
            # Condition: candle i is BULLISH (close > open)
            # AND next 1-3 candles form a sharp impulse DOWN
            if closes[i] > opens[i]:  # bullish candle
                impulse_lo = min(lows[i+1:i+4])
                move_down  = (lows[i] - impulse_lo) / (closes[i] + 0.001)

                if move_down > impulse_threshold:
                    vol_ratio = vols[i] / (vmean + 1)
                    strength  = round(min(100, move_down * 100 * vol_ratio * 10), 1)

                    ob_high = closes[i]
                    ob_low  = opens[i]

                    curr_price = closes[-1]
                    tested = ob_low * 0.99 <= curr_price <= ob_high

                    if curr_price >= ob_low * 0.98:
                        obs_bear.append({
                            "type":     "Bearish OB 🔴",
                            "ob_high":  round(ob_high, 2),
                            "ob_low":   round(ob_low,  2),
                            "date":     str(dates[i].date()) if hasattr(dates[i], "date") else str(dates[i]),
                            "strength": strength,
                            "tested":   "✅ Retesting" if tested else "⏳ Awaiting retest",
                            "move_pct": round(move_down * 100, 2),
                            "vol_ratio":round(vol_ratio, 2),
                        })

        # Sort by strength, keep top 3 each
        obs_bull = sorted(obs_bull, key=lambda x: x["strength"], reverse=True)[:3]
        obs_bear = sorted(obs_bear, key=lambda x: x["strength"], reverse=True)[:3]

    except: pass

    return obs_bull, obs_bear


def ob_signal(obs_bull, obs_bear, curr_price, atr):
    """
    Determine if price is currently inside or approaching a valid OB.
    Returns: signal (+1 bullish, -1 bearish, 0 neutral), description, score
    """
    sig = 0; desc = "No active OB signal"; score = 0

    try:
        # Check bullish OBs — price retesting demand zone
        for ob in obs_bull:
            if ob["tested"] == "✅ Retesting":
                dist = (curr_price - ob["ob_low"]) / (atr + 0.001)
                if dist <= 1.5:  # within 1.5 ATR of OB
                    score = min(4, round(ob["strength"] / 25))
                    sig  = 1
                    desc = f"Price retesting Bullish OB zone {ob['ob_low']}–{ob['ob_high']} (strength {ob['strength']})"
                    break

        # Check bearish OBs — price retesting supply zone
        if sig == 0:
            for ob in obs_bear:
                if ob["tested"] == "✅ Retesting":
                    dist = (ob["ob_high"] - curr_price) / (atr + 0.001)
                    if dist <= 1.5:
                        score = -min(4, round(ob["strength"] / 25))
                        sig  = -1
                        desc = f"Price retesting Bearish OB zone {ob['ob_low']}–{ob['ob_high']} (strength {ob['strength']})"
                        break

        # Approaching bullish OB (within 2 ATR below)
        if sig == 0:
            for ob in obs_bull:
                proximity = (ob["ob_high"] - curr_price) / (atr + 0.001)
                if 0 < proximity <= 2:
                    score = 2
                    sig  = 1
                    desc = f"Price approaching Bullish OB {ob['ob_low']}–{ob['ob_high']} (buy zone near)"
                    break

    except: pass

    return sig, desc, score


# ==================== BREAK OF STRUCTURE ====================
def detect_bos(df, lookback=30):
    """
    Break of Structure (BOS):
    Bullish BOS = price breaks above previous swing high (higher high)
    Bearish BOS = price breaks below previous swing low (lower low)
    """
    if df is None or len(df) < lookback + 5:
        return "NEUTRAL", 0, "Insufficient data"
    try:
        recent  = df.tail(lookback)
        highs   = recent["High"].values
        lows    = recent["Low"].values
        closes  = recent["Close"].values
        curr    = closes[-1]

        # Find swing high/low in the middle section (exclude last 5 bars)
        mid_highs = highs[:-5]
        mid_lows  = lows[:-5]

        swing_high = float(np.max(mid_highs))
        swing_low  = float(np.min(mid_lows))

        if curr > swing_high * 1.001:
            strength = round((curr - swing_high) / swing_high * 100, 2)
            return "BULLISH BOS 🔼", 3, f"Price {curr:.1f} broke above swing high {swing_high:.1f} (+{strength}%)"
        elif curr < swing_low * 0.999:
            strength = round((swing_low - curr) / swing_low * 100, 2)
            return "BEARISH BOS 🔽", -3, f"Price {curr:.1f} broke below swing low {swing_low:.1f} (-{strength}%)"
        else:
            pct_hi = round((swing_high - curr) / swing_high * 100, 2)
            return "RANGING", 0, f"Inside range. {pct_hi}% below swing high {swing_high:.1f}"
    except:
        return "NEUTRAL", 0, "BOS detection error"


# ==================== FAIR VALUE GAP ====================
def detect_fvg(df, lookback=20):
    """
    Fair Value Gap (FVG) / Imbalance:
    Bullish FVG: candle[i-1].high < candle[i+1].low (gap upward)
    Bearish FVG: candle[i-1].low > candle[i+1].high (gap downward)
    """
    fvgs = []
    if df is None or len(df) < lookback + 3:
        return fvgs
    try:
        recent = df.tail(lookback + 3)
        highs  = recent["High"].values
        lows   = recent["Low"].values
        closes = recent["Close"].values
        dates  = recent.index
        curr   = closes[-1]

        for i in range(1, len(recent)-1):
            # Bullish FVG
            if highs[i-1] < lows[i+1]:
                gap_mid = (highs[i-1] + lows[i+1]) / 2
                if lows[-1] <= gap_mid * 1.02:  # price approaching or in gap
                    fvgs.append({
                        "type":    "Bullish FVG ⬆️",
                        "upper":   round(lows[i+1], 2),
                        "lower":   round(highs[i-1], 2),
                        "gap_mid": round(gap_mid, 2),
                        "date":    str(dates[i].date()) if hasattr(dates[i],"date") else "",
                        "filled":  curr >= highs[i-1],
                    })
            # Bearish FVG
            if lows[i-1] > highs[i+1]:
                gap_mid = (lows[i-1] + highs[i+1]) / 2
                if closes[-1] >= gap_mid * 0.98:
                    fvgs.append({
                        "type":    "Bearish FVG ⬇️",
                        "upper":   round(lows[i-1], 2),
                        "lower":   round(highs[i+1], 2),
                        "gap_mid": round(gap_mid, 2),
                        "date":    str(dates[i].date()) if hasattr(dates[i],"date") else "",
                        "filled":  curr <= lows[i-1],
                    })
    except: pass
    return fvgs[-4:] if len(fvgs) > 4 else fvgs


# ==================== SENTIMENT ====================
def _pol(txt):
    try: return TextBlob(str(txt)[:2000]).sentiment.polarity
    except: return 0.0

def _google(sym):
    try:
        q = sym.replace(".NS","").replace("-","").replace("&","")
        f = feedparser.parse(f"https://news.google.com/rss/search?q={q}+NSE+India+stock&hl=en-IN&gl=IN&ceid=IN:en")
        t = " ".join(e.get("title","")+" "+e.get("summary","") for e in f.entries[:12])
        return _pol(t)
    except: return 0.0

def _mc(sym):
    try:
        q = sym.replace(".NS","").replace("-","").lower()
        f = feedparser.parse(f"https://www.moneycontrol.com/rss/results.xml?search={q}")
        t = " ".join(e.get("title","")+" "+e.get("summary","") for e in f.entries[:8])
        return _pol(t)
    except: return 0.0

def _dsc(sym):
    try:
        q = sym.replace(".NS","").replace("-","").replace("&","")
        r = requests.get(f"https://www.dscindia.com/search?q={q}", timeout=6, headers=HEADERS)
        soup = BeautifulSoup(r.text,"html.parser")
        t = " ".join(x.get_text(" ",strip=True) for x in soup.find_all(["p","h2","h3"])[:20])
        return _pol(t)
    except: return 0.0

def _nse(sym):
    try:
        s = sym.replace(".NS","").replace("-","").replace("&","")
        r = requests.get(
            f"https://www.nseindia.com/api/corp-info?symbol={s}&corpType=announcements&market=equities",
            timeout=6, headers={**HEADERS,"Referer":"https://www.nseindia.com/","Accept":"application/json"})
        items = r.json().get("data",[])[:8]
        titles= [i.get("subject","")+" "+i.get("desc","") for i in items]
        txt   = " ".join(titles)
        pol   = _pol(txt)
        pos   = ["dividend","bonus","buyback","profit","order","partnership","record","award"]
        neg   = ["loss","penalty","fraud","investigation","default","downgrade","delay","fire"]
        pol  += sum(0.1 for k in pos if k in txt.lower())
        pol  -= sum(0.1 for k in neg if k in txt.lower())
        return max(-1.0, min(1.0, pol)), titles[:4]
    except: return 0.0, []

def get_sentiment(stock):
    nse_p, ann = _nse(stock)
    raw = {"NSE Corp":nse_p, "DSC India":_dsc(stock), "MoneyControl":_mc(stock), "Google News":_google(stock)}
    wts = {"NSE Corp":0.40, "DSC India":0.25, "MoneyControl":0.20, "Google News":0.15}
    comp = sum(raw[k]*wts[k] for k in wts)
    score = round(comp * 15, 2)
    label = "🟢 Positive" if score>2 else ("🔴 Negative" if score<-2 else "🟡 Neutral")
    bd = {k:{"polarity":round(raw[k],3),"weight":f"{int(wts[k]*100)}%",
             "signal":"🟢" if raw[k]>0.05 else("🔴" if raw[k]<-0.05 else "🟡")} for k in wts}
    return score, label, round(comp,3), bd, ann


# ==================== PREDICTION ENGINE ====================
def predict(df, news_score):
    """
    Hybrid model: Order Block + BOS + FVG + Classic indicators + Sentiment
    Only outputs UP when score >= 5 (targets +1-2% moves)
    """
    if df is None or len(df) < 60:
        return "UNKNOWN", 0, 0.0, {}

    score = 0.0
    MAX   = 24.0
    det   = {}

    try:
        def sv(col, k=-1):
            try:
                s = df[col].dropna()
                return float(s.iloc[k]) if len(s) > abs(k) else 0.0
            except: return 0.0

        cl   = sv("Close");  cl1 = sv("Close",-2); cl5 = sv("Close",-5)
        op   = sv("Open");   hi  = sv("High");      lo  = sv("Low")
        ma20 = sv("MA20");   ma50= sv("MA50");      ma200=sv("MA200")
        e9   = sv("EMA9");   e21 = sv("EMA21")
        e9_1 = sv("EMA9",-2);e21_1=sv("EMA21",-2)
        rsi  = sv("RSI");    rsi1= sv("RSI",-2)
        sk   = sv("SK");     sd  = sv("SD")
        sk1  = sv("SK",-2);  sd1 = sv("SD",-2)
        macd = sv("MACD");   ms  = sv("MACDS");     mh  = sv("MACDH")
        macd1= sv("MACD",-2);ms1 = sv("MACDS",-2); mh1 = sv("MACDH",-2)
        bbu  = sv("BBU");    bbl = sv("BBL");        bbm = sv("BBM")
        atr  = sv("ATR");    obv = sv("OBV");        obv5= sv("OBV",-5); obv10=sv("OBV",-10)
        vol  = sv("Volume"); vma = sv("VMA")
        r1   = sv("R1");     r5  = sv("R5");         r20 = sv("R20")
        h52  = sv("H52")
        vr   = vol / (vma + 1)

        # ── A. ORDER BLOCK (±4) — Institutional footprint ─────────────────
        obs_bull, obs_bear = detect_order_blocks(df)
        ob_sig, ob_desc, ob_sc = ob_signal(obs_bull, obs_bear, cl, atr)
        score += ob_sc
        det["A. Order Block"] = (
            "UP" if ob_sig > 0 else ("DOWN" if ob_sig < 0 else "NEUTRAL"),
            ob_desc
        )

        # ── B. BREAK OF STRUCTURE (±3) — Market structure confirmation ────
        bos_lbl, bos_sc, bos_desc = detect_bos(df)
        score += bos_sc
        det["B. Break of Structure"] = (
            "UP" if bos_sc > 0 else ("DOWN" if bos_sc < 0 else "NEUTRAL"),
            f"{bos_lbl} — {bos_desc}"
        )

        # ── C. FAIR VALUE GAP (±2) — Imbalance fill ───────────────────────
        fvgs = detect_fvg(df)
        fvg_sc = 0
        fvg_desc = "No active FVG near price"
        for fvg in fvgs:
            if "Bullish" in fvg["type"] and not fvg["filled"]:
                fvg_sc = 2; fvg_desc = f"Price in/near {fvg['type']} {fvg['lower']}–{fvg['upper']}"; break
            elif "Bearish" in fvg["type"] and not fvg["filled"]:
                fvg_sc = -2; fvg_desc = f"Price in/near {fvg['type']} {fvg['lower']}–{fvg['upper']}"; break
        score += fvg_sc
        det["C. Fair Value Gap"] = ("UP" if fvg_sc>0 else ("DOWN" if fvg_sc<0 else "NEUTRAL"), fvg_desc)

        # ── 1. TREND (±3) ─────────────────────────────────────────────────
        if ma20>ma50>ma200:     score+=3; det["1. Trend"]=("UP",   "MA20>MA50>MA200 strong uptrend")
        elif ma20<ma50<ma200:   score-=3; det["1. Trend"]=("DOWN", "MA20<MA50<MA200 strong downtrend")
        elif ma20>ma50:         score+=1; det["1. Trend"]=("UP",   "Short-term uptrend")
        elif ma20<ma50:         score-=1; det["1. Trend"]=("DOWN", "Short-term downtrend")
        else:                             det["1. Trend"]=("NEUTRAL","Flat MAs")

        # ── 2. EMA CROSS (±2) ─────────────────────────────────────────────
        if e9>e21 and e9_1<=e21_1:   score+=2; det["2. EMA Cross"]=("UP",   "🔔 Fresh EMA9 crossover above EMA21")
        elif e9<e21 and e9_1>=e21_1: score-=2; det["2. EMA Cross"]=("DOWN", "🔔 Fresh EMA9 crossunder below EMA21")
        elif e9>e21:                  score+=1; det["2. EMA Cross"]=("UP",   "EMA9 above EMA21")
        else:                         score-=1; det["2. EMA Cross"]=("DOWN", "EMA9 below EMA21")

        # ── 3. RSI + DIVERGENCE (±3) ──────────────────────────────────────
        bull_div=(cl<cl5)and(rsi>rsi1); bear_div=(cl>cl5)and(rsi<rsi1)
        if 52<=rsi<68:   score+=3; det["3. RSI"]=("UP",   f"RSI={rsi:.1f} ideal bullish zone")
        elif 68<=rsi<75: score+=1; det["3. RSI"]=("UP",   f"RSI={rsi:.1f} strong but getting hot")
        elif rsi>=75:
            score-=2
            if bear_div: score-=1; det["3. RSI"]=("DOWN",f"RSI={rsi:.1f} overbought + bearish divergence ⚠️")
            else:                   det["3. RSI"]=("DOWN",f"RSI={rsi:.1f} overbought")
        elif rsi<40:
            if bull_div: score+=2; det["3. RSI"]=("UP",f"RSI={rsi:.1f} oversold + bullish divergence 🔔")
            else:                   det["3. RSI"]=("NEUTRAL",f"RSI={rsi:.1f} oversold, wait for signal")
        else: score-=1; det["3. RSI"]=("DOWN",f"RSI={rsi:.1f} below 52 — weak")

        # ── 4. MACD (±3) ──────────────────────────────────────────────────
        fu=(macd>ms)and(macd1<=ms1); fd=(macd<ms)and(macd1>=ms1)
        if fu:            score+=3; det["4. MACD"]=("UP",   f"🔔 Fresh MACD bullish crossover")
        elif fd:          score-=3; det["4. MACD"]=("DOWN", f"🔔 Fresh MACD bearish crossover")
        elif macd>ms and mh>mh1: score+=2; det["4. MACD"]=("UP",f"Bullish histogram expanding ({mh:.2f})")
        elif macd>ms:     score+=1; det["4. MACD"]=("UP",   f"MACD positive ({mh:.2f})")
        elif macd<ms and mh<mh1: score-=2; det["4. MACD"]=("DOWN",f"Bearish histogram expanding ({mh:.2f})")
        else:             score-=1; det["4. MACD"]=("DOWN", f"MACD negative ({mh:.2f})")

        # ── 5. STOCHASTIC (±2) ────────────────────────────────────────────
        cu=(sk>sd)and(sk1<=sd1); cd=(sk<sd)and(sk1>=sd1)
        if cu and sk<80:   score+=2; det["5. Stochastic"]=("UP",   f"🔔 Stoch bullish cross K={sk:.1f}")
        elif cd and sk>20: score-=2; det["5. Stochastic"]=("DOWN", f"🔔 Stoch bearish cross K={sk:.1f}")
        elif sk>sd and sk<80: score+=1; det["5. Stochastic"]=("UP",f"K above D ({sk:.1f})")
        elif sk<sd and sk>20: score-=1; det["5. Stochastic"]=("DOWN",f"K below D ({sk:.1f})")
        else: det["5. Stochastic"]=("NEUTRAL",f"Extreme zone K={sk:.1f}")

        # ── 6. VOLUME (±2) ────────────────────────────────────────────────
        if vr>=1.5 and r1>0.005:   score+=2; det["6. Volume"]=("UP",  f"Strong volume {vr:.1f}x on up move ✅")
        elif vr>=1.5 and r1<-0.005:score-=2; det["6. Volume"]=("DOWN",f"Strong volume {vr:.1f}x on down move ❌")
        elif vr>=1.2 and r1>0:     score+=1; det["6. Volume"]=("UP",  f"Moderate volume {vr:.1f}x confirms up")
        elif vr<0.7 and r1>0.01:   score-=1; det["6. Volume"]=("DOWN",f"Low-volume rally {vr:.1f}x — weak ⚠️")
        else: det["6. Volume"]=("NEUTRAL",f"Vol ratio {vr:.1f}x")

        # ── 7. OBV (±2) ───────────────────────────────────────────────────
        if obv>sv("OBV",-5)>obv10:  score+=2; det["7. OBV"]=("UP",  "OBV rising — accumulation")
        elif obv<sv("OBV",-5)<obv10:score-=2; det["7. OBV"]=("DOWN","OBV falling — distribution")
        elif obv>obv10:              score+=1; det["7. OBV"]=("UP",  "OBV net positive 10D")
        else:                        score-=1; det["7. OBV"]=("DOWN","OBV net negative 10D")

        # ── 8. BB SQUEEZE (±2) ────────────────────────────────────────────
        bw = (bbu-bbl)/(bbm+0.001)
        bp = (cl-bbl)/(bbu-bbl+0.001)
        bws= ((df["BBU"]-df["BBL"])/(df["BBM"]+0.001)).dropna()
        sq = bw < float(bws.quantile(0.20)) if len(bws)>20 else False
        if sq and r1>0.005:    score+=2; det["8. Bollinger"]=("UP",  "BB Squeeze breakout UP ⚡")
        elif sq and r1<-0.005: score-=2; det["8. Bollinger"]=("DOWN","BB Squeeze breakout DOWN ⚡")
        elif bp>0.75 and vr>1.2: score+=1; det["8. Bollinger"]=("UP",f"Upper band + volume ({bp:.0%})")
        elif bp<0.25 and vr>1.2: score-=1; det["8. Bollinger"]=("DOWN",f"Lower band + volume ({bp:.0%})")
        else: det["8. Bollinger"]=("NEUTRAL",f"BB position {bp:.0%}")

        # ── 9. MOMENTUM (±2) ──────────────────────────────────────────────
        if r5>0.03 and r20>0.05:   score+=2; det["9. Momentum"]=("UP",  f"5D={r5:.1%} 20D={r20:.1%} strong")
        elif r5>0.015:             score+=1; det["9. Momentum"]=("UP",  f"5D positive ({r5:.1%})")
        elif r5<-0.03 and r20<-0.05:score-=2;det["9. Momentum"]=("DOWN",f"5D={r5:.1%} 20D={r20:.1%} weak")
        elif r5<-0.015:            score-=1; det["9. Momentum"]=("DOWN",f"5D negative ({r5:.1%})")
        else: det["9. Momentum"]=("NEUTRAL",f"5D={r5:.1%}")

        # ── 10. NEWS SENTIMENT (±3) ───────────────────────────────────────
        ns = max(-3.0, min(3.0, news_score / 5.0))
        score += ns
        det["10. Sentiment"]=(
            "UP" if ns>0.5 else ("DOWN" if ns<-0.5 else "NEUTRAL"),
            f"Composite score {news_score:.2f}"
        )

    except: return "UNKNOWN", 0, 0.0, {}

    conf = round(min(97, max(3, (score + MAX)/(2*MAX)*100)), 1)

    # HIGH bar: require score >= 5 for UP to target 1-2% move
    if score >= 5:     direction = "UP 📈"
    elif score <= -5:  direction = "DOWN 📉"
    else:              direction = "NEUTRAL ➡️"

    return direction, conf, round(score, 2), det


# ==================== TRADE PLAN ====================
def trade_plan(df, direction):
    try:
        cl  = flt(df["Close"])
        atr = flt(df["ATR"])
        if atr == 0: atr = cl * 0.01

        if "UP" in direction:
            sl  = round(cl - 1.5 * atr, 2)
            tgt = round(cl + 2.0 * atr, 2)   # targets ~1-2% up move
        elif "DOWN" in direction:
            sl  = round(cl + 1.5 * atr, 2)
            tgt = round(cl - 2.0 * atr, 2)
        else:
            sl = tgt = cl

        rr = round(abs(tgt-cl)/abs(cl-sl), 2) if cl != sl else 0
        move_pct = round((tgt - cl) / cl * 100, 2)
        return round(cl,2), sl, tgt, rr, move_pct
    except: return 0, 0, 0, 0, 0


# ==================== BACKTEST ====================
def backtest(df):
    if df is None or len(df) < 80:
        return 0, 0.0, 0.0, 0.0, []

    trades=[]; correct=0; total_1m=0
    in_trade=False; t_entry=t_sl=t_tgt=0.0
    monthly={}

    try:
        for i in range(60, len(df)-1):
            sub = df.iloc[:i]
            if len(sub)<60: continue

            def sv(col, k=-1):
                try:
                    s=sub[col].dropna()
                    return float(s.iloc[k]) if len(s)>abs(k) else 0.0
                except: return 0.0

            ma20=sv("MA20"); ma50=sv("MA50"); ma200=sv("MA200")
            e9=sv("EMA9"); e21=sv("EMA21")
            e9_1=sv("EMA9",-2); e21_1=sv("EMA21",-2)
            rsi=sv("RSI")
            macd=sv("MACD"); ms=sv("MACDS"); mh=sv("MACDH")
            macd1=sv("MACD",-2); ms1=sv("MACDS",-2)
            obv=sv("OBV"); obv10=sv("OBV",-10)
            vol=sv("Volume"); vma=sv("VMA")
            r1=sv("R1"); cl=sv("Close"); atr=sv("ATR")
            vr=vol/(vma+1)

            sig=0.0
            if ma20>ma50>ma200: sig+=3
            elif ma20<ma50<ma200: sig-=3
            elif ma20>ma50: sig+=1
            else: sig-=1
            if e9>e21 and e9_1<=e21_1: sig+=2
            elif e9<e21 and e9_1>=e21_1: sig-=2
            elif e9>e21: sig+=1
            else: sig-=1
            if 52<=rsi<68: sig+=3
            elif rsi>=75: sig-=2
            elif rsi<40: sig+=0
            else: sig-=1
            if (macd>ms)and(macd1<=ms1): sig+=3
            elif (macd<ms)and(macd1>=ms1): sig-=3
            elif macd>ms: sig+=1
            else: sig-=1
            if vr>=1.5 and r1>0.005: sig+=2
            elif vr>=1.5 and r1<-0.005: sig-=2
            if obv>sv("OBV",-5): sig+=1
            else: sig-=1

            pred_up = sig >= 5
            pred_dn = sig <= -5

            next_cl = float(df["Close"].iloc[i+1]) if i+1<len(df) else cl
            act_up  = next_cl > cl * 1.005

            if i >= len(df)-23:
                total_1m += 1
                if (pred_up and act_up) or (pred_dn and not act_up):
                    correct += 1

            nlo = float(df["Low"].iloc[i+1])  if i+1<len(df) else cl
            nhi = float(df["High"].iloc[i+1]) if i+1<len(df) else cl
            mkey = df.index[i].strftime("%Y-%m") if hasattr(df.index[i],"strftime") else "unknown"

            if not in_trade and pred_up and atr>0:
                in_trade=True
                t_entry=next_cl
                t_sl=t_entry-1.5*atr
                t_tgt=t_entry+2.0*atr
            elif in_trade:
                if nlo<=t_sl:
                    trades.append(-1); monthly[mkey]=monthly.get(mkey,0)-1; in_trade=False
                elif nhi>=t_tgt:
                    trades.append(1);  monthly[mkey]=monthly.get(mkey,0)+2; in_trade=False

        total  = len(trades)
        wins   = trades.count(1); losses=trades.count(-1)
        wr     = round(wins/total*100,1)       if total>0 else 0.0
        exp    = round((wins*2-losses)/total,2) if total>0 else 0.0
        acc1m  = round(correct/total_1m*100,1) if total_1m>0 else 0.0
        mtbl   = [{"Month":k,"Net R":v,"Result":"✅" if v>0 else "❌"} for k,v in sorted(monthly.items())]
        return total, wr, exp, acc1m, mtbl
    except: return 0, 0.0, 0.0, 0.0, []


# ==================== INTRADAY ====================
@st.cache_data(ttl=300, show_spinner=False)
def load_intra(stock):
    try:
        df = yf.download(stock, period="1d", interval="5m", progress=False, auto_adjust=True)
        return prep(df, min_rows=10)
    except: return None

def intra_signal(df):
    try:
        if df is None or len(df)<15: return None
        oh = float(df["High"].iloc[:3].max())
        ol = float(df["Low"].iloc[:3].min())
        cl = float(df["Close"].iloc[-1])
        vr = float(df["Volume"].iloc[-3:].sum())/(float(df["Volume"].mean())+1)
        if cl>oh and vr>1.3:
            sl=round(ol,2); tgt=round(cl+(cl-sl)*1.5,2)
            return "BUY 🟢", round(cl,2), sl, tgt
        if cl<ol and vr>1.3:
            sl=round(oh,2); tgt=round(cl-(sl-cl)*1.5,2)
            return "SELL 🔴", round(cl,2), sl, tgt
        return "WAIT ⏳", round(cl,2), 0, 0
    except: return None


# ==================== UI ====================
st.set_page_config(page_title="AI Trading — Nifty 500", page_icon="📊",
                   layout="wide", initial_sidebar_state="expanded")
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Syne:wght@700;800&display=swap');
html,body,[class*="css"]{font-family:'Syne',sans-serif;background:#060b18;color:#dce8ff}
.stApp{background:#060b18}
h1,h2,h3{font-family:'Syne',sans-serif;font-weight:800}
.card{background:linear-gradient(135deg,#0f172a,#162035);border:1px solid #1e3058;
      border-radius:12px;padding:14px 18px;margin:5px 0;line-height:1.6}
.up{background:#082a1a;color:#00e676;border:1px solid #00e676;border-radius:5px;
    padding:1px 9px;font-family:'JetBrains Mono',monospace;font-size:12px;font-weight:700}
.dn{background:#2a0808;color:#ff5252;border:1px solid #ff5252;border-radius:5px;
    padding:1px 9px;font-family:'JetBrains Mono',monospace;font-size:12px;font-weight:700}
.nt{background:#1a1a30;color:#ffd740;border:1px solid #ffd740;border-radius:5px;
    padding:1px 9px;font-family:'JetBrains Mono',monospace;font-size:12px;font-weight:700}
.ob{background:#0d1f3c;border:1px solid #2563eb;border-radius:10px;padding:12px 16px;margin:4px 0}
.stButton>button{background:linear-gradient(135deg,#1d4ed8,#1e40af);color:white;
    border:none;border-radius:8px;font-weight:700;padding:10px 24px}
</style>""", unsafe_allow_html=True)

st.markdown("## 📊 AI Trading System — Nifty 500")
st.markdown("*Order Block + SMC + Multi-indicator · Targets +1–2% next-day moves · Real NSE data*")
st.divider()

with st.sidebar:
    st.markdown("### ⚙️ Settings")
    mode = st.radio("Scan Mode", ["📋 My Watchlist","🏆 Top N","🔢 Full Nifty 500"], index=0)
    if mode=="📋 My Watchlist":
        wl = st.text_area("Tickers (one per line)", "\n".join(DEFAULT_WATCHLIST), height=180)
        sel = [t.strip().upper() for t in wl.splitlines() if t.strip()]
        sel = [s if s.endswith(".NS") else s+".NS" for s in sel]
    elif mode=="🏆 Top N":
        n = st.slider("Number", 10, 500, 50, step=10)
        sel = NSE_500[:n]
        st.info(f"⏱ ~{round(n*0.05,1)} min")
    else:
        sel = NSE_500
        st.warning("⏱ ~25–40 min ☕")

    min_sc = st.slider("Min Score (5=UP)", -24, 24, 5)
    show_neutral = st.checkbox("Show NEUTRAL signals too", value=False)
    st.divider()
    st.markdown(f"**Queued:** {len(sel)} stocks")
    st.divider()
    st.markdown("### 🔬 Deep Dive")
    single = st.text_input("Ticker", "RELIANCE.NS")
    dive   = st.button("🔬 Analyse")

tab1,tab2,tab3,tab4,tab5 = st.tabs([
    "🔮 Next-Day Picks","🧱 Order Blocks","📈 Backtest","⚡ Intraday","🔬 Deep Dive"
])

# ===== TAB 1: PREDICTION =====
with tab1:
    st.markdown("### 🔮 Next-Day Prediction — Stocks likely to move +1% to +2%")
    st.info("Combines Order Block + BOS + FVG + 10 indicators + 4-source news sentiment. **Score ≥ 5 = UP signal.**")

    if st.button("▶️ Run Prediction Scan", key="scan"):
        results=[]; total=len(sel); t0=datetime.now()
        prog=st.progress(0); stat=st.empty(); eta=st.empty()

        for i,stock in enumerate(sel):
            el=(datetime.now()-t0).seconds; rt=(i+1)/max(el,1)
            rem=int((total-i-1)/rt) if rt>0 else 0; m,s=divmod(rem,60)
            prog.progress((i+1)/total)
            stat.markdown(f"🔍 **{stock}** — {i+1}/{total}")
            eta.markdown(f"⏱ ETA **{m}m {s}s**")

            df=load_data(stock)
            if df is None: continue

            ns,ns_lbl,_,_,_ = get_sentiment(stock)
            direction,conf,sc,_ = predict(df, ns)
            entry,sl,tgt,rr,mp = trade_plan(df, direction)

            if sc < min_sc: continue
            if not show_neutral and direction=="NEUTRAL ➡️": continue

            results.append({
                "Stock":      stock.replace(".NS",""),
                "Signal":     direction,
                "Score":      sc,
                "Confidence": conf,
                "Entry ₹":    entry,
                "Stop ₹":     sl,
                "Target ₹":   tgt,
                "Move %":     mp,
                "R:R":        rr,
                "Sentiment":  ns_lbl,
            })

        prog.empty(); stat.empty(); eta.empty()

        if results:
            dfr = pd.DataFrame(results).sort_values("Score", ascending=False)
            c1,c2,c3,c4 = st.columns(4)
            c1.metric("🟢 UP",   sum(1 for r in results if "UP"   in r["Signal"]))
            c2.metric("🔴 DOWN", sum(1 for r in results if "DOWN" in r["Signal"]))
            c3.metric("📋 Total",len(results))
            c4.metric("🎯 Top Score", dfr["Score"].max())
            st.dataframe(dfr, use_container_width=True, hide_index=True,
                column_config={
                    "Confidence": st.column_config.ProgressColumn("Conf %", min_value=0, max_value=100),
                    "Score":      st.column_config.NumberColumn("Score",  format="%.1f"),
                    "Move %":     st.column_config.NumberColumn("Move %", format="%.2f%%"),
                })
            st.markdown("#### 🏆 Top 5 UP Picks")
            top5 = dfr[dfr["Signal"].str.contains("UP")].head(5)
            if not top5.empty:
                st.dataframe(top5, use_container_width=True, hide_index=True)
        else:
            st.warning("No stocks passed filter. Lower Min Score or add more stocks.")

# ===== TAB 2: ORDER BLOCKS =====
with tab2:
    st.markdown("### 🧱 Order Block Scanner — Institutional Zones")
    st.info("Detects Bullish/Bearish Order Blocks, Break of Structure (BOS) and Fair Value Gaps (FVG) using SMC methodology.")

    if st.button("▶️ Scan Order Blocks", key="ob"):
        ob_results=[]; total=len(sel)
        prog=st.progress(0); stat=st.empty()

        for i,stock in enumerate(sel):
            prog.progress((i+1)/total)
            stat.markdown(f"🧱 Scanning OBs: **{stock}** — {i+1}/{total}")
            df=load_data(stock)
            if df is None: continue

            obs_bull, obs_bear = detect_order_blocks(df)
            bos_lbl,bos_sc,bos_desc = detect_bos(df)
            fvgs = detect_fvg(df)
            cl = flt(df["Close"])
            atr= flt(df["ATR"])
            ob_sig,ob_desc,ob_sc = ob_signal(obs_bull, obs_bear, cl, atr)

            # Only show if there's an active OB signal
            active_bull = [ob for ob in obs_bull if ob["tested"]=="✅ Retesting"]
            active_bear = [ob for ob in obs_bear if ob["tested"]=="✅ Retesting"]

            if active_bull or active_bear or bos_sc != 0:
                ob_results.append({
                    "Stock":     stock.replace(".NS",""),
                    "Price ₹":   round(cl,2),
                    "BOS":       bos_lbl,
                    "OB Signal": ob_desc[:60],
                    "OB Score":  ob_sc,
                    "Bull OBs":  len(obs_bull),
                    "Bear OBs":  len(obs_bear),
                    "FVGs":      len(fvgs),
                })

        prog.empty(); stat.empty()

        if ob_results:
            df_ob = pd.DataFrame(ob_results).sort_values("OB Score", ascending=False)
            st.dataframe(df_ob, use_container_width=True, hide_index=True)
        else:
            st.info("No active Order Block retest setups found.")

# ===== TAB 3: BACKTEST =====
with tab3:
    st.markdown("### 📈 Walk-Forward Backtest")
    st.info("No lookahead bias — predicts each day using ONLY past data. Checks actual next-day outcome.")

    if st.button("▶️ Run Backtest", key="bt"):
        bt_res=[]; total=len(sel)
        prog=st.progress(0); stat=st.empty()
        for i,stock in enumerate(sel):
            prog.progress((i+1)/total)
            stat.markdown(f"📊 Backtesting **{stock}** — {i+1}/{total}")
            df=load_data(stock)
            if df is None: continue
            tot,wr,exp,acc1m,mtbl = backtest(df)
            if tot>0:
                bt_res.append({
                    "Stock":         stock.replace(".NS",""),
                    "1M Accuracy %": acc1m,
                    "Yr Win Rate %": wr,
                    "Trades":        tot,
                    "Expectancy R":  exp,
                    "Grade": "⭐ Excellent" if acc1m>=65 else("✅ Good" if acc1m>=55 else "⚠️ Weak"),
                })
        prog.empty(); stat.empty()
        if bt_res:
            df_bt=pd.DataFrame(bt_res).sort_values("1M Accuracy %", ascending=False)
            c1,c2,c3=st.columns(3)
            c1.metric("Avg 1M Accuracy",   f"{round(df_bt['1M Accuracy %'].mean(),1)}%")
            c2.metric("Avg Year Win Rate",  f"{round(df_bt['Yr Win Rate %'].mean(),1)}%")
            c3.metric("Best Stock",          df_bt.iloc[0]["Stock"])
            st.dataframe(df_bt, use_container_width=True, hide_index=True)

# ===== TAB 4: INTRADAY =====
with tab4:
    st.markdown("### ⚡ Intraday Breakout Signals")
    st.warning("⏰ Run during NSE hours: 9:15 AM – 3:30 PM IST for live signals")
    if st.button("▶️ Scan Intraday", key="intra"):
        intra=[]; prog=st.progress(0)
        for i,stock in enumerate(sel):
            prog.progress((i+1)/len(sel))
            df=load_intra(stock)
            if df is None: continue
            sig=intra_signal(df)
            if sig and "WAIT" not in sig[0]:
                intra.append({"Stock":stock.replace(".NS",""),"Signal":sig[0],
                               "Entry ₹":sig[1],"SL ₹":sig[2],"Target ₹":sig[3]})
        prog.empty()
        if intra: st.dataframe(pd.DataFrame(intra), use_container_width=True, hide_index=True)
        else: st.info("No breakout signals now. Run during market hours.")

# ===== TAB 5: DEEP DIVE =====
with tab5:
    st.markdown("### 🔬 Single Stock Deep Dive")

    if dive and single:
        ticker = single.upper().strip()
        if not ticker.endswith(".NS"): ticker+=".NS"

        with st.spinner(f"Loading {ticker}..."):
            df = load_data(ticker)

        if df is None:
            st.error(f"Cannot fetch {ticker}. Check symbol.")
        else:
            with st.spinner("Analysing Order Blocks, BOS, FVG, indicators & sentiment..."):
                ns,ns_lbl,_,sent_bd,ann = get_sentiment(ticker)
                direction,conf,sc,det   = predict(df, ns)
                entry,sl,tgt,rr,mp      = trade_plan(df, direction)
                tot,wr,exp,acc1m,mtbl   = backtest(df)
                obs_bull,obs_bear       = detect_order_blocks(df)
                bos_lbl,bos_sc,bos_desc = detect_bos(df)
                fvgs                    = detect_fvg(df)
                cl                      = flt(df["Close"])
                atr_v                   = flt(df["ATR"])

            # ── Header metrics ──
            c1,c2,c3,c4 = st.columns(4)
            c1.metric("📌 Stock",      ticker.replace(".NS",""))
            c2.metric("🔮 Signal",     direction)
            c3.metric("💯 Confidence", f"{conf}%")
            c4.metric("📊 Score",      f"{sc} / 24")
            st.divider()

            # ── Trade plan ──
            c1,c2,c3,c4,c5 = st.columns(5)
            c1.metric("CMP ₹",        cl)
            c2.metric("Entry ₹",      entry)
            c3.metric("Stop Loss ₹",  sl,  delta=f"{round((sl-entry)/entry*100,1)}%")
            c4.metric("Target ₹",     tgt, delta=f"+{mp}%")
            c5.metric("Risk:Reward",  f"1:{rr}")
            st.divider()

            # ── Order Blocks ──
            st.markdown("#### 🧱 Detected Order Blocks")
            c1,c2 = st.columns(2)
            with c1:
                st.markdown("**Bullish Order Blocks (Demand Zones)**")
                if obs_bull:
                    for ob in obs_bull:
                        tested_color = "🟢" if ob["tested"]=="✅ Retesting" else "⚪"
                        st.markdown(f"""<div class="ob">
                            {tested_color} <b>{ob['type']}</b><br>
                            Zone: <b>{ob['ob_low']} – {ob['ob_high']}</b> ₹<br>
                            Strength: <b>{ob['strength']}</b> | Move: +{ob['move_pct']}% | Vol: {ob['vol_ratio']}x<br>
                            Date: {ob['date']} | Status: {ob['tested']}
                        </div>""", unsafe_allow_html=True)
                else:
                    st.info("No bullish OBs detected in recent data.")
            with c2:
                st.markdown("**Bearish Order Blocks (Supply Zones)**")
                if obs_bear:
                    for ob in obs_bear:
                        tested_color = "🔴" if ob["tested"]=="✅ Retesting" else "⚪"
                        st.markdown(f"""<div class="ob">
                            {tested_color} <b>{ob['type']}</b><br>
                            Zone: <b>{ob['ob_low']} – {ob['ob_high']}</b> ₹<br>
                            Strength: <b>{ob['strength']}</b> | Move: -{ob['move_pct']}% | Vol: {ob['vol_ratio']}x<br>
                            Date: {ob['date']} | Status: {ob['tested']}
                        </div>""", unsafe_allow_html=True)
                else:
                    st.info("No bearish OBs detected in recent data.")

            # ── BOS + FVG ──
            st.divider()
            c1,c2 = st.columns(2)
            with c1:
                st.markdown("#### 🔼 Break of Structure")
                badge = "up" if bos_sc>0 else ("dn" if bos_sc<0 else "nt")
                st.markdown(f'<div class="card"><span class="{badge}">{bos_lbl}</span><br>{bos_desc}</div>',
                            unsafe_allow_html=True)
            with c2:
                st.markdown("#### ⬜ Fair Value Gaps")
                if fvgs:
                    for fvg in fvgs[:3]:
                        filled = "✅ Filled" if fvg["filled"] else "🔲 Unfilled"
                        st.markdown(f'<div class="card"><b>{fvg["type"]}</b> | Zone: {fvg["lower"]}–{fvg["upper"]} ₹ | {filled}</div>',
                                    unsafe_allow_html=True)
                else:
                    st.info("No active FVGs near current price.")

            st.divider()

            # ── Signal breakdown ──
            st.markdown("#### 🧠 Full Signal Breakdown")
            for factor,(sig,reason) in det.items():
                badge = "up" if sig=="UP" else ("dn" if sig=="DOWN" else "nt")
                st.markdown(
                    f'<div class="card"><b>{factor}</b>: <span class="{badge}">{sig}</span> &nbsp; {reason}</div>',
                    unsafe_allow_html=True)

            st.divider()

            # ── Sentiment ──
            st.markdown("#### 📰 News Sentiment Breakdown")
            st.dataframe(pd.DataFrame([
                {"Source":k,"Signal":v["signal"],"Polarity":v["polarity"],"Weight":v["weight"]}
                for k,v in sent_bd.items()
            ]), use_container_width=True, hide_index=True)
            if ann:
                st.markdown("**📢 NSE Corporate Announcements:**")
                for a in ann: st.markdown(f"- {a}")

            st.divider()

            # ── Backtest ──
            st.markdown("#### 📈 Backtest Performance")
            c1,c2,c3,c4 = st.columns(4)
            c1.metric("1-Month Accuracy", f"{acc1m}%")
            c2.metric("1-Year Win Rate",  f"{wr}%")
            c3.metric("Total Trades",     tot)
            c4.metric("Expectancy",       f"{exp}R")
            if mtbl:
                st.dataframe(pd.DataFrame(mtbl), use_container_width=True, hide_index=True)

            st.divider()
            st.markdown("#### 📊 Price + MA Chart (Last 6 months)")
            chart = df[["Close","MA20","MA50","MA200"]].tail(130).dropna()
            st.line_chart(chart)

st.divider()
st.markdown("<small>⚠️ For educational use only. Not SEBI investment advice. Past performance ≠ future results.</small>",
            unsafe_allow_html=True)
