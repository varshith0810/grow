"use client";
import { use, useEffect, useMemo, useState } from "react";
import Link from "next/link";

const API = "";

type Quote={symbol:string;name:string;price:number;change_pct:number;exchange:string;volume?:number;updated_at?:number};
type Candle={time:string;open:number;high:number;low:number;close:number;volume:number};
type News={title:string;source:string;url:string;published_at:string};
type AI={signal:"GREEN"|"RED"|"NEUTRAL";confidence:number;summary:string;rationale:string[];risks:string[];technical_score:number;news_sentiment:string;horizon:string;context?:any;provider?:string};

const ranges:Record<string,[string,string]>={
  live:["1d","1m"],"1m":["1d","1m"],"15m":["1mo","15m"],"1h":["3mo","1h"],
  "1d":["1y","1d"],"1w":["5y","1wk"],"1yr":["max","1mo"]
};

export default function StockPage({params}:{params:Promise<{symbol:string}>}){
 const {symbol}=use(params); const ticker=symbol.toUpperCase();
 const [quote,setQuote]=useState<Quote|null>(null);
 const [candles,setCandles]=useState<Candle[]>([]);
 const [news,setNews]=useState<News[]>([]);
 const [ai,setAi]=useState<AI|null>(null);
 const [tf,setTf]=useState("live");
 const [chartType,setChartType]=useState<"line"|"candle">("line");
 const [aiLoading,setAiLoading]=useState(false);
 const [marketOpen,setMarketOpen]=useState(false);
 const [liveConnected,setLiveConnected]=useState(false);

 async function loadChart(t:string){
   const [period,interval]=ranges[t];
   const r=await fetch(`${API}/api/stocks/${ticker}/history?period=${period}&interval=${interval}`,{cache:"no-store"});
   if(r.ok){const d=await r.json();setCandles(d.candles||[]);}
 }

 async function runAI(){
   setAiLoading(true);
   try{
     const r=await fetch(`${API}/api/predictions/${ticker}?timeframe=${tf}`,{cache:"no-store"});
     if(r.ok)setAi(await r.json());
   } finally {setAiLoading(false);}
 }

 useEffect(()=>{
   let cancelled=false;
   fetch(`${API}/api/stocks/${ticker}`,{cache:"no-store"}).then(r=>r.json()).then(d=>{if(!cancelled)setQuote(d.quote)});
   fetch(`${API}/api/news/${ticker}`,{cache:"no-store"}).then(r=>r.json()).then(d=>{if(!cancelled)setNews(d)});
   loadChart("live");

   const source=new EventSource(`${API}/api/market/stream?symbols=${encodeURIComponent(ticker)}`);
   const onQuotes=(event:MessageEvent)=>{
     try{
       const incoming=JSON.parse(event.data) as Quote[];
       if(incoming[0]&&!cancelled)setQuote(q=>q?{...q,...incoming[0]}:incoming[0]);
     }catch{}
   };
   source.addEventListener("quotes",onQuotes);

   const refreshStatus=async()=>{
     try{
       const r=await fetch(`${API}/api/market/live/status`,{cache:"no-store"});
       if(r.ok){const d=await r.json();if(!cancelled){setMarketOpen(Boolean(d.market_open));setLiveConnected(Boolean(d.connected));}}
     }catch{}
   };
   refreshStatus();
   const statusTimer=setInterval(refreshStatus,15000);

   return()=>{cancelled=true;source.removeEventListener("quotes",onQuotes);source.close();clearInterval(statusTimer)};
 },[ticker]);

 useEffect(()=>{loadChart(tf)},[tf]);

 const stats=useMemo(()=>{
   if(!candles.length)return null;
   const last=candles[candles.length-1];
   return {high:Math.max(...candles.map(x=>x.high)),low:Math.min(...candles.map(x=>x.low)),volume:last.volume};
 },[candles]);

 if(!quote)return <main className="app-shell"><Link href="/" className="back">← Market</Link><p>Loading {ticker}…</p></main>;

 return <main className="app-shell">
   <Link href="/" className="back">← Market</Link>
   <header className="hero">
     <div><p className="eyebrow">{quote.exchange} · STOCK</p><h1>{quote.name}</h1><p className="muted">{quote.symbol} · <span className="live-badge">{marketOpen&&liveConnected?"● LIVE":"● CLOSED"}</span> · {marketOpen&&liveConnected?"Live market feed":"Last traded session price"}</p></div>
     <div><h1>₹{quote.price.toLocaleString("en-IN",{maximumFractionDigits:2})}</h1><strong className={quote.change_pct>=0?"up":"down"}>{quote.change_pct>=0?"+":""}{quote.change_pct.toFixed(2)}%</strong></div>
   </header>

   <section className="chart-shell">
     <div className="tabs">
       {["live","1m","15m","1h","1d","1w","1yr"].map(x=><button className={tf===x?"active":""} key={x} onClick={()=>setTf(x)}>{x}</button>)}
       <span style={{flex:1}}/>
       <button className={chartType==="line"?"active":""} onClick={()=>setChartType("line")}>Graph</button>
       <button className={chartType==="candle"?"active":""} onClick={()=>setChartType("candle")}>Candles</button>
     </div>
     <MarketChart candles={candles} type={chartType}/>
     {stats&&<div className="ai-meta"><span>High ₹{stats.high.toFixed(2)}</span><span>Low ₹{stats.low.toFixed(2)}</span><span>Volume {stats.volume.toLocaleString("en-IN")}</span><span>{candles.length} candles</span></div>}
   </section>

   <section className="ai-card">
     <div className="panel-title"><div><p className="eyebrow">CLAUDE · AMAZON BEDROCK</p><h2>Historical stock analysis</h2></div><button className="ai-run" onClick={runAI}>{aiLoading?"Analysing…":"Analyse with Claude"}</button></div>
     <p className="muted">Claude analyses previous price/volume history, technical indicators, historical returns, volatility, drawdown and recent news. It does not use the current tick alone to make a prediction.</p>
     {ai&&<><div className={`ai-signal ${ai.signal==="GREEN"?"up":ai.signal==="RED"?"down":""}`}>{ai.signal} <span style={{fontSize:15,fontWeight:600}}>· {(ai.confidence*100).toFixed(0)}% model confidence</span></div><p className="muted">{ai.summary}</p><div className="ai-meta"><span>Horizon {ai.horizon}</span><span>Technical {ai.technical_score}/100</span><span>News {ai.news_sentiment}</span><span>Provider {ai.provider||"Bedrock"}</span></div><div className="ai-columns"><div><h3>Historical evidence</h3><ul>{ai.rationale.map((x,i)=><li key={i}>{x}</li>)}</ul></div><div><h3>Risks & limitations</h3><ul>{ai.risks.map((x,i)=><li key={i}>{x}</li>)}</ul></div></div></>}
   </section>

   <section className="panel"><div className="panel-title"><h2>Stock overview</h2><span>Research</span></div><div className="feature-grid"><Mini title="Price action" text="Historical returns, trend, volatility and drawdown."/><Mini title="Fundamentals" text="Valuation, financial statements and company data."/><Mini title="F&O" text="Option chain, open interest and derivatives analytics."/><Mini title="Events" text="Dividends, splits, results and announcements."/><Mini title="Similar stocks" text="Compare peers and sector performance."/><Mini title="Ownership" text="Institutional and mutual-fund participation." /></div></section>

   <section className="panel"><div className="panel-title"><h2>Latest news</h2><span>Top 10</span></div>{news.slice(0,10).map((n,i)=><article className="news" key={i}><a href={n.url} target="_blank" rel="noreferrer">{n.title}</a><small>{n.source} · {n.published_at}</small></article>)}</section>
   <footer><span>grow+ stock research</span><span>AI analysis is informational and not personalized financial advice.</span></footer>
 </main>
}

function Mini({title,text}:{title:string;text:string}){return <article className="feature-card"><h3>{title}</h3><p>{text}</p></article>}

function MarketChart({candles,type}:{candles:Candle[];type:"line"|"candle"}){
 if(!candles.length)return <div className="chart-placeholder">No chart data returned by the market provider.</div>;
 const vals=candles.slice(-120);
 const min=Math.min(...vals.map(x=>x.low)),max=Math.max(...vals.map(x=>x.high)),range=max-min||1;
 if(type==="line"){
   const points=vals.map((x,i)=>`${(i/(vals.length-1||1))*100},${100-((x.close-min)/range)*90-5}`).join(" ");
   return <div className="svg-chart"><svg viewBox="0 0 100 100" preserveAspectRatio="none" aria-label="Stock price graph"><polyline points={points} fill="none" stroke="currentColor" strokeWidth="0.9" vectorEffect="non-scaling-stroke"/></svg></div>;
 }
 return <div className="svg-chart"><svg viewBox="0 0 120 100" preserveAspectRatio="none" aria-label="Candlestick chart">
   {vals.map((x,i)=>{
     const cx=(i+0.5)*(120/vals.length), scaleY=(p:number)=>100-((p-min)/range)*90-5;
     const open=scaleY(x.open),close=scaleY(x.close),high=scaleY(x.high),low=scaleY(x.low),body=Math.max(0.7,Math.abs(close-open)),top=Math.min(open,close);
     const up=x.close>=x.open;
     return <g key={i} className={up?"candle-up":"candle-down"}><line x1={cx} x2={cx} y1={high} y2={low} stroke="currentColor" strokeWidth="0.35"/><rect x={cx-0.28} y={top} width="0.56" height={body} fill="currentColor"/></g>;
   })}
 </svg></div>;
}
