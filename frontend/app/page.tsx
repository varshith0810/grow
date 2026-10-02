"use client";
import {useEffect,useState} from "react";

type Quote={symbol:string;name:string;price:number;change_pct:number;exchange:string};

export default function Home(){
 const [quotes,setQuotes]=useState<Quote[]>([]);
 const [period,setPeriod]=useState("day");
 useEffect(()=>{fetch("http://localhost:8000/api/market/quotes").then(r=>r.json()).then(setQuotes)},[]);
 const top=[...quotes].sort((a,b)=>b.change_pct-a.change_pct).slice(0,10);
 const worst=[...quotes].sort((a,b)=>a.change_pct-b.change_pct).slice(0,10);
 const list=(items:Quote[])=>items.map(q=><div className="row" key={q.symbol}><b>{q.symbol}</b><span>{q.name}</span><strong>₹{q.price.toLocaleString("en-IN")}</strong><em className={q.change_pct>=0?"up":"down"}>{q.change_pct>=0?"+":""}{q.change_pct.toFixed(2)}%</em></div>);
 return <main><header><h1>Market</h1><input placeholder="Search Indian stocks"/></header>
 <section className="tabs">{["live","day","weekly","yearly"].map(p=><button onClick={()=>setPeriod(p)} className={period===p?"active":""} key={p}>{p}</button>)}</section>
 <div className="grid"><section><h2>Top performers</h2>{list(top)}</section><section><h2>Worst performers</h2>{list(worst)}</section></div>
 <section><h2>All stocks</h2>{list(quotes)}</section></main>
}