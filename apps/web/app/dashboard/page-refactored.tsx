"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";

// Components
import { PerformanceCards } from "../components/dashboard/PerformanceCards";
import { PerformanceChart } from "../components/dashboard/PerformanceChart";
import { SimulationPanel } from "../components/dashboard/SimulationPanel";
import { PortfolioAllocation } from "../components/dashboard/PortfolioAllocation";
import { TopHoldings } from "../components/dashboard/TopHoldings";
import { ErrorBoundary } from "../components/shared/ErrorBoundary";
import SmartRefresh from "../components/SmartRefresh";

// Hooks
import { usePortfolioData } from "../hooks/usePortfolioData";
import { useSimulation } from "../hooks/useSimulation";

// Types
import { TimeRange } from "../types/chart";

// Constants
import { CHART_CONFIG } from "../constants/config";

export default function Dashboard() {
  const router = useRouter();
  const [chartTimeRange, setChartTimeRange] = useState<TimeRange>(CHART_CONFIG.DEFAULT_TIME_RANGE);
  const [showComparison, setShowComparison] = useState(true);
  const [showDataPanel, setShowDataPanel] = useState(false);
  const [showMovingAverage, setShowMovingAverage] = useState(false);
  const [showVolatilityBands, setShowVolatilityBands] = useState(false);
  const [individualAssets, setIndividualAssets] = useState<{[key: string]: boolean}>({});
  
  const token = typeof window !== "undefined" ? localStorage.getItem("token") : null;

  // Use custom hooks
  const {
    indexSeries,
    spSeries,
    allocations,
    riskMetrics,
    loading,
    error,
    refresh: refreshDashboardData,
  } = usePortfolioData();

  const {
    amount,
    setAmount,
    currency,
    setCurrency,
    startDate,
    setStartDate,
    simResult,
    simulating,
    runSimulation,
  } = useSimulation();

  useEffect(() => {
    if (!token) {
      router.push("/login");
    }
  }, [token, router]);

  if (error) {
    return (
      <main className="min-h-screen relative">
        <div className="fixed inset-0 gradient-bg opacity-5" />
        <div className="max-w-7xl mx-auto px-6 py-10 relative">
          <div className="card p-8 text-center">
            <h2 className="text-2xl font-bold text-red-400 mb-4">Error Loading Dashboard</h2>
            <p className="text-neutral-400 mb-6">{error}</p>
            <button onClick={refreshDashboardData} className="btn-primary">
              Retry
            </button>
          </div>
        </div>
      </main>
    );
  }

  return (
    <ErrorBoundary>
      <main className="min-h-screen relative">
        {/* Animated background */}
        <div className="fixed inset-0 gradient-bg opacity-5" />
        
        <div className="max-w-7xl mx-auto px-6 py-10 relative">
          {/* Header */}
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
          <PerformanceCards
            indexSeries={indexSeries}
            allocationsCount={allocations.length}
            riskMetrics={riskMetrics}
          />

          {/* Performance Chart */}
          <PerformanceChart
            indexSeries={indexSeries}
            spSeries={spSeries}
            loading={loading}
            chartTimeRange={chartTimeRange}
            setChartTimeRange={setChartTimeRange}
            showComparison={showComparison}
            setShowComparison={setShowComparison}
            showDataPanel={showDataPanel}
            setShowDataPanel={setShowDataPanel}
            showMovingAverage={showMovingAverage}
            setShowMovingAverage={setShowMovingAverage}
            showVolatilityBands={showVolatilityBands}
            setShowVolatilityBands={setShowVolatilityBands}
            individualAssets={individualAssets}
            setIndividualAssets={setIndividualAssets}
            allocations={allocations}
          />

          {/* Simulation Panel */}
          <SimulationPanel
            amount={amount}
            setAmount={setAmount}
            currency={currency}
            setCurrency={setCurrency}
            startDate={startDate}
            setStartDate={setStartDate}
            simResult={simResult}
            simulating={simulating}
            onSimulate={runSimulation}
          />

          {/* Smart Market Data Refresh */}
          <motion.section
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.7 }}
            className="mb-8"
          >
            <SmartRefresh onRefreshComplete={refreshDashboardData} />
          </motion.section>

          {/* Portfolio Allocation & Top Holdings */}
          <div className="grid md:grid-cols-2 gap-6">
            <PortfolioAllocation 
              allocations={allocations} 
              loading={loading} 
            />
            <TopHoldings 
              allocations={allocations} 
              loading={loading} 
            />
          </div>
        </div>
      </main>
    </ErrorBoundary>
  );
}