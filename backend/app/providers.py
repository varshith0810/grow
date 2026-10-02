from datetime import datetime, timezone
from .models import Quote, NewsArticle
from .settings import settings

class DemoMarketProvider:
    def quotes(self) -> list[Quote]:
        data=[("RELIANCE","Reliance Industries","NSE",2920.10,2.41),("TCS","Tata Consultancy Services","NSE",3988.20,1.82),("HDFCBANK","HDFC Bank","NSE",1784.30,1.37),("INFY","Infosys","NSE",1620.50,0.94),("ICICIBANK","ICICI Bank","NSE",1422.60,0.71),("ITC","ITC","NSE",511.30,0.35),("SBIN","State Bank of India","NSE",842.20,-0.44),("ADANIENT","Adani Enterprises","NSE",2460.80,-1.18),("TATAMOTORS","Tata Motors","NSE",1011.40,-2.05),("WIPRO","Wipro","NSE",526.90,-2.76)]
        return [Quote(symbol=s,name=n,exchange=e,price=p,change_pct=c) for s,n,e,p,c in data]
    def news(self,symbol:str)->list[NewsArticle]:
        now=datetime.now(timezone.utc).isoformat()
        return [NewsArticle(title=f"{symbol}: latest market update",source="Demo Feed",url="#",published_at=now)]

class TrueDataMarketProvider:
    def __init__(self):
        self.configured=bool(settings.truedata_username and settings.truedata_password)
    def quotes(self)->list[Quote]:
        # Integration point for the licensed TrueData WebSocket/REST feed.
        # Keep credentials server-side; never expose them to the browser.
        if not self.configured:
            return []
        raise NotImplementedError("Enable the TrueData adapter with your subscribed API contract.")

    def news(self,symbol:str)->list[NewsArticle]:
        if not self.configured:
            return []
        raise NotImplementedError("Enable the TrueData news adapter with your subscribed API contract.")

class MarketProviderRegistry:
    def __init__(self):
        self.market=TrueDataMarketProvider() if settings.market_data_provider=="truedata" else DemoMarketProvider()
        self.news=self.market