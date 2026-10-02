from .models import Quote, NewsArticle
from .settings import settings
import yfinance as yf

SYMBOLS=["RELIANCE","TCS","HDFCBANK","INFY","ICICIBANK","ITC","SBIN","ADANIENT","TATAMOTORS","WIPRO","BHARTIARTL","LT","KOTAKBANK","AXISBANK","MARUTI","SUNPHARMA","HCLTECH","TITAN","NTPC","POWERGRID","ONGC","COALINDIA","BEL","TECHM","M&M","BAJFINANCE","BAJAJFINSV","INDUSINDBK","HINDUNILVR","ASIANPAINT","ULTRACEMCO","NESTLEIND","TATASTEEL","JSWSTEEL","ADANIPORTS","HINDALCO","CIPLA","DRREDDY","EICHERMOT","GRASIM","DIVISLAB","APOLLOHOSP","BRITANNIA","HEROMOTOCO","TATACONSUM","SBILIFE","HDFCLIFE","TRENT","SHRIRAMFIN"]

class FreeMarketProvider:
    def quotes(self)->list[Quote]:
        out=[]
        try:
            data=yf.download([s+".NS" for s in SYMBOLS],period="5d",interval="1d",group_by="ticker",auto_adjust=False,progress=False,threads=True)
            for s in SYMBOLS:
                try:
                    frame=data[s+".NS"].dropna()
                    if frame.empty: continue
                    last=frame.iloc[-1]
                    close=float(last["Close"])
                    previous=float(frame.iloc[-2]["Close"]) if len(frame)>1 else close
                    change=(close/previous-1)*100 if previous else 0
                    out.append(Quote(symbol=s,name=s,exchange="NSE",price=close,change_pct=change,volume=int(last["Volume"])))
                except Exception:
                    continue
        except Exception:
            pass
        return out

    def news(self,symbol:str)->list[NewsArticle]:
        return []

class DemoMarketProvider:
    def quotes(self)->list[Quote]:
        return [Quote(symbol=s,name=s,exchange="NSE",price=0,change_pct=0) for s in SYMBOLS]
    def news(self,symbol:str)->list[NewsArticle]:
        return []

class MarketProviderRegistry:
    def __init__(self):
        self.market=FreeMarketProvider() if settings.market_data_provider=="free" else DemoMarketProvider()
        self.news=self.market
