"use client";
import { useEffect, useMemo, useState } from "react";
import Link from "next/link";

const API = "";

type Quote = { symbol:string; name:string; price:number; change_pct:number; exchange:string; volume?:number };
type Product = { id:string; title:string; subtitle:string; icon:string; description:string };

const products: Product[] = [
  {id:"stocks",title:"Stocks",subtitle:"Invest & trade",icon:"↗",description:"NSE/BSE stocks, intraday, ETFs and MTF"},
  {id:"mutual-funds",title:"Mutual Funds",subtitle:"SIP & lumpsum",icon:"◉",description:"Explore, compare and track funds"},
  {id:"fno",title:"F&O",subtitle:"Derivatives",icon:"⌁",description:"Futures, options, chains and baskets"},
  {id:"ipo",title:"IPO",subtitle:"New listings",icon:"◆",description:"Upcoming, open and past IPOs"},
  {id:"etf",title:"ETFs",subtitle:"Diversify",icon:"▦",description:"Index, sector, gold and international ETFs"},
  {id:"gold",title:"Gold",subtitle:"Gold investing",icon:"◇",description:"Gold ETFs, funds and commodities"},
  {id:"bonds",title:"Bonds",subtitle:"Fixed income",icon:"▤",description:"Explore fixed-income opportunities"},
  {id:"portfolio",title:"Portfolio",subtitle:"Your money",icon:"◫",description:"Holdings, P&L, allocation and activity"},
];

export default function Home(){
 const [quotes,setQuotes]=useState<Quote[]>([]);
 const [query,setQuery]=useState("");
 const [tab,setTab]=useState("stocks");
 const [watch,setWatch]=useState<string[]>([]);
 const [loading,setLoading]=useState(true);
 const [error,setError]=useState("");

 useEffect(()=>{ try{setWatch(JSON.parse(localStorage.getItem("grow-watchlist")||"[]"));}catch{} },[]);
 useEffect(()=>{
   let cancelled=false;
   async function load(){
     try{ const r=await fetch(`${API}/api/market/quotes`,{cache:"no-store"}); if(!r.ok) throw new Error(`Market API returned HTTP ${r.status}`); const d=await r.json(); if(!Array.isArray(d)) throw new Error("Invalid market response"); if(!cancelled){setQuotes(d);setError("");} }
     catch(e){if(!cancelled)setError(e instanceof Error?e.message:"Market data unavailable");}
     finally{if(!cancelled)setLoading(false);}
   }
   load();
   return()=>{cancelled=true};
 },[]);

 useEffect(()=>{
   if(!quotes.length) return;
   const symbols=quotes.slice(0,100).map(q=>q.symbol).join(",");
   const source=new EventSource(`${API}/api/market/stream?symbols=${encodeURIComponent(symbols)}`);
   const onQuotes=(event:MessageEvent)=>{try{
     const incoming=JSON.parse(event.data) as Quote[];
     if(!incoming.length) return;
     setQuotes(current=>{const next=new Map(current.map(q=>[q.symbol,q]));incoming.forEach(q=>next.set(q.symbol,q));return Array.from(next.values())});
   }catch{}};
   source.addEventListener("quotes",onQuotes);
   source.onerror=()=>{};
   return()=>{source.removeEventListener("quotes",onQuotes);source.close()};
 },[quotes.length]);

 const toggleWatch=(symbol:string)=>{const next=watch.includes(symbol)?watch.filter(x=>x!==symbol):[...watch,symbol];setWatch(next);localStorage.setItem("grow-watchlist",JSON.stringify(next));};
 const filtered=useMemo(()=>quotes.filter(q=>`${q.symbol} ${q.name}`.toLowerCase().includes(query.toLowerCase())),[quotes,query]);
 const top=[...filtered].sort((a,b)=>b.change_pct-a.change_pct).slice(0,10);
 const worst=[...filtered].sort((a,b)=>a.change_pct-b.change_pct).slice(0,10);
 const watchQuotes=quotes.filter(q=>watch.includes(q.symbol));
 const money=(n:number)=>`₹${n.toLocaleString("en-IN",{maximumFractionDigits:2})}`;

 return <main className="app-shell">
   <nav className="topbar"><Link href="/" className="brand">grow<span>+</span></Link><div className="navlinks">{products.slice(0,6).map(p=><button key={p.id} className={tab===p.id?"nav-active":""} onClick={()=>setTab(p.id)}>{p.title}</button>)}</div><button className="profile">Account</button></nav>
   <section className="hero"><div><p className="eyebrow">INDIAN MARKETS</p><h1>Investing, trading & analysis in one place.</h1><p className="muted">A Groww-inspired research terminal with Claude AI analysis built into every stock page.</p></div><div className="market-pulse"><span>● Market data</span><b>{loading?"Loading":error?"Unavailable":"Live"}</b></div></section>
   <div className="searchbar"><span>⌕</span><input value={query} onChange={e=>setQuery(e.target.value)} placeholder="Search stocks, ETFs, mutual funds, IPOs..." /><kbd>⌘ K</kbd></div>

   <section className="product-strip">{products.map(p=><button key={p.id} className={`product-card ${tab===p.id?"selected":""}`} onClick={()=>setTab(p.id)}><span className="product-icon">{p.icon}</span><b>{p.title}</b><small>{p.subtitle}</small></button>)}</section>

   {tab==="stocks" && <>
     <section className="section-head"><div><p className="eyebrow">MARKET SNAPSHOT</p><h2>Stocks</h2></div><div className="pills"><span>NSE</span><span>BSE</span><span>Intraday</span></div></section>
     {error&&<div className="alert">{error}<button onClick={()=>location.reload()}>Retry</button></div>}
     <div className="market-grid">
       <section className="panel"><div className="panel-title"><h3>Top performers</h3><span>Today</span></div>{top.map(q=><StockRow key={q.symbol} q={q} watched={watch.includes(q.symbol)} onWatch={()=>toggleWatch(q.symbol)} />)}</section>
       <section className="panel"><div className="panel-title"><h3>Worst performers</h3><span>Today</span></div>{worst.map(q=><StockRow key={q.symbol} q={q} watched={watch.includes(q.symbol)} onWatch={()=>toggleWatch(q.symbol)} />)}</section>
     </div>
     <section className="panel full"><div className="panel-title"><h3>All market stocks</h3><span>{filtered.length} instruments</span></div>{filtered.map(q=><StockRow key={q.symbol} q={q} watched={watch.includes(q.symbol)} onWatch={()=>toggleWatch(q.symbol)} />)}</section>
   </>}

   {tab==="portfolio" && <section className="feature-page"><p className="eyebrow">YOUR MONEY</p><h2>Portfolio</h2><div className="portfolio-total">{money(0)} <span>Paper portfolio</span></div><div className="empty-state"><b>No holdings yet</b><p>Add stocks to your watchlist, then connect a broker when you are ready for live orders.</p><button>Explore stocks</button></div>{watchQuotes.length>0&&<div className="panel"><h3>Watchlist</h3>{watchQuotes.map(q=><StockRow key={q.symbol} q={q} watched onWatch={()=>toggleWatch(q.symbol)}/>)}</div>}</section>}

   {tab!=="stocks"&&tab!=="portfolio"&&<section className="feature-page"><p className="eyebrow">PRODUCT</p><h2>{products.find(p=>p.id===tab)?.title}</h2><p className="muted">{products.find(p=>p.id===tab)?.description}</p><div className="feature-grid"><FeatureCard title="Discover" text="Browse instruments, categories and market data."/><FeatureCard title="Compare" text="Compare performance, risk and key metrics."/><FeatureCard title="Track" text="Add instruments to your personal watchlist."/><FeatureCard title="Analyse" text="Use charts, fundamentals and Claude-powered research where supported."/><FeatureCard title="Orders" text="Order-entry UI is ready for broker/API integration; no real-money order is placed by this demo."/><FeatureCard title="Alerts" text="Set price and percentage-change alerts in the next iteration." /></div></section>}

   <footer><span>grow+ research terminal</span><span>Market data is for research only. AI output is not guaranteed financial advice.</span></footer>
 </main>
}

function StockRow({q,watched,onWatch}:{q:Quote;watched:boolean;onWatch:()=>void}){return <div className="stock-row"><button className="star" onClick={onWatch}>{watched?"★":"☆"}</button><Link href={`/stock/${q.symbol}`} className="ticker"><b>{q.symbol}</b><small>{q.name}</small></Link><span className="exchange">{q.exchange}</span><strong>{`₹${q.price.toLocaleString("en-IN",{maximumFractionDigits:2})}`}</strong><em className={q.change_pct>=0?"up":"down"}>{q.change_pct>=0?"+":""}{q.change_pct.toFixed(2)}%</em></div>}
function FeatureCard({title,text}:{title:string;text:string}){return <article className="feature-card"><span>✦</span><h3>{title}</h3><p>{text}</p></article>}
