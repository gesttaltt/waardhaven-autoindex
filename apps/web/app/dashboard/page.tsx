"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, AreaChart, Area, PieChart, Pie, Cell, ReferenceLine, Brush } from "recharts";
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
  const [hoveredAsset, setHoveredAsset] = useState<string | null>(null);
  const [chartTimeRange, setChartTimeRange] = useState<string>("all");
  const [showComparison, setShowComparison] = useState(true);
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

  // Filter data based on time range
  const filterDataByRange = (data: SeriesPoint[]) => {
    if (chartTimeRange === "all" || data.length === 0) return data;
    
    const now = new Date();
    const cutoffDate = new Date();
    
    switch (chartTimeRange) {
      case "1y": cutoffDate.setFullYear(now.getFullYear() - 1); break;
      case "6m": cutoffDate.setMonth(now.getMonth() - 6); break;
      case "3m": cutoffDate.setMonth(now.getMonth() - 3); break;
      case "1m": cutoffDate.setMonth(now.getMonth() - 1); break;
      default: return data;
    }
    
    return data.filter(point => new Date(point.date) >= cutoffDate);
  };

  // Calculate performance metrics
  const currentPerformance = indexSeries.length > 0 
    ? ((indexSeries[indexSeries.length - 1].value - 100) / 100 * 100).toFixed(2)
    : "0";

  // Calculate volatility (standard deviation of returns)
  const calculateVolatility = (data: SeriesPoint[]) => {
    if (data.length < 2) return 0;
    const returns = data.slice(1).map((point, i) => 
      (point.value - data[i].value) / data[i].value
    );
    const avgReturn = returns.reduce((a, b) => a + b, 0) / returns.length;
    const variance = returns.reduce((sum, ret) => sum + Math.pow(ret - avgReturn, 2), 0) / returns.length;
    return Math.sqrt(variance) * Math.sqrt(252) * 100; // Annualized volatility
  };

  const volatility = calculateVolatility(indexSeries);
  const filteredIndexSeries = filterDataByRange(indexSeries);
  const filteredSpSeries = filterDataByRange(spSeries);

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
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.1 }}
            whileHover={{ 
              scale: 1.02, 
              y: -2,
              boxShadow: "0 8px 25px rgba(139,92,246,0.15)" 
            }}
            className="card cursor-pointer"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-neutral-400">Total Performance</p>
                <p className="text-3xl font-bold gradient-text">{currentPerformance}%</p>
              </div>
              <motion.div 
                className="text-4xl"
                whileHover={{ scale: 1.1, rotate: 5 }}
              >
                📈
              </motion.div>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.2 }}
            whileHover={{ 
              scale: 1.02, 
              y: -2,
              boxShadow: "0 8px 25px rgba(236,72,153,0.15)" 
            }}
            className="card cursor-pointer"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-neutral-400">Active Assets</p>
                <p className="text-3xl font-bold gradient-text">{allocations.length}</p>
              </div>
              <motion.div 
                className="text-4xl"
                whileHover={{ scale: 1.1, rotate: -5 }}
              >
                💼
              </motion.div>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.3 }}
            whileHover={{ 
              scale: 1.02, 
              y: -2,
              boxShadow: "0 8px 25px rgba(59,130,246,0.15)" 
            }}
            className="card cursor-pointer"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-neutral-400">Index Value</p>
                <p className="text-3xl font-bold gradient-text">
                  {indexSeries.length > 0 ? indexSeries[indexSeries.length - 1].value.toFixed(2) : "100"}
                </p>
              </div>
              <motion.div 
                className="text-4xl"
                whileHover={{ scale: 1.1, rotate: 10 }}
              >
                💎
              </motion.div>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.4 }}
            whileHover={{ 
              scale: 1.02, 
              y: -2,
              boxShadow: "0 8px 25px rgba(16,185,129,0.15)" 
            }}
            className="card cursor-pointer"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-neutral-400">Volatility (Annual)</p>
                <p className="text-3xl font-bold gradient-text">{volatility.toFixed(1)}%</p>
              </div>
              <motion.div 
                className="text-4xl"
                whileHover={{ scale: 1.1, y: -2 }}
              >
                📊
              </motion.div>
            </div>
          </motion.div>
        </div>

        {/* Performance Chart */}
        <motion.section
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="card mb-6"
        >
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-6">
            <h2 className="text-xl font-semibold gradient-text mb-4 sm:mb-0">Performance History</h2>
            
            <div className="flex flex-wrap gap-2">
              {/* Time Range Selector */}
              <div className="flex bg-white/5 rounded-lg p-1">
                {[
                  { key: "1m", label: "1M" },
                  { key: "3m", label: "3M" },
                  { key: "6m", label: "6M" },
                  { key: "1y", label: "1Y" },
                  { key: "all", label: "All" }
                ].map((range) => (
                  <button
                    key={range.key}
                    onClick={() => setChartTimeRange(range.key)}
                    className={`px-3 py-1 rounded-md text-sm font-medium transition-all ${
                      chartTimeRange === range.key
                        ? "bg-purple-500 text-white"
                        : "text-neutral-400 hover:text-white hover:bg-white/5"
                    }`}
                  >
                    {range.label}
                  </button>
                ))}
              </div>
              
              {/* Comparison Toggle */}
              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => setShowComparison(!showComparison)}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                  showComparison
                    ? "bg-purple-500/20 text-purple-300 border border-purple-500/30"
                    : "bg-white/5 text-neutral-400 hover:text-white"
                }`}
              >
                {showComparison ? "Hide" : "Show"} S&P 500
              </motion.button>
            </div>
          </div>
          {loading ? (
            <div className="h-96 skeleton rounded-xl" />
          ) : (
            <ResponsiveContainer width="100%" height={400}>
              <AreaChart 
                data={filteredIndexSeries.map((p,i) => ({
                  ...p, 
                  sp: showComparison ? filteredSpSeries[i]?.value : undefined
                }))}
                margin={{ top: 10, right: 30, left: 0, bottom: 40 }}
              >
                <defs>
                  <linearGradient id="colorIndex" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.8}/>
                    <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0.1}/>
                  </linearGradient>
                  <linearGradient id="colorSP" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#ec4899" stopOpacity={0.6}/>
                    <stop offset="95%" stopColor="#ec4899" stopOpacity={0.1}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                <XAxis 
                  dataKey="date" 
                  minTickGap={50} 
                  stroke="rgba(255,255,255,0.5)"
                  tick={{ fontSize: 12 }}
                  tickFormatter={(value) => {
                    const date = new Date(value);
                    return date.toLocaleDateString('en-US', { month: 'short', year: '2-digit' });
                  }}
                />
                <YAxis 
                  stroke="rgba(255,255,255,0.5)"
                  tick={{ fontSize: 12 }}
                  tickFormatter={(value) => `${value.toFixed(0)}`}
                />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: 'rgba(0,0,0,0.9)', 
                    border: '1px solid rgba(139,92,246,0.3)',
                    borderRadius: '12px',
                    backdropFilter: 'blur(20px)',
                    boxShadow: '0 8px 32px rgba(0,0,0,0.3)'
                  }}
                  labelFormatter={(value) => {
                    const date = new Date(value);
                    return date.toLocaleDateString('en-US', { 
                      weekday: 'short',
                      year: 'numeric', 
                      month: 'short', 
                      day: 'numeric' 
                    });
                  }}
                  formatter={(value: number, name: string) => [
                    `${value.toFixed(2)}`,
                    name === "value" ? "Autoindex" : "S&P 500"
                  ]}
                />
                <Legend />
                
                {/* Reference line at 100 */}
                <ReferenceLine y={100} stroke="rgba(255,255,255,0.3)" strokeDasharray="5 5" />
                
                <Area 
                  type="monotone" 
                  dataKey="value" 
                  name="Autoindex" 
                  stroke="#8b5cf6" 
                  strokeWidth={2}
                  fillOpacity={1} 
                  fill="url(#colorIndex)"
                  dot={false}
                  activeDot={{ r: 6, stroke: '#8b5cf6', strokeWidth: 2, fill: '#1f1f23' }}
                />
                
                {showComparison && (
                  <Area 
                    type="monotone" 
                    dataKey="sp" 
                    name="S&P 500" 
                    stroke="#ec4899" 
                    strokeWidth={2}
                    fillOpacity={1} 
                    fill="url(#colorSP)"
                    dot={false}
                    activeDot={{ r: 6, stroke: '#ec4899', strokeWidth: 2, fill: '#1f1f23' }}
                  />
                )}
                
                {/* Zoom and pan functionality */}
                <Brush 
                  dataKey="date" 
                  height={30} 
                  stroke="#8b5cf6"
                  tickFormatter={(value) => {
                    const date = new Date(value);
                    return date.toLocaleDateString('en-US', { month: 'short', year: '2-digit' });
                  }}
                />
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
                className="mt-6 p-6 rounded-xl bg-gradient-to-br from-purple-500/10 via-blue-500/10 to-pink-500/10 border border-purple-500/20 backdrop-blur-sm"
              >
                <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                  <motion.div 
                    className="text-center"
                    whileHover={{ scale: 1.05 }}
                  >
                    <p className="text-sm text-neutral-400 mb-1">Initial Investment</p>
                    <p className="text-xl font-bold text-white">
                      {simResult.currency} {amount.toLocaleString('en-US', { 
                        minimumFractionDigits: 2, 
                        maximumFractionDigits: 2 
                      })}
                    </p>
                  </motion.div>
                  
                  <motion.div 
                    className="text-center"
                    whileHover={{ scale: 1.05 }}
                  >
                    <p className="text-sm text-neutral-400 mb-1">Final Amount</p>
                    <p className="text-xl font-bold gradient-text">
                      {simResult.currency} {simResult.amount_final.toLocaleString('en-US', { 
                        minimumFractionDigits: 2, 
                        maximumFractionDigits: 2 
                      })}
                    </p>
                  </motion.div>
                  
                  <motion.div 
                    className="text-center"
                    whileHover={{ scale: 1.05 }}
                  >
                    <p className="text-sm text-neutral-400 mb-1">Total Return</p>
                    <p className={`text-xl font-bold ${simResult.roi_pct >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                      {simResult.roi_pct > 0 ? '+' : ''}{simResult.roi_pct.toFixed(2)}%
                    </p>
                  </motion.div>
                  
                  <motion.div 
                    className="text-center"
                    whileHover={{ scale: 1.05 }}
                  >
                    <p className="text-sm text-neutral-400 mb-1">Profit/Loss</p>
                    <p className={`text-xl font-bold ${simResult.amount_final >= amount ? 'text-green-400' : 'text-red-400'}`}>
                      {simResult.amount_final >= amount ? '+' : ''}{simResult.currency} {(simResult.amount_final - amount).toLocaleString('en-US', { 
                        minimumFractionDigits: 2, 
                        maximumFractionDigits: 2 
                      })}
                    </p>
                  </motion.div>
                </div>
                
                {/* Growth visualization bar */}
                <div className="mt-4">
                  <div className="flex justify-between text-xs text-neutral-400 mb-2">
                    <span>Growth Timeline</span>
                    <span>{startDate} → Today</span>
                  </div>
                  <div className="w-full bg-white/10 rounded-full h-2 overflow-hidden">
                    <motion.div 
                      className={`h-full rounded-full ${simResult.roi_pct >= 0 ? 'bg-gradient-to-r from-green-500 to-emerald-400' : 'bg-gradient-to-r from-red-500 to-orange-400'}`}
                      initial={{ width: 0 }}
                      animate={{ width: `${Math.min(Math.abs(simResult.roi_pct), 100)}%` }}
                      transition={{ duration: 1, delay: 0.5 }}
                    />
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
            whileHover={{ 
              scale: 1.01,
              boxShadow: "0 4px 20px rgba(139,92,246,0.1)" 
            }}
            className="card"
          >
            <h2 className="text-xl font-semibold mb-4 gradient-text">Portfolio Allocation</h2>
            {loading ? (
              <div className="h-64 skeleton rounded-xl" />
            ) : allocations.length > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={allocations.map(a => ({ 
                      name: a.symbol, 
                      value: a.weight * 100,
                      fullName: a.name,
                      sector: a.sector
                    }))}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={false}
                    outerRadius={hoveredAsset ? 90 : 85}
                    fill="#8884d8"
                    dataKey="value"
                    onMouseEnter={(data) => setHoveredAsset(data.name)}
                    onMouseLeave={() => setHoveredAsset(null)}
                  >
                    {allocations.map((entry, index) => (
                      <Cell 
                        key={`cell-${index}`} 
                        fill={COLORS[index % COLORS.length]}
                        stroke={hoveredAsset === entry.symbol ? '#ffffff' : 'transparent'}
                        strokeWidth={hoveredAsset === entry.symbol ? 2 : 0}
                      />
                    ))}
                  </Pie>
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: 'rgba(0,0,0,0.9)', 
                      border: '1px solid rgba(139,92,246,0.3)',
                      borderRadius: '12px',
                      backdropFilter: 'blur(20px)',
                      boxShadow: '0 8px 32px rgba(0,0,0,0.3)'
                    }}
                    formatter={(value: number, name: string, props: any) => [
                      `${value.toFixed(2)}%`,
                      (props as any).payload.fullName || (props as any).payload.name
                    ]}
                  />
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
            whileHover={{ 
              scale: 1.01,
              boxShadow: "0 4px 20px rgba(236,72,153,0.1)" 
            }}
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
                    className={`flex items-center justify-between p-3 rounded-lg transition-all cursor-pointer ${
                      hoveredAsset === a.symbol 
                        ? 'bg-purple-500/20 border border-purple-500/30' 
                        : 'bg-white/5 hover:bg-white/10'
                    }`}
                    onMouseEnter={() => setHoveredAsset(a.symbol)}
                    onMouseLeave={() => setHoveredAsset(null)}
                    whileHover={{ scale: 1.02, x: 4 }}
                  >
                    <div className="flex items-center gap-3">
                      <motion.div 
                        className="w-3 h-3 rounded-full" 
                        style={{ backgroundColor: COLORS[i % COLORS.length] }}
                        animate={{ 
                          scale: hoveredAsset === a.symbol ? 1.3 : 1,
                          boxShadow: hoveredAsset === a.symbol 
                            ? `0 0 12px ${COLORS[i % COLORS.length]}40` 
                            : 'none'
                        }}
                      />
                      <div>
                        <span className="font-medium block">{a.symbol}</span>
                        {a.name && (
                          <span className="text-xs text-neutral-500">{a.name}</span>
                        )}
                      </div>
                    </div>
                    <div className="text-right">
                      <span className="font-semibold gradient-text">
                        {(a.weight * 100).toFixed(2)}%
                      </span>
                      {a.sector && (
                        <div className="text-xs text-neutral-500">{a.sector}</div>
                      )}
                    </div>
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