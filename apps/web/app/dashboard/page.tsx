"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, AreaChart, Area, PieChart, Pie, Cell } from "recharts";
import { motion, AnimatePresence } from "framer-motion";
import api from "../utils/api";

type SeriesPoint = { date: string; value: number };

export default function Dashboard() {
  const router = useRouter();
  const [indexSeries, setIndexSeries] = useState<SeriesPoint[]>([]);
  const [spSeries, setSpSeries] = useState<SeriesPoint[]>([]);
  const [allocations, setAllocations] = useState<{symbol:string; weight:number; name?:string; sector?:string}[]>([]);
  const [amount, setAmount] = useState(10000);
  const [currency, setCurrency] = useState("USD");
  const [currencies, setCurrencies] = useState<{[key: string]: string}>({});
  const [startDate, setStartDate] = useState<string>("2019-01-01");
  const [simResult, setSimResult] = useState<{amount_final:number; roi_pct:number; currency:string} | null>(null);
  const [loading, setLoading] = useState(true);
  const [simulating, setSimulating] = useState(false);
  const token = typeof window !== "undefined" ? localStorage.getItem("token") : null;

  // Chart colors for pie chart
  const COLORS = ['#8b5cf6', '#ec4899', '#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#06b6d4', '#a855f7'];

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
    }).finally(() => {
      setLoading(false);
    });
  }, [token, router]);

  const runSimulation = async () => {
    setSimulating(true);
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
    } finally {
      setSimulating(false);
    }
  };

  // Calculate performance metrics
  const currentPerformance = indexSeries.length > 0 
    ? ((indexSeries[indexSeries.length - 1].value - 100) / 100 * 100).toFixed(2)
    : "0";

  return (
    <main className="min-h-screen relative">
      {/* Animated background */}
      <div className="fixed inset-0 gradient-bg opacity-5" />
      
      <div className="max-w-7xl mx-auto px-6 py-10 relative">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <h1 className="text-4xl font-bold mb-2 gradient-text">Dashboard</h1>
          <p className="text-neutral-400 mb-8">Track your portfolio performance in real-time</p>
        </motion.div>

        {/* Performance Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.1 }}
            className="card"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-neutral-400">Total Performance</p>
                <p className="text-3xl font-bold gradient-text">{currentPerformance}%</p>
              </div>
              <div className="text-4xl">📈</div>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.2 }}
            className="card"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-neutral-400">Active Assets</p>
                <p className="text-3xl font-bold gradient-text">{allocations.length}</p>
              </div>
              <div className="text-4xl">💼</div>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.3 }}
            className="card"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-neutral-400">Index Value</p>
                <p className="text-3xl font-bold gradient-text">
                  {indexSeries.length > 0 ? indexSeries[indexSeries.length - 1].value.toFixed(2) : "100"}
                </p>
              </div>
              <div className="text-4xl">💎</div>
            </div>
          </motion.div>
        </div>

        {/* Performance Chart */}
        <motion.section
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="card mb-6"
        >
          <h2 className="text-xl font-semibold mb-4 gradient-text">Performance History</h2>
          {loading ? (
            <div className="h-64 skeleton rounded-xl" />
          ) : (
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={indexSeries.map((p,i) => ({...p, sp: spSeries[i]?.value}))}>
                <defs>
                  <linearGradient id="colorIndex" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.8}/>
                    <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0}/>
                  </linearGradient>
                  <linearGradient id="colorSP" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#ec4899" stopOpacity={0.8}/>
                    <stop offset="95%" stopColor="#ec4899" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                <XAxis dataKey="date" minTickGap={32} stroke="rgba(255,255,255,0.5)" />
                <YAxis stroke="rgba(255,255,255,0.5)" />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: 'rgba(0,0,0,0.8)', 
                    border: '1px solid rgba(255,255,255,0.2)',
                    borderRadius: '8px',
                    backdropFilter: 'blur(10px)'
                  }} 
                />
                <Legend />
                <Area type="monotone" dataKey="value" name="Autoindex" stroke="#8b5cf6" fillOpacity={1} fill="url(#colorIndex)" />
                <Area type="monotone" dataKey="sp" name="S&P 500" stroke="#ec4899" fillOpacity={1} fill="url(#colorSP)" />
              </AreaChart>
            </ResponsiveContainer>
          )}
        </motion.section>

        {/* Simulation Section */}
        <motion.section
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="card mb-6"
        >
          <h2 className="text-xl font-semibold mb-4 gradient-text">Investment Simulator</h2>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <label className="text-sm text-neutral-400">Amount</label>
              <input 
                className="input mt-1" 
                type="number" 
                value={amount} 
                onChange={e=>setAmount(parseFloat(e.target.value))} 
              />
            </div>
            <div>
              <label className="text-sm text-neutral-400">Currency</label>
              <select 
                className="input mt-1" 
                value={currency} 
                onChange={e=>setCurrency(e.target.value)}
              >
                {Object.entries(currencies).map(([code, name]) => (
                  <option key={code} value={code}>{code} - {name}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="text-sm text-neutral-400">Start date</label>
              <input 
                className="input mt-1" 
                type="date" 
                value={startDate} 
                onChange={e=>setStartDate(e.target.value)} 
              />
            </div>
            <div className="flex items-end">
              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                className="btn w-full relative"
                onClick={runSimulation}
                disabled={simulating}
              >
                {simulating ? (
                  <span className="flex items-center justify-center gap-2">
                    <motion.div
                      animate={{ rotate: 360 }}
                      transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                      className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full"
                    />
                    Simulating...
                  </span>
                ) : (
                  "Run Simulation"
                )}
              </motion.button>
            </div>
          </div>

          <AnimatePresence>
            {simResult && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: "auto" }}
                exit={{ opacity: 0, height: 0 }}
                className="mt-6 p-4 rounded-xl bg-gradient-to-r from-purple-500/10 to-pink-500/10 border border-purple-500/20"
              >
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-neutral-400">Final Amount</p>
                    <p className="text-2xl font-bold">
                      {simResult.currency} {simResult.amount_final.toLocaleString('en-US', { 
                        minimumFractionDigits: 2, 
                        maximumFractionDigits: 2 
                      })}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-neutral-400">Return on Investment</p>
                    <p className="text-2xl font-bold gradient-text">
                      {simResult.roi_pct > 0 ? '+' : ''}{simResult.roi_pct.toFixed(2)}%
                    </p>
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </motion.section>

        {/* Portfolio Allocation */}
        <div className="grid md:grid-cols-2 gap-6">
          <motion.section
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.6 }}
            className="card"
          >
            <h2 className="text-xl font-semibold mb-4 gradient-text">Portfolio Allocation</h2>
            {loading ? (
              <div className="h-64 skeleton rounded-xl" />
            ) : allocations.length > 0 ? (
              <ResponsiveContainer width="100%" height={250}>
                <PieChart>
                  <Pie
                    data={allocations.map(a => ({ 
                      name: a.symbol, 
                      value: a.weight * 100 
                    }))}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name} ${(percent).toFixed(1)}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {allocations.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <p className="text-neutral-400">No allocations available</p>
            )}
          </motion.section>

          <motion.section
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.7 }}
            className="card"
          >
            <h2 className="text-xl font-semibold mb-4 gradient-text">Top Holdings</h2>
            <div className="space-y-3">
              {loading ? (
                <>
                  <div className="h-12 skeleton rounded-lg" />
                  <div className="h-12 skeleton rounded-lg" />
                  <div className="h-12 skeleton rounded-lg" />
                </>
              ) : (
                allocations.slice(0, 5).map((a, i) => (
                  <motion.div
                    key={a.symbol}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.8 + i * 0.1 }}
                    className="flex items-center justify-between p-3 rounded-lg bg-white/5 hover:bg-white/10 transition-all"
                  >
                    <div className="flex items-center gap-3">
                      <div 
                        className="w-3 h-3 rounded-full" 
                        style={{ backgroundColor: COLORS[i % COLORS.length] }}
                      />
                      <span className="font-medium">{a.symbol}</span>
                    </div>
                    <span className="text-neutral-400">
                      {(a.weight * 100).toFixed(2)}%
                    </span>
                  </motion.div>
                ))
              )}
            </div>
          </motion.section>
        </div>
      </div>
    </main>
  );
}