"use client";
import { use, useEffect, useMemo, useState } from "react";
import Link from "next/link";
const API="";
type Quote={symbol:string;name:string;price:number;change_pct:number;exchange:string;volume?:number};
type Candle={time:string;open:number;high:number;low:number;close:number;volume:number};
type News={title:string;source:string;url:string;published_at:string};
type AI={signal:"GREEN"|"RED"|"NEUTRAL";confidence:number;summary:string;rationale:string[];risks:string[];technical_score:number;news_sentiment:string;horizon:string;context?:any};

export default function StockPage({params}:{params:Promise<{symbol:string}>}){
 const {symbol}=use(params); const ticker=symbol.toUpperCase();
 const [quote,setQuote]=useState<Quote|null>(null),[candles,setCandles]=useState<Candle[]>([]),[news,setNews]=useState<News[]>([]),[ai,setAi]=useState<AI|null>(null),[tf,setTf]=useState("1d"),[aiLoading,setAiLoading]=useState(false);
 const ranges:Record<string,[string,string]>={live:["1d","1m"],"1m":["1d","1m"],"15m":["1mo","15m"],"1h":["3mo","1h"],"1d":["1y","1d"],"1w":["5y","1wk"],"1yr":["max","1mo"]};
 async function loadChart(t:string){const [period,interval]=ranges[t];const r=await fetch(`${API}/api/stocks/${ticker}/history?period=${period}&interval=${interval}`,{cache:"no-store"});if(r.ok){const d=await r.json();setCandles(d.candles||[])}}
 async function runAI(){setAiLoading(true);try{const r=await fetch(`${API}/api/predictions/${ticker}?timeframe=${tf}`,{cache:"no-store"});setAi(await r.json())}finally{setAiLoading(false)}}
 useEffect(()=>{fetch(`${API}/api/stocks/${ticker}`).then(r=>r.json()).then(d=>setQuote(d.quote));fetch(`${API}/api/news/${ticker}`).then(r=>r.json()).then(setNews);loadChart("1d")},[ticker]);
 const stats=useMemo(()=>{if(!candles.length)return null;const last=candles[candles.length-1],high=Math.max(...candles.map(x=>x.high)),low=Math.min(...candles.map(x=>x.low));return {high,low,volume:last.volume}},[candles]);
 if(!quote)return <main className="app-shell"><Link href="/">← Market</Link><p>Loading {ticker}…</p></main>;
 return <main className="app-shell">
   <Link href="/" className="back">← Market</Link>
   <header className="hero"><div><p className="eyebrow">{quote.exchange} · STOCK</p><h1>{quote.name}</h1><p className="muted">{quote.symbol} · AI-assisted market research</p></div><div><h1>{`₹${quote.price.toLocaleString("en-IN",{maximumFractionDigits:2})}`}</h1><strong className={quote.change_pct>=0?"up":"down"}>{quote.change_pct>=0?"+":""}{quote.change_pct.toFixed(2)}%</strong></div></header>
   <section className="chart-shell"><div className="tabs">{["live","1m","15m","1h","1d","1w","1yr"].map(x=><button className={tf===x?"active":""} key={x} onClick={()=>{setTf(x);loadChart(x)}}>{x}</button>)}</div><SimpleChart candles={candles}/>{stats&&<div className="ai-meta"><span>High {`₹${stats.high.toFixed(2)}`}</span><span>Low {`₹${stats.low.toFixed(2)}`}</span><span>Volume {stats.volume.toLocaleString("en-IN")}</span><span>{candles.length} candles</span></div>}</section>
   <section className="ai-card"><div className="panel-title"><div><p className="eyebrow">CLAUDE AI</p><h2>Stock outlook</h2></div><button className="ai-run" onClick={runAI}>{aiLoading?"Analysing…":"Analyse with Claude"}</button></div>{ai?<><div className={`ai-signal ${ai.signal==="GREEN"?"up":ai.signal==="RED"?"down":""}`}>{ai.signal} <span style={{fontSize:15,fontWeight:600}}>· {(ai.confidence*100).toFixed(0)}% confidence</span></div><p className="muted">{ai.summary}</p><div className="ai-meta"><span>Horizon {ai.horizon}</span><span>Technical {ai.technical_score}/100</span><span>News {ai.news_sentiment}</span></div><div className="ai-columns"><div><h3>Why Claude says this</h3><ul>{ai.rationale.map((x,i)=><li key={i}>{x}</li>)}</ul></div><div><h3>Risks</h3><ul>{ai.risks.map((x,i)=><li key={i}>{x}</li>)}</ul></div></div></>:<p className="muted">Claude evaluates recent price behaviour, technical indicators and current news when you run an analysis. It does not guarantee future returns.</p>}</section>
   <section className="panel"><div className="panel-title"><h2>Stock overview</h2><span>Research</span></div><div className="feature-grid"><Mini title="Price action" text="Track recent returns, trend and volatility."/><Mini title="Fundamentals" text="Add valuation, financials, shareholding and corporate actions data."/><Mini title="F&O" text="Option chain, open interest, futures and contract analytics."/><Mini title="Events" text="Dividends, bonuses, splits, buybacks and announcements."/><Mini title="Similar stocks" text="Compare peers and sector performance."/><Mini title="Ownership" text="Track institutional and mutual-fund participation." /></div></section>
   <section className="panel"><div className="panel-title"><h2>Latest news</h2><span>Top 10</span></div>{news.slice(0,10).map((n,i)=><article className="news" key={i}><a href={n.url} target="_blank" rel="noreferrer">{n.title}</a><small>{n.source} · {n.published_at}</small></article>)}</section>
   <footer><span>grow+ stock research</span><span>AI analysis is informational and not personalized financial advice.</span></footer>
 </main>
}
function Mini({title,text}:{title:string;text:string}){return <article className="feature-card"><h3>{title}</h3><p>{text}</p></article>}
function SimpleChart({candles}:{candles:Candle[]}){if(!candles.length)return <div className="chart-placeholder">No chart data returned by the market provider.</div>;const vals=candles.slice(-100);const min=Math.min(...vals.map(x=>x.low)),max=Math.max(...vals.map(x=>x.high));const range=max-min||1;const points=vals.map((x,i)=>`${(i/(vals.length-1||1))*100},${100-((x.close-min)/range)*90-5}`).join(" ");return <div className="svg-chart"><svg viewBox="0 0 100 100" preserveAspectRatio="none" aria-label="Stock price chart"><polyline points={points} fill="none" stroke="currentColor" strokeWidth="0.9" vectorEffect="non-scaling-stroke"/></svg></div>}
