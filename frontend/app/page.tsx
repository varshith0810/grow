"use client";
import { useEffect, useMemo, useState } from "react";
import Link from "next/link";

const API = "";

type Quote = { symbol:string; name:string; price:number; change_pct:number; exchange:string; volume?:number };
type Product = { id:string; title:string; subtitle:string; icon:string; description:string };

const products: Product[] = [
  {id:"stocks",title:"Stocks",subtitle:"Nifty 50",icon:"↗",description:"Nifty 50 stocks with live prices, charts and Claude analysis"},
  {id:"ipo",title:"IPO",subtitle:"Open & upcoming",icon:"◆",description:"Currently open and upcoming Indian IPOs"},
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
 const ranked=[...filtered].sort((a,b)=>b.change_pct-a.change_pct);
 const top=ranked.slice(0,5);
 const worst=ranked.slice(Math.max(0,ranked.length-5)).reverse();
 const watchQuotes=quotes.filter(q=>watch.includes(q.symbol));
 const money=(n:number)=>`₹${n.toLocaleString("en-IN",{maximumFractionDigits:2})}`;

 return <main className="app-shell">
   <nav className="topbar"><Link href="/" className="brand">grow<span>+</span></Link><div className="navlinks">{products.map(p=><button key={p.id} className={tab===p.id?"nav-active":""} onClick={()=>setTab(p.id)}>{p.title}</button>)}</div><button className="profile">Account</button></nav>
   <section className="hero"><div><p className="eyebrow">INDIAN MARKETS</p><h1>Investing, trading & analysis in one place.</h1><p className="muted">Nifty 50 stock research with live market data, charts, IPO tracking and Claude-powered historical analysis.</p></div><div className="market-pulse"><span>● Market data</span><b>{loading?"Loading":error?"Unavailable":"Live"}</b></div></section>
   <div className="searchbar"><span>⌕</span><input value={query} onChange={e=>setQuery(e.target.value)} placeholder="Search Nifty 50 stocks or IPOs..." /><kbd>⌘ K</kbd></div>

   <section className="product-strip">{products.map(p=><button key={p.id} className={`product-card ${tab===p.id?"selected":""}`} onClick={()=>setTab(p.id)}><span className="product-icon">{p.icon}</span><b>{p.title}</b><small>{p.subtitle}</small></button>)}</section>

   {tab==="stocks" && <>
     <section className="section-head"><div><p className="eyebrow">NIFTY 50</p><h2>Stocks</h2></div><div className="pills"><span>50 stocks</span><span>NSE</span><span>Live / last close</span></div></section>
     {error&&<div className="alert">{error}<button onClick={()=>location.reload()}>Retry</button></div>}
     <div className="market-grid">
       <section className="panel"><div className="panel-title"><h3>Top performers</h3><span>Highest % change</span></div>{top.map(q=><StockRow key={q.symbol} q={q} watched={watch.includes(q.symbol)} onWatch={()=>toggleWatch(q.symbol)} />)}</section>
       <section className="panel"><div className="panel-title"><h3>Worst performers</h3><span>Lowest % change</span></div>{worst.map(q=><StockRow key={q.symbol} q={q} watched={watch.includes(q.symbol)} onWatch={()=>toggleWatch(q.symbol)} />)}</section>
     </div>
     <section className="panel full"><div className="panel-title"><h3>All Nifty 50 stocks</h3><span>{filtered.length} stocks</span></div>{filtered.map(q=><StockRow key={q.symbol} q={q} watched={watch.includes(q.symbol)} onWatch={()=>toggleWatch(q.symbol)} />)}</section>
   </>}

   {tab==="ipo" && <IPOSection />}\n\n   <footer><span>grow+ research terminal</span><span>Market data is for research only. AI output is not guaranteed financial advice.</span></footer>
 </main>
}

function StockRow({q,watched,onWatch}:{q:Quote;watched:boolean;onWatch:()=>void}){return <div className="stock-row"><button className="star" onClick={onWatch}>{watched?"★":"☆"}</button><Link href={`/stock/${q.symbol}`} className="ticker"><b>{q.symbol}</b><small>{q.name}</small></Link><span className="exchange">{q.exchange}</span><strong>{`₹${q.price.toLocaleString("en-IN",{maximumFractionDigits:2})}`}</strong><em className={q.change_pct>=0?"up":"down"}>{q.change_pct>=0?"+":""}{q.change_pct.toFixed(2)}%</em></div>}
function IPOSection(){
 const [data,setData]=useState<{open:any[];upcoming:any[]}>({open:[],upcoming:[]});
 const [loading,setLoading]=useState(true);
 useEffect(()=>{fetch("/api/ipos",{cache:"no-store"}).then(r=>r.ok?r.json():Promise.reject()).then(d=>setData(d)).catch(()=>{}).finally(()=>setLoading(false))},[]);
 return <section className="feature-page">
   <div className="section-head"><div><p className="eyebrow">PRIMARY MARKET</p><h2>IPO</h2><p className="muted">Currently open and upcoming IPO issues.</p></div></div>
   <div className="market-grid">
    <section className="panel"><div className="panel-title"><h3>Open IPOs</h3><span>{loading?"Loading…":data.open.length+" issues"}</span></div>{data.open.map((x,i)=><IPORow key={i} data={x} status="OPEN"/>)}{!loading&&!data.open.length&&<p className="muted">No open IPOs found.</p>}</section>
    <section className="panel"><div className="panel-title"><h3>Upcoming IPOs</h3><span>{loading?"Loading…":data.upcoming.length+" issues"}</span></div>{data.upcoming.map((x,i)=><IPORow key={i} data={x} status="UPCOMING"/>)}{!loading&&!data.upcoming.length&&<p className="muted">No upcoming IPOs found.</p>}</section>
   </div>
   <p className="muted" style={{fontSize:12}}>IPO information is fetched from the public NSE issue feed when available; verify the exchange page before applying.</p>
 </section>
}
function IPORow({data,status}:{data:string[];status:"OPEN"|"UPCOMING"}){return <article className="ipo-row"><div><b>{data[0]}</b><small>{data[1]} · {data[2]} → {data[3]}</small></div><span className={status==="OPEN"?"ipo-open":"ipo-upcoming"}>{status}</span><strong>{data[4]}</strong></article>}
function FeatureCard({title,text}:{title:string;text:string}){return <article className="feature-card"><span>✦</span><h3>{title}</h3><p>{text}</p></article>}