"use client";

import { useEffect, useState, useMemo } from "react";
import { useRouter } from "next/navigation";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, AreaChart, Area, PieChart, Pie, Cell, ReferenceLine, Brush } from "recharts";
import { motion, AnimatePresence } from "framer-motion";
import api, { strategyApi, RiskMetric } from "../utils/api";
import SmartRefresh from "../components/SmartRefresh";

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
  const [showComparison, setShowComparison] = useState(true);  // Show S&P 500 by default
  const [showDataPanel, setShowDataPanel] = useState(false);
  const [selectedDataSeries, setSelectedDataSeries] = useState<string[]>(["autoindex", "sp500"]);
  const [showVolume, setShowVolume] = useState(false);
  const [showMovingAverage, setShowMovingAverage] = useState(false);
  const [showVolatilityBands, setShowVolatilityBands] = useState(false);
  const [individualAssets, setIndividualAssets] = useState<{[key: string]: boolean}>({});
  const [assetSeriesData, setAssetSeriesData] = useState<{[key: string]: SeriesPoint[]}>({});
  const [loadingAssets, setLoadingAssets] = useState<{[key: string]: boolean}>({});
  const [riskMetrics, setRiskMetrics] = useState<RiskMetric | null>(null);
  const token = typeof window !== "undefined" ? localStorage.getItem("token") : null;
  
  // Function to refresh dashboard data
  const refreshDashboardData = async () => {
    try {
      const [indexRes, spRes, allocRes] = await Promise.all([
        api.get('/api/v1/index/history'),
        api.get('/api/v1/benchmark/sp500'),
        api.get('/api/v1/index/current')
      ]);
      
      setIndexSeries(indexRes.data.series);
      setSpSeries(spRes.data.series);
      setAllocations(allocRes.data.allocations);
    } catch (err) {
      console.error('Failed to refresh dashboard data:', err);
    }
  };

  // Function to fetch individual asset data with better error handling
  const fetchAssetData = async (symbol: string) => {
    // Check if already loaded or loading
    if (assetSeriesData[symbol] || loadingAssets[symbol]) return;
    
    setLoadingAssets(prev => ({ ...prev, [symbol]: true }));
    
    try {
      const response = await api.get(`/api/v1/index/assets/${symbol}/history`);
      if (response.data && response.data.series) {
        setAssetSeriesData(prev => ({ 
          ...prev, 
          [symbol]: response.data.series 
        }));
      } else {
        throw new Error('Invalid response format');
      }
    } catch (err: any) {
      console.error(`Failed to fetch data for ${symbol}:`, err);
      // Show user-friendly error message
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to load asset data';
      console.warn(`${symbol}: ${errorMessage}`);
      // Remove from individual assets if fetch fails
      setIndividualAssets(prev => ({ ...prev, [symbol]: false }));
    } finally {
      setLoadingAssets(prev => ({ ...prev, [symbol]: false }));
    }
  };

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
      api.get('/api/v1/benchmark/sp500').then(r => setSpSeries(r.data.series)).catch(spErr => {
        console.warn('S&P 500 benchmark data not available:', spErr.response?.status);
        setSpSeries([]);
      }),
      api.get('/api/v1/index/current').then(r => setAllocations(r.data.allocations)),
      api.get('/api/v1/index/currencies').then(r => setCurrencies(r.data)),
      strategyApi.getRiskMetrics(1).then(r => {
        if (r.data.metrics && r.data.metrics.length > 0) {
          setRiskMetrics(r.data.metrics[0]);
        }
      }).catch(err => {
        console.warn('Risk metrics not available:', err);
      })
    ]).catch(err => {
      console.error('Failed to fetch dashboard data:', err);
    }).finally(() => {
      setLoading(false);
    });
  }, [token, router]);

  // Fetch asset data when individual assets are selected
  useEffect(() => {
    Object.entries(individualAssets).forEach(([symbol, isSelected]) => {
      if (isSelected && !assetSeriesData[symbol] && !loadingAssets[symbol]) {
        fetchAssetData(symbol);
      }
    });
  }, [individualAssets]); // Remove assetSeriesData and loadingAssets to prevent infinite loops

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

  // Calculate volatility (standard deviation of returns) with safety checks
  const calculateVolatility = (data: SeriesPoint[]) => {
    if (!data || data.length < 2) return 0;
    try {
      const returns = data.slice(1).map((point, i) => {
        const prevValue = data[i].value;
        if (prevValue === 0) return 0; // Avoid division by zero
        return (point.value - prevValue) / prevValue;
      });
      
      if (returns.length === 0) return 0;
      
      const avgReturn = returns.reduce((a, b) => a + b, 0) / returns.length;
      const variance = returns.reduce((sum, ret) => sum + Math.pow(ret - avgReturn, 2), 0) / returns.length;
      return Math.sqrt(variance) * Math.sqrt(252) * 100; // Annualized volatility
    } catch (err) {
      console.error('Error calculating volatility:', err);
      return 0;
    }
  };

  // Memoize expensive calculations
  const volatility = useMemo(() => calculateVolatility(indexSeries), [indexSeries]);
  const filteredIndexSeries = useMemo(() => filterDataByRange(indexSeries), [indexSeries, chartTimeRange]);
  const filteredSpSeries = useMemo(() => filterDataByRange(spSeries), [spSeries, chartTimeRange]);
  
  // Calculate technical indicators with improved performance
  const calculateMovingAverage = (data: SeriesPoint[], period: number = 50) => {
    if (!data || data.length < period) {
      return new Array(data?.length || 0).fill(null);
    }
    
    const result: (number | null)[] = new Array(data.length).fill(null);
    let sum = 0;
    
    // Calculate initial sum for the first period
    for (let i = 0; i < period && i < data.length; i++) {
      sum += data[i].value;
    }
    
    if (data.length >= period) {
      result[period - 1] = sum / period;
      
      // Use sliding window for efficiency
      for (let i = period; i < data.length; i++) {
        sum = sum - data[i - period].value + data[i].value;
        result[i] = sum / period;
      }
    }
    
    return result;
  };

  const calculateVolatilityBands = (data: SeriesPoint[], period: number = 20, multiplier: number = 2) => {
    const ma = calculateMovingAverage(data, period);
    
    return data.map((point, index) => {
      if (index < period - 1) return { upper: null, lower: null };
      
      const periodData = data.slice(index - period + 1, index + 1);
      const avg = ma[index];
      if (!avg) return { upper: null, lower: null };
      
      const variance = periodData.reduce((sum, p) => 
        sum + Math.pow(p.value - avg, 2), 0) / period;
      const stdDev = Math.sqrt(variance);
      
      return {
        upper: avg + (stdDev * multiplier),
        lower: avg - (stdDev * multiplier)
      };
    });
  };

  // Create properly aligned dataset for chart rendering with memoization
  const createAlignedChartData = () => {
    if (!filteredIndexSeries || filteredIndexSeries.length === 0) return [];
    
    // Create a map of SP500 data by date for efficient lookup
    const spDataMap = new Map<string, number>();
    if (filteredSpSeries && filteredSpSeries.length > 0) {
      filteredSpSeries.forEach(point => {
        spDataMap.set(point.date.toString(), point.value);
      });
    }
    
    // Create maps for individual asset data by date
    const assetDataMaps = new Map();
    Object.entries(individualAssets).forEach(([symbol, isSelected]) => {
      if (isSelected && assetSeriesData[symbol]) {
        const filteredAssetData = filterDataByRange(assetSeriesData[symbol]);
        assetDataMaps.set(symbol, new Map(
          filteredAssetData.map(point => [point.date, point.value])
        ));
      }
    });
    
    // Calculate technical indicators
    const movingAverage = showMovingAverage ? calculateMovingAverage(filteredIndexSeries, 50) : [];
    const volatilityBands = showVolatilityBands ? calculateVolatilityBands(filteredIndexSeries, 20, 2) : [];
    
    // Map index data and align all data by date
    const alignedData = filteredIndexSeries.map((point, index) => {
      const dataPoint: any = {
        date: point.date,
        value: point.value,
        sp: showComparison ? (spDataMap.get(point.date.toString()) || null) : undefined,
        ma: showMovingAverage && movingAverage[index] !== null ? movingAverage[index] : undefined,
        upperBand: showVolatilityBands && volatilityBands[index]?.upper !== null ? volatilityBands[index]?.upper : undefined,
        lowerBand: showVolatilityBands && volatilityBands[index]?.lower !== null ? volatilityBands[index]?.lower : undefined
      };
      
      // Add individual asset data with proper date handling
      assetDataMaps.forEach((assetMap, symbol) => {
        dataPoint[symbol] = assetMap.get(point.date.toString()) || null;
      });
      
      return dataPoint;
    });
    
    return alignedData;
  };
  
  // Memoize chart data creation to prevent recalculation on every render
  const alignedChartData = useMemo(() => createAlignedChartData(), [
    filteredIndexSeries,
    filteredSpSeries,
    showComparison,
    showMovingAverage,
    showVolatilityBands,
    individualAssets,
    assetSeriesData
  ]);
  
  // Calculate performance metrics
  const calculatePerformanceMetrics = () => {
    if (filteredIndexSeries.length === 0) return null;
    
    const indexStart = filteredIndexSeries[0]?.value || 100;
    const indexEnd = filteredIndexSeries[filteredIndexSeries.length - 1]?.value || 100;
    const spStart = filteredSpSeries[0]?.value || 100;
    const spEnd = filteredSpSeries[filteredSpSeries.length - 1]?.value || 100;
    
    const indexReturn = ((indexEnd - indexStart) / indexStart) * 100;
    const spReturn = ((spEnd - spStart) / spStart) * 100;
    const outperformance = indexReturn - spReturn;
    
    return {
      indexReturn,
      spReturn,
      outperformance,
      indexValue: indexEnd,
      spValue: spEnd
    };
  };
  
  // Memoize performance metrics calculation
  const performanceMetrics = useMemo(() => calculatePerformanceMetrics(), [
    filteredIndexSeries,
    filteredSpSeries
  ]);

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
          <div className="flex justify-between items-start mb-8">
            <div>
              <h1 className="text-4xl font-bold mb-2 gradient-text">Dashboard</h1>
              <p className="text-neutral-400">Track your portfolio performance in real-time</p>
            </div>
            <div className="flex items-center gap-3 mt-2">
              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => router.push("/ai-insights")}
                className="btn-primary text-sm px-4 py-2"
              >
                AI Insights
              </motion.button>
              <button
                onClick={() => router.push("/admin")}
                className="btn-ghost btn-sm"
              >
                Admin Panel
              </button>
              <button
                onClick={() => {
                  localStorage.removeItem("token");
                  router.push("/login");
                }}
                className="btn-ghost btn-sm"
              >
                Logout
              </button>
            </div>
          </div>
        </motion.div>

        {/* Performance Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.1 }}
            className="card"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-neutral-300">Total Performance</p>
                <p className="text-3xl font-bold gradient-text">{currentPerformance}%</p>
              </div>
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
                <p className="text-sm text-neutral-300">Active Assets</p>
                <p className="text-3xl font-bold gradient-text">{allocations.length}</p>
              </div>
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
                <p className="text-sm text-neutral-300">
                  {riskMetrics ? "Sharpe Ratio" : "Index Value"}
                </p>
                <p className="text-3xl font-bold gradient-text">
                  {riskMetrics 
                    ? riskMetrics.sharpe_ratio.toFixed(2)
                    : (indexSeries.length > 0 ? indexSeries[indexSeries.length - 1].value.toFixed(2) : "100")
                  }
                </p>
              </div>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.4 }}
            className="card"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-neutral-300">
                  {riskMetrics ? "Max Drawdown" : "Volatility (Annual)"}
                </p>
                <p className={`text-3xl font-bold ${
                  riskMetrics ? "text-orange-400" : "gradient-text"
                }`}>
                  {riskMetrics 
                    ? `${(riskMetrics.max_drawdown * 100).toFixed(1)}%`
                    : `${volatility.toFixed(1)}%`
                  }
                </p>
              </div>
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
          {/* Header with Title and Metrics */}
          <div className="mb-6">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-4">
              <div>
                <h2 className="text-xl font-semibold gradient-text mb-2">Performance History</h2>
                <p className="text-sm text-neutral-400">AutoIndex vs S&P 500 Benchmark Comparison</p>
              </div>
              
              {/* Performance Metrics Display */}
              {performanceMetrics && (
                <motion.div
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  className="flex gap-4 mt-4 sm:mt-0"
                >
                  <div className="text-center">
                    <p className="text-xs text-neutral-400">AutoIndex</p>
                    <p className={`text-lg font-bold ${performanceMetrics.indexReturn >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                      {performanceMetrics.indexReturn >= 0 ? '+' : ''}{performanceMetrics.indexReturn.toFixed(2)}%
                    </p>
                  </div>
                  
                  {filteredSpSeries.length > 0 ? (
                    <>
                      <div className="text-center">
                        <p className="text-xs text-neutral-400">S&P 500</p>
                        <p className={`text-lg font-bold ${performanceMetrics.spReturn >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                          {performanceMetrics.spReturn >= 0 ? '+' : ''}{performanceMetrics.spReturn.toFixed(2)}%
                        </p>
                      </div>
                      <div className="text-center">
                        <p className="text-xs text-neutral-400">Outperformance</p>
                        <p className={`text-lg font-bold ${performanceMetrics.outperformance >= 0 ? 'text-purple-400' : 'text-orange-400'}`}>
                          {performanceMetrics.outperformance >= 0 ? '+' : ''}{performanceMetrics.outperformance.toFixed(2)}%
                        </p>
                      </div>
                    </>
                  ) : (
                    <div className="text-center">
                      <p className="text-xs text-neutral-400">S&P 500 Comparison</p>
                      <p className="text-sm text-neutral-500">
                        Data not available
                      </p>
                    </div>
                  )}
                </motion.div>
              )}
            </div>
            
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
              
              {/* Data Panel Toggle */}
              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => setShowDataPanel(!showDataPanel)}
                className="btn-secondary btn-sm"
              >
{showDataPanel ? "Hide" : "Show"} Data Options
              </motion.button>
            </div>
            
            {/* Deployable Data Panel */}
            <AnimatePresence>
              {showDataPanel && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: "auto" }}
                  exit={{ opacity: 0, height: 0 }}
                  transition={{ duration: 0.3 }}
                  className="mt-4 p-4 bg-white/5 rounded-lg border border-white/10"
                >
                  <div className="mb-4">
                    <h3 className="text-sm font-medium text-neutral-300 mb-3">Chart Display Options</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      {/* Primary Data Series */}
                      <div>
                        <p className="text-xs text-neutral-400 mb-2">Primary Data</p>
                        <div className="space-y-2">
                          <button
                            onClick={() => setShowComparison(!showComparison)}
                            className={`w-full px-3 py-2 rounded-lg text-sm transition-all flex items-center justify-between ${
                              showComparison
                                ? "bg-purple-500 text-white"
                                : "bg-white/10 text-neutral-400 hover:bg-white/20"
                            } ${filteredSpSeries.length === 0 ? 'opacity-50 cursor-not-allowed' : ''}`}
                            disabled={filteredSpSeries.length === 0}
                          >
                            <span className="flex items-center gap-2">
                              <span>S&P 500 Benchmark</span>
                              {filteredSpSeries.length === 0 && (
                                <span className="text-xs opacity-75">(No Data)</span>
                              )}
                            </span>
                            <span className={`w-2 h-2 rounded-full ${showComparison && filteredSpSeries.length > 0 ? 'bg-white' : 'bg-neutral-600'}`}></span>
                          </button>
                        </div>
                      </div>
                      
                      {/* Technical Indicators */}
                      <div>
                        <p className="text-xs text-neutral-400 mb-2">Technical Indicators</p>
                        <div className="space-y-2">
                          <button
                            onClick={() => setShowVolatilityBands(!showVolatilityBands)}
                            className={`w-full px-3 py-2 rounded-lg text-sm transition-all flex items-center justify-between ${
                              showVolatilityBands
                                ? "bg-blue-500 text-white"
                                : "bg-white/10 text-neutral-400 hover:bg-white/20"
                            }`}
                          >
                            <span>Volatility Bands</span>
                            <span className={`w-2 h-2 rounded-full ${showVolatilityBands ? 'bg-white' : 'bg-neutral-600'}`}></span>
                          </button>
                          
                          <button
                            onClick={() => setShowMovingAverage(!showMovingAverage)}
                            className={`w-full px-3 py-2 rounded-lg text-sm transition-all flex items-center justify-between ${
                              showMovingAverage
                                ? "bg-green-500 text-white"
                                : "bg-white/10 text-neutral-400 hover:bg-white/20"
                            }`}
                          >
                            <span>Moving Average (50)</span>
                            <span className={`w-2 h-2 rounded-full ${showMovingAverage ? 'bg-white' : 'bg-neutral-600'}`}></span>
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  {/* Individual Assets Section */}
                  {allocations.length > 0 && (
                    <div className="mb-4">
                      <h3 className="text-sm font-medium text-neutral-300 mb-3">Individual Assets</h3>
                      <div className="grid grid-cols-2 md:grid-cols-3 gap-2 max-h-32 overflow-y-auto">
                        {allocations.slice(0, 6).map((asset, index) => (
                          <button
                            key={asset.symbol}
                            onClick={() => setIndividualAssets(prev => ({
                              ...prev,
                              [asset.symbol]: !prev[asset.symbol]
                            }))}
                            disabled={loadingAssets[asset.symbol]}
                            className={`px-2 py-1 rounded text-xs transition-all flex items-center justify-between ${
                              individualAssets[asset.symbol]
                                ? "bg-gradient-to-r from-purple-500 to-pink-500 text-white"
                                : "bg-white/10 text-neutral-400 hover:bg-white/20"
                            } ${loadingAssets[asset.symbol] ? 'opacity-50 cursor-not-allowed' : ''}`}
                          >
                            <span className="flex items-center">
                              <div 
                                className="w-2 h-2 rounded-full mr-2" 
                                style={{ backgroundColor: COLORS[(index + 2) % COLORS.length] }}
                              />
                              {asset.symbol}
                              {loadingAssets[asset.symbol] && (
                                <div className="ml-1 w-3 h-3 border border-white/30 border-t-white rounded-full animate-spin"></div>
                              )}
                            </span>
                            <span className={`w-1.5 h-1.5 rounded-full ${
                              individualAssets[asset.symbol] ? 'bg-white' : 'bg-neutral-600'
                            }`}></span>
                          </button>
                        ))}
                        {allocations.length > 6 && (
                          <div className="px-2 py-1 text-xs text-neutral-500 flex items-center">
                            +{allocations.length - 6} more
                          </div>
                        )}
                      </div>
                      <p className="text-xs text-neutral-500 mt-2">
                        Click assets to overlay their performance on the chart for comparison
                      </p>
                    </div>
                  )}
                  
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs">
                    <div className="bg-white/5 rounded-lg p-2">
                      <p className="text-neutral-400 mb-1">Data Points</p>
                      <p className="font-medium text-white">{filteredIndexSeries.length}</p>
                    </div>
                    <div className="bg-white/5 rounded-lg p-2">
                      <p className="text-neutral-400 mb-1">Date Range</p>
                      <p className="font-medium text-white">
                        {filteredIndexSeries[0]?.date ? new Date(filteredIndexSeries[0].date).toLocaleDateString() : 'N/A'}
                      </p>
                    </div>
                    <div className="bg-white/5 rounded-lg p-2">
                      <p className="text-neutral-400 mb-1">Update Status</p>
                      <p className="font-medium text-green-400">Live</p>
                    </div>
                    <div className="bg-white/5 rounded-lg p-2">
                      <p className="text-neutral-400 mb-1">Benchmark</p>
                      <p className="font-medium text-white">S&P 500</p>
                    </div>
                  </div>
                  
                  {/* Legend with interactive elements */}
                  <div className="mt-3 pt-3 border-t border-white/10">
                    <div className="flex items-center justify-between text-sm">
                      <div className="flex flex-wrap items-center gap-3">
                        <div className="flex items-center gap-2">
                          <div className="w-3 h-3 rounded-full bg-purple-500"></div>
                          <span className="text-neutral-300">AutoIndex</span>
                          <span className="text-green-400 font-medium">
                            {performanceMetrics?.indexValue.toFixed(2)}
                          </span>
                        </div>
                        {showComparison && filteredSpSeries.length > 0 && (
                          <div className="flex items-center gap-2">
                            <div className="w-3 h-3 rounded-full bg-pink-500"></div>
                            <span className="text-neutral-300">S&P 500</span>
                            <span className="text-neutral-400 font-medium">
                              {performanceMetrics?.spValue.toFixed(2)}
                            </span>
                          </div>
                        )}
                        {/* Individual Assets in Legend */}
                        {Object.entries(individualAssets).map(([symbol, isSelected], index) => {
                          if (!isSelected || !assetSeriesData[symbol]) return null;
                          
                          const assetData = assetSeriesData[symbol];
                          const currentValue = assetData[assetData.length - 1]?.value;
                          const color = COLORS[(index + 2) % COLORS.length];
                          
                          return (
                            <div key={symbol} className="flex items-center gap-2">
                              <div 
                                className="w-3 h-3 rounded-full" 
                                style={{ backgroundColor: color }}
                              ></div>
                              <span className="text-neutral-300">{symbol}</span>
                              <span className="text-neutral-400 font-medium">
                                {currentValue?.toFixed(2) || 'N/A'}
                              </span>
                            </div>
                          );
                        })}
                      </div>
                      <button
                        onClick={() => setChartTimeRange("all")}
                        className="text-xs text-purple-400 hover:text-purple-300 transition-colors"
                      >
                        Reset View
                      </button>
                    </div>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
          {loading ? (
            <div className="h-96 skeleton rounded-xl" />
          ) : (
            <ResponsiveContainer width="100%" height={400}>
              <AreaChart 
                data={alignedChartData}
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
                  formatter={(value: number, name: string) => {
                    const labels = {
                      value: "Autoindex",
                      sp: "S&P 500",
                      ma: "50-Day MA",
                      upperBand: "Upper Band",
                      lowerBand: "Lower Band"
                    };
                    // For individual assets, use the symbol as the label
                    const label = labels[name as keyof typeof labels] || name;
                    return [
                      value ? `${value.toFixed(2)}` : 'N/A',
                      label
                    ];
                  }}
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
                
                {/* Technical Indicators */}
                {showMovingAverage && (
                  <Line 
                    type="monotone" 
                    dataKey="ma" 
                    name="50-Day MA" 
                    stroke="#10b981" 
                    strokeWidth={2}
                    strokeDasharray="5 5"
                    dot={false}
                    fill="none"
                    activeDot={{ r: 4, stroke: '#10b981', strokeWidth: 2, fill: '#1f1f23' }}
                  />
                )}
                
                {showVolatilityBands && (
                  <>
                    <Line 
                      type="monotone" 
                      dataKey="upperBand" 
                      name="Upper Band" 
                      stroke="#3b82f6" 
                      strokeWidth={1}
                      strokeDasharray="3 3"
                      dot={false}
                      fill="none"
                    />
                    <Line 
                      type="monotone" 
                      dataKey="lowerBand" 
                      name="Lower Band" 
                      stroke="#3b82f6" 
                      strokeWidth={1}
                      strokeDasharray="3 3"
                      dot={false}
                      fill="none"
                    />
                  </>
                )}
                
                {/* Individual Asset Lines */}
                {Object.entries(individualAssets).map(([symbol, isSelected], index) => {
                  if (!isSelected || !assetSeriesData[symbol]) return null;
                  
                  const color = COLORS[(index + 2) % COLORS.length]; // Offset to avoid conflicts with AutoIndex and S&P 500
                  
                  return (
                    <Line 
                      key={symbol}
                      type="monotone" 
                      dataKey={symbol} 
                      name={symbol} 
                      stroke={color} 
                      strokeWidth={2}
                      dot={false}
                      fill="none"
                      activeDot={{ r: 4, stroke: color, strokeWidth: 2, fill: '#1f1f23' }}
                    />
                  );
                })}
                
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
              <label className="text-sm text-neutral-300">Amount</label>
              <input 
                className="input mt-1" 
                type="number" 
                value={amount} 
                onChange={e=>setAmount(parseFloat(e.target.value))} 
              />
            </div>
            <div>
              <label className="text-sm text-neutral-300">Currency</label>
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
              <label className="text-sm text-neutral-300">Start date</label>
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
                  <div className="text-center">
                    <p className="text-sm text-neutral-400 mb-1">Initial Investment</p>
                    <p className="text-xl font-bold text-white">
                      {simResult.currency} {amount.toLocaleString('en-US', { 
                        minimumFractionDigits: 2, 
                        maximumFractionDigits: 2 
                      })}
                    </p>
                  </div>
                  
                  <div className="text-center">
                    <p className="text-sm text-neutral-400 mb-1">Final Amount</p>
                    <p className="text-xl font-bold gradient-text">
                      {simResult.currency} {simResult.amount_final.toLocaleString('en-US', { 
                        minimumFractionDigits: 2, 
                        maximumFractionDigits: 2 
                      })}
                    </p>
                  </div>
                  
                  <div className="text-center">
                    <p className="text-sm text-neutral-400 mb-1">Total Return</p>
                    <p className={`text-xl font-bold ${simResult.roi_pct >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                      {simResult.roi_pct > 0 ? '+' : ''}{simResult.roi_pct.toFixed(2)}%
                    </p>
                  </div>
                  
                  <div className="text-center">
                    <p className="text-sm text-neutral-400 mb-1">Profit/Loss</p>
                    <p className={`text-xl font-bold ${simResult.amount_final >= amount ? 'text-green-400' : 'text-red-400'}`}>
                      {simResult.amount_final >= amount ? '+' : ''}{simResult.currency} {(simResult.amount_final - amount).toLocaleString('en-US', { 
                        minimumFractionDigits: 2, 
                        maximumFractionDigits: 2 
                      })}
                    </p>
                  </div>
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

        {/* Smart Market Data Refresh */}
        <motion.section
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.7 }}
          className="mb-8"
        >
          <SmartRefresh onRefreshComplete={refreshDashboardData} />
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