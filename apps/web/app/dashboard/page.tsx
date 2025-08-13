"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts";
import api from "../utils/api";

type SeriesPoint = { date: string; value: number };

export default function Dashboard() {
  const router = useRouter();
  const [indexSeries, setIndexSeries] = useState<SeriesPoint[]>([]);
  const [spSeries, setSpSeries] = useState<SeriesPoint[]>([]);
  const [allocations, setAllocations] = useState<{symbol:string; weight:number;}[]>([]);
  const [amount, setAmount] = useState(10000);
  const [currency, setCurrency] = useState("USD");
  const [currencies, setCurrencies] = useState<{[key: string]: string}>({});
  const [startDate, setStartDate] = useState<string>("2019-01-01");
  const [simResult, setSimResult] = useState<{amount_final:number; roi_pct:number; currency:string} | null>(null);
  const token = typeof window !== "undefined" ? localStorage.getItem("token") : null;

  useEffect(() => {
    if (!token) {
      router.push("/login");
      return;
    }
    
    // Fetch all data in parallel
    Promise.all([
      api.get('/api/v1/index/history').then(r => setIndexSeries(r.data.series)),
      api.get('/api/v1/benchmark/sp500').then(r => setSpSeries(r.data.series)),
      api.get('/api/v1/index/current').then(r => setAllocations(r.data.allocations)),
      api.get('/api/v1/index/currencies').then(r => setCurrencies(r.data))
    ]).catch(err => {
      console.error('Failed to fetch dashboard data:', err);
    });
  }, [token, router]);

  const runSimulation = async () => {
    try {
      const r = await api.post('/api/v1/index/simulate', { 
        amount, 
        start_date: startDate,
        currency: currency 
      });
      setSimResult({ 
        amount_final: r.data.amount_final, 
        roi_pct: r.data.roi_pct,
        currency: r.data.currency 
      });
    } catch (error) {
      console.error('Simulation failed:', error);
      alert('Failed to run simulation. Please try again.');
    }
  };

  return (
    <main className="min-h-screen max-w-6xl mx-auto px-6 py-10">
      <h1 className="text-3xl font-bold">Dashboard</h1>

      <section className="card mt-6">
        <h2 className="text-xl font-semibold">Performance</h2>
        <div className="h-80 w-full mt-4">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={indexSeries.map((p,i) => ({...p, sp: spSeries[i]?.value}))}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" minTickGap={32}/>
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="value" name="Autoindex" dot={false} />
              <Line type="monotone" dataKey="sp" name="S&P 500" dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </section>

      <section className="card mt-6">
        <h2 className="text-xl font-semibold">Simulation</h2>
        <div className="mt-4 grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="text-sm text-neutral-400">Amount</label>
            <input className="input mt-1" type="number" value={amount} onChange={e=>setAmount(parseFloat(e.target.value))} />
          </div>
          <div>
            <label className="text-sm text-neutral-400">Currency</label>
            <select className="input mt-1" value={currency} onChange={e=>setCurrency(e.target.value)}>
              {Object.entries(currencies).map(([code, name]) => (
                <option key={code} value={code}>{code} - {name}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="text-sm text-neutral-400">Start date</label>
            <input className="input mt-1" type="date" value={startDate} onChange={e=>setStartDate(e.target.value)} />
          </div>
          <div className="flex items-end">
            <button className="btn w-full" onClick={runSimulation}>Run Simulation</button>
          </div>
        </div>
        {simResult && (
          <div className="mt-4 text-neutral-300">
            <p>Final amount: <b>{simResult.currency} {simResult.amount_final.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</b></p>
            <p>ROI: <b>{simResult.roi_pct.toFixed(2)}%</b></p>
          </div>
        )}
      </section>

      <section className="card mt-6">
        <h2 className="text-xl font-semibold">Current Allocation</h2>
        <div className="mt-4 overflow-x-auto">
          <table className="w-full text-left">
            <thead className="text-neutral-400">
              <tr><th className="py-2">Symbol</th><th>Weight</th></tr>
            </thead>
            <tbody>
              {allocations.map((a, idx) => (
                <tr key={idx} className="border-t border-white/5">
                  <td className="py-2">{a.symbol}</td>
                  <td>{(a.weight*100).toFixed(2)}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="mt-4">
          <button className="btn">Execute Order (Mock)</button>
        </div>
      </section>
    </main>
  );
}
