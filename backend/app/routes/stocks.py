from fastapi import APIRouter, HTTPException, Query
import yfinance as yf
from ..providers import MarketProviderRegistry

router=APIRouter()
providers=MarketProviderRegistry()

@router.get("/{symbol}")
def stock(symbol:str, timeframe:str=Query("1d",pattern="^(live|1m|15m|1h|1d|1w|1yr)$")):
    symbol=symbol.upper()
    quote=next((q for q in providers.market.quotes() if q.symbol==symbol),None)
    if not quote:
        # Free fallback: Yahoo Finance public market data via yfinance.
        try:
            t=yf.Ticker(symbol+".NS")
            hist=t.history(period="1y",interval="1d",auto_adjust=False)
            if hist.empty: raise ValueError
            last=hist.iloc[-1]
            prev=hist.iloc[-2] if len(hist)>1 else last
            price=float(last["Close"])
            change=float((price/float(prev["Close"])-1)*100) if float(prev["Close"]) else 0
            from ..models import Quote
            quote=Quote(symbol=symbol,name=symbol,exchange="NSE",price=price,change_pct=change)
        except Exception:
            raise HTTPException(status_code=404,detail="Stock not found")
    return {"quote":quote,"chart":{"timeframe":timeframe,"source":"free public market data","candles":[]}}

@router.get("/{symbol}/history")
def history(symbol:str, period:str=Query("1y",pattern="^(1d|5d|1mo|3mo|6mo|1y|5y|max)$"), interval:str=Query("1d",pattern="^(1m|5m|15m|30m|1h|1d|1wk|1mo)$")):
    try:
        hist=yf.Ticker(symbol.upper()+".NS").history(period=period,interval=interval,auto_adjust=False)
        candles=[]
        for idx,row in hist.iterrows():
            candles.append({"time":idx.isoformat(),"open":float(row["Open"]),"high":float(row["High"]),"low":float(row["Low"]),"close":float(row["Close"]),"volume":int(row["Volume"])})
        return {"symbol":symbol.upper(),"period":period,"interval":interval,"candles":candles}
    except Exception:
        raise HTTPException(status_code=503,detail="Historical data temporarily unavailable")
