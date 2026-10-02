from fastapi import APIRouter
import feedparser
from urllib.parse import quote
from ..models import NewsArticle

router=APIRouter()

@router.get("/{symbol}")
def news(symbol:str):
    query=quote(f"{symbol} India stock")
    feed=feedparser.parse(f"https://news.google.com/rss/search?q={query}&hl=en-IN&gl=IN&ceid=IN:en")
    out=[]
    for entry in feed.entries[:10]:
        out.append(NewsArticle(title=entry.get("title",""),source=entry.get("source",{}).get("title","Google News"),url=entry.get("link","#"),published_at=entry.get("published","")))
    return out
