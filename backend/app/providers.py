from .models import Quote, NewsArticle
from .settings import settings
import httpx

FREE_API="https://indian-stock-market-api.onrender.com"

class FreeMarketProvider:
    def quotes(self)->list[Quote]:
        try:
            data=httpx.get(f"{FREE_API}/stock/list?symbols=RELIANCE.NS,TCS.NS,HDFCBANK.NS,INFY.NS,ICICIBANK.NS,ITC.NS,SBIN.NS,ADANIENT.NS,TATAMOTORS.NS,WIPRO.NS",timeout=8).json()
            rows=data if isinstance(data,list) else data.get("data",[])
            out=[]
            for x in rows:
                symbol=str(x.get("symbol") or x.get("ticker") or "").replace(".NS","").replace(".BO","")
                price=x.get("price") or x.get("ltp") or x.get("last_price")
                change=x.get("change_percent") or x.get("change_pct") or x.get("percent_change") or 0
                if symbol and price is not None:
                    out.append(Quote(symbol=symbol,name=x.get("name",symbol),exchange="NSE",price=float(price),change_pct=float(change)))
            return out
        except Exception:
            return []

    def news(self,symbol:str)->list[NewsArticle]:
        return []

class DemoMarketProvider:
    def quotes(self)->list[Quote]:
        data=[("RELIANCE","Reliance Industries","NSE",2920.10,2.41),("TCS","Tata Consultancy Services","NSE",3988.20,1.82),("HDFCBANK","HDFC Bank","NSE",1784.30,1.37),("INFY","Infosys","NSE",1620.50,0.94),("ICICIBANK","ICICI Bank","NSE",1422.60,0.71),("ITC","ITC","NSE",511.30,0.35),("SBIN","State Bank of India","NSE",842.20,-0.44),("ADANIENT","Adani Enterprises","NSE",2460.80,-1.18),("TATAMOTORS","Tata Motors","NSE",1011.40,-2.05),("WIPRO","Wipro","NSE",526.90,-2.76)]
        return [Quote(symbol=s,name=n,exchange=e,price=p,change_pct=c) for s,n,e,p,c in data]
    def news(self,symbol:str)->list[NewsArticle]:
        return []

class MarketProviderRegistry:
    def __init__(self):
        self.market=FreeMarketProvider() if settings.market_data_provider=="free" else DemoMarketProvider()
        self.news=self.market