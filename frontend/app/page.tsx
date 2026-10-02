"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";

const API = "";

type Quote = {
  symbol: string;
  name: string;
  price: number;
  change_pct: number;
  exchange: string;
};

export default function Home() {
  const [quotes, setQuotes] = useState<Quote[]>([]);
  const [period, setPeriod] = useState("day");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let cancelled = false;

    async function loadQuotes() {
      setLoading(true);
      setError("");

      try {
        const response = await fetch(`${API}/api/market/quotes`, {
          cache: "no-store",
        });

        if (!response.ok) {
          throw new Error(`Market API returned HTTP ${response.status}`);
        }

        const data = await response.json();

        if (!Array.isArray(data)) {
          throw new Error("Market API returned an invalid response");
        }

        if (!cancelled) setQuotes(data);
      } catch (err) {
        if (!cancelled) {
          setQuotes([]);
          setError(
            err instanceof Error
              ? err.message
              : "Unable to connect to the market API"
          );
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    loadQuotes();
    const timer = setInterval(loadQuotes, 60_000);

    return () => {
      cancelled = true;
      clearInterval(timer);
    };
  }, []);

  const top = useMemo(
    () => [...quotes].sort((a, b) => b.change_pct - a.change_pct).slice(0, 10),
    [quotes]
  );

  const worst = useMemo(
    () => [...quotes].sort((a, b) => a.change_pct - b.change_pct).slice(0, 10),
    [quotes]
  );

  const list = (items: Quote[]) =>
    items.map((q) => (
      <Link href={`/stock/${q.symbol}`} className="row" key={q.symbol}>
        <b>{q.symbol}</b>
        <span>{q.name}</span>
        <strong>₹{q.price.toLocaleString("en-IN")}</strong>
        <em className={q.change_pct >= 0 ? "up" : "down"}>
          {q.change_pct >= 0 ? "+" : ""}
          {q.change_pct.toFixed(2)}%
        </em>
      </Link>
    ));

  return (
    <main>
      <header>
        <h1>Market</h1>
        <input placeholder="Search Indian stocks" />
      </header>

      <section className="tabs">
        {["live", "day", "weekly", "yearly"].map((p) => (
          <button
            onClick={() => setPeriod(p)}
            className={period === p ? "active" : ""}
            key={p}
          >
            {p}
          </button>
        ))}
      </section>

      {error && (
        <section>
          <h2>Market data unavailable</h2>
          <p>{error}</p>
          <p>
            API: <code>{API}</code>
          </p>
        </section>
      )}

      {loading && !error && (
        <section>
          <p>Loading market data…</p>
        </section>
      )}

      {!loading && !error && quotes.length === 0 && (
        <section>
          <h2>No market data returned</h2>
          <p>The backend is reachable, but the market-data provider returned no quotes.</p>
        </section>
      )}

      <div className="grid">
        <section>
          <h2>Top performers</h2>
          {!loading && !error && list(top)}
        </section>

        <section>
          <h2>Worst performers</h2>
          {!loading && !error && list(worst)}
        </section>
      </div>

      <section>
        <h2>All stocks</h2>
        {!loading && !error && list(quotes)}
      </section>
    </main>
  );
}
