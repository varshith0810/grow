"use client";
import {use,useEffect,useState} from "react";
import Link from "next/link";
const API=process.env.NEXT_PUBLIC_API_URL||"http://localhost:8000";
type Quote={symbol:string;name:string;price:number;change_pct:number;exchange:string};
type Article={title:string;source:string;url:string;published_at:string};
export default function StockPage({params}:{params:Promise<{symbol:string}>}){
 const {symbol}=use(params); const ticker=symbol.toUpperCase();
 const [quote,setQuote]=useState<Quote|null>(null); const [news,setNews]=useState<Article[]>([]); const [timeframe,setTimeframe]=useState("15m");
 useEffect(()=>{fetch(`${API}/api/stocks/${ticker}`).then(r=>r.json()).then(d=>setQuote(d.quote));fetch(`${API}/api/news/${ticker}`).then(r=>r.json()).then(setNews)},[ticker]);
 if(!quote)return <main><Link href="/">← Market</Link><p>Loading...</p></main>;
 return <main><Link href="/">← Market</Link><header><div><h1>{quote.name}</h1><p>{quote.symbol} · {quote.exchange}</p></div><div><h1>₹{quote.price.toLocaleString("en-IN")}</h1><strong className={quote.change_pct>=0?"up":"down"}>{quote.change_pct>=0?"+":""}{quote.change_pct.toFixed(2)}%</strong></div></header>
 <section className="chart"><div className="tabs">{["live","1m","15m","1h","1d","1w","1yr"].map(t=><button className={timeframe===t?"active":""} onClick={()=>setTimeframe(t)} key={t}>{t}</button>)}</div><div className="chartbox">Candlestick / price chart · {timeframe}<div className="placeholder">Historical OHLCV renders here after the market-data provider is connected.</div></div></section>
 <section><h2>AI forecast</h2><button onClick={()=>fetch(`${API}/api/predictions/${ticker}?timeframe=${timeframe}`).then(r=>r.json()).then(x=>alert(JSON.stringify(x,null,2)))}>Run Claude forecast</button></section>
 <section><h2>Top news</h2>{news.slice(0,10).map((n,i)=><article className="news" key={i}><a href={n.url} target="_blank" rel="noreferrer">{n.title}</a><small>{n.source} · {n.published_at}</small></article>)}</section></main>
}