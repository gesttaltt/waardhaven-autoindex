"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { strategyApi, StrategyConfig as IStrategyConfig, RiskMetric } from "../utils/api";

export default function StrategyConfig() {
  const [config, setConfig] = useState<IStrategyConfig | null>(null);
  const [riskMetrics, setRiskMetrics] = useState<RiskMetric[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [editMode, setEditMode] = useState(false);
  const [localConfig, setLocalConfig] = useState<IStrategyConfig | null>(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [configRes, metricsRes] = await Promise.all([
        strategyApi.getConfig(),
        strategyApi.getRiskMetrics()
      ]);
      
      setConfig(configRes.data);
      setLocalConfig(configRes.data);
      setRiskMetrics(metricsRes.data.metrics);
    } catch (error) {
      console.error("Failed to load strategy data:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    if (!localConfig) return;
    
    setSaving(true);
    try {
      await strategyApi.updateConfig(localConfig, true);
      setConfig(localConfig);
      setEditMode(false);
      
      // Reload metrics after recomputation
      setTimeout(async () => {
        const metricsRes = await strategyApi.getRiskMetrics();
        setRiskMetrics(metricsRes.data.metrics);
      }, 2000);
    } catch (error) {
      console.error("Failed to save configuration:", error);
      alert("Failed to save configuration. Please try again.");
    } finally {
      setSaving(false);
    }
  };

  const handleRebalance = async () => {
    try {
      await strategyApi.triggerRebalance(true);
      alert("Rebalancing triggered successfully");
      loadData();
    } catch (error) {
      console.error("Failed to trigger rebalance:", error);
      alert("Failed to trigger rebalance. Please try again.");
    }
  };

  const validateWeights = () => {
    if (!localConfig) return false;
    const total = localConfig.momentum_weight + localConfig.market_cap_weight + localConfig.risk_parity_weight;
    return Math.abs(total - 1.0) < 0.001;
  };

  if (loading) {
    return (
      <div className="card">
        <div className="h-96 skeleton rounded-xl" />
      </div>
    );
  }

  const latestMetric = riskMetrics[0];

  return (
    <div className="space-y-6">
      {/* Risk Metrics Summary */}
      {latestMetric && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="card"
        >
          <div className="border-b border-white/10 pb-4 mb-6">
            <h2 className="text-xl font-semibold gradient-text">Risk Analytics</h2>
            <p className="text-sm text-neutral-400 mt-1">
              Real-time risk metrics and performance indicators
            </p>
          </div>
          
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <motion.div 
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.1 }}
              className="bg-white/5 rounded-lg p-4 border border-white/10 hover:bg-white/[0.08] transition-all"
            >
              <p className="text-xs text-neutral-400 mb-1">Sharpe Ratio</p>
              <p className="text-2xl font-bold gradient-text">{latestMetric.sharpe_ratio.toFixed(2)}</p>
              <p className="text-xs text-neutral-500 mt-1">Risk-adjusted return</p>
            </motion.div>
            
            <motion.div 
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.2 }}
              className="bg-white/5 rounded-lg p-4 border border-white/10 hover:bg-white/[0.08] transition-all"
            >
              <p className="text-xs text-neutral-400 mb-1">Sortino Ratio</p>
              <p className="text-2xl font-bold gradient-text">{latestMetric.sortino_ratio.toFixed(2)}</p>
              <p className="text-xs text-neutral-500 mt-1">Downside risk-adjusted</p>
            </motion.div>
            
            <motion.div 
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.3 }}
              className="bg-white/5 rounded-lg p-4 border border-white/10 hover:bg-white/[0.08] transition-all"
            >
              <p className="text-xs text-neutral-400 mb-1">Max Drawdown</p>
              <p className="text-2xl font-bold text-orange-400">
                {(latestMetric.max_drawdown * 100).toFixed(1)}%
              </p>
              <p className="text-xs text-neutral-500 mt-1">Peak to trough</p>
            </motion.div>
            
            <motion.div 
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.4 }}
              className="bg-white/5 rounded-lg p-4 border border-white/10 hover:bg-white/[0.08] transition-all"
            >
              <p className="text-xs text-neutral-400 mb-1">Current Drawdown</p>
              <p className={`text-2xl font-bold ${
                latestMetric.current_drawdown < -0.05 ? 'text-red-400' : 'text-green-400'
              }`}>
                {(latestMetric.current_drawdown * 100).toFixed(1)}%
              </p>
              <p className="text-xs text-neutral-500 mt-1">From recent peak</p>
            </motion.div>
          </div>
        </motion.div>
      )}

      {/* Strategy Configuration */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="card"
      >
        <div className="border-b border-white/10 pb-4 mb-6">
          <div className="flex justify-between items-center">
            <div>
              <h2 className="text-xl font-semibold gradient-text">Strategy Configuration</h2>
              <p className="text-sm text-neutral-400 mt-1">
                Dynamic weighted AutoIndex strategy parameters
              </p>
            </div>
            <div className="flex gap-2">
              {editMode ? (
                <>
                  <motion.button
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    onClick={handleSave}
                    disabled={saving || !validateWeights()}
                    className="btn-primary btn-sm"
                  >
                    {saving ? (
                      <span className="flex items-center gap-2">
                        <motion.div
                          animate={{ rotate: 360 }}
                          transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                          className="w-3 h-3 border-2 border-white/30 border-t-white rounded-full"
                        />
                        Saving...
                      </span>
                    ) : (
                      "Save & Recompute"
                    )}
                  </motion.button>
                  <button
                    onClick={() => {
                      setLocalConfig(config);
                      setEditMode(false);
                    }}
                    className="btn-ghost btn-sm"
                  >
                    Cancel
                  </button>
                </>
              ) : (
                <>
                  <button onClick={() => setEditMode(true)} className="btn-secondary btn-sm">
                    Edit Configuration
                  </button>
                  <motion.button 
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    onClick={handleRebalance} 
                    className="btn-primary btn-sm"
                  >
                    Force Rebalance
                  </motion.button>
                </>
              )}
            </div>
          </div>
        </div>

        {localConfig && (
          <div className="space-y-6">
            {/* Strategy Weights */}
            <div className="bg-white/5 rounded-lg p-4 border border-white/10">
              <h3 className="font-medium text-neutral-200 mb-4 flex items-center gap-2">
                <span className="w-2 h-2 bg-purple-500 rounded-full"></span>
                Strategy Weights
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="text-xs text-neutral-400 uppercase tracking-wider">Momentum Weight</label>
                  <div className="mt-2 relative">
                    <input
                      type="number"
                      value={localConfig.momentum_weight}
                      onChange={(e) => setLocalConfig({
                        ...localConfig,
                        momentum_weight: parseFloat(e.target.value)
                      })}
                      disabled={!editMode}
                      step="0.1"
                      min="0"
                      max="1"
                      className="input"
                    />
                    <div className="mt-1 text-xs text-neutral-500">
                      {(localConfig.momentum_weight * 100).toFixed(0)}% of portfolio
                    </div>
                  </div>
                </div>
                
                <div>
                  <label className="text-xs text-neutral-400 uppercase tracking-wider">Market Cap Weight</label>
                  <div className="mt-2 relative">
                    <input
                      type="number"
                      value={localConfig.market_cap_weight}
                      onChange={(e) => setLocalConfig({
                        ...localConfig,
                        market_cap_weight: parseFloat(e.target.value)
                      })}
                      disabled={!editMode}
                      step="0.1"
                      min="0"
                      max="1"
                      className="input"
                    />
                    <div className="mt-1 text-xs text-neutral-500">
                      {(localConfig.market_cap_weight * 100).toFixed(0)}% of portfolio
                    </div>
                  </div>
                </div>
                
                <div>
                  <label className="text-xs text-neutral-400 uppercase tracking-wider">Risk Parity Weight</label>
                  <div className="mt-2 relative">
                    <input
                      type="number"
                      value={localConfig.risk_parity_weight}
                      onChange={(e) => setLocalConfig({
                        ...localConfig,
                        risk_parity_weight: parseFloat(e.target.value)
                      })}
                      disabled={!editMode}
                      step="0.1"
                      min="0"
                      max="1"
                      className="input"
                    />
                    <div className="mt-1 text-xs text-neutral-500">
                      {(localConfig.risk_parity_weight * 100).toFixed(0)}% of portfolio
                    </div>
                  </div>
                </div>
              </div>
              
              <AnimatePresence>
                {editMode && !validateWeights() && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: "auto" }}
                    exit={{ opacity: 0, height: 0 }}
                    className="mt-3 p-2 bg-red-500/10 border border-red-500/20 rounded-lg"
                  >
                    <p className="text-red-400 text-sm flex items-center gap-2">
                      <span className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></span>
                      Weights must sum to 1.0 (current: {
                        (localConfig.momentum_weight + localConfig.market_cap_weight + localConfig.risk_parity_weight).toFixed(2)
                      })
                    </p>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>

            {/* Risk Parameters */}
            <div className="bg-white/5 rounded-lg p-4 border border-white/10">
              <h3 className="font-medium text-neutral-200 mb-4 flex items-center gap-2">
                <span className="w-2 h-2 bg-blue-500 rounded-full"></span>
                Risk Parameters
              </h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div>
                  <label className="text-xs text-neutral-400 uppercase tracking-wider">Min Price ($)</label>
                  <input
                    type="number"
                    value={localConfig.min_price_threshold}
                    onChange={(e) => setLocalConfig({
                      ...localConfig,
                      min_price_threshold: parseFloat(e.target.value)
                    })}
                    disabled={!editMode}
                    step="0.1"
                    min="0.01"
                    className="input mt-2"
                  />
                </div>
                
                <div>
                  <label className="text-xs text-neutral-400 uppercase tracking-wider">Max Daily Return</label>
                  <div className="relative">
                    <input
                      type="number"
                      value={localConfig.max_daily_return}
                      onChange={(e) => setLocalConfig({
                        ...localConfig,
                        max_daily_return: parseFloat(e.target.value)
                      })}
                      disabled={!editMode}
                      step="0.1"
                      className="input mt-2"
                    />
                    <span className="absolute right-3 top-1/2 transform -translate-y-1/2 text-neutral-500 text-sm mt-1">
                      {(localConfig.max_daily_return * 100).toFixed(0)}%
                    </span>
                  </div>
                </div>
                
                <div>
                  <label className="text-xs text-neutral-400 uppercase tracking-wider">Min Daily Return</label>
                  <div className="relative">
                    <input
                      type="number"
                      value={localConfig.min_daily_return}
                      onChange={(e) => setLocalConfig({
                        ...localConfig,
                        min_daily_return: parseFloat(e.target.value)
                      })}
                      disabled={!editMode}
                      step="0.1"
                      className="input mt-2"
                    />
                    <span className="absolute right-3 top-1/2 transform -translate-y-1/2 text-neutral-500 text-sm mt-1">
                      {(localConfig.min_daily_return * 100).toFixed(0)}%
                    </span>
                  </div>
                </div>
                
                <div>
                  <label className="text-xs text-neutral-400 uppercase tracking-wider">Drop Threshold</label>
                  <div className="relative">
                    <input
                      type="number"
                      value={localConfig.daily_drop_threshold}
                      onChange={(e) => setLocalConfig({
                        ...localConfig,
                        daily_drop_threshold: parseFloat(e.target.value)
                      })}
                      disabled={!editMode}
                      step="0.01"
                      className="input mt-2"
                    />
                    <span className="absolute right-3 top-1/2 transform -translate-y-1/2 text-neutral-500 text-sm mt-1">
                      {(localConfig.daily_drop_threshold * 100).toFixed(0)}%
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {/* Rebalancing Settings */}
            <div className="bg-white/5 rounded-lg p-4 border border-white/10">
              <h3 className="font-medium text-neutral-200 mb-4 flex items-center gap-2">
                <span className="w-2 h-2 bg-green-500 rounded-full"></span>
                Rebalancing Settings
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="text-xs text-neutral-400 uppercase tracking-wider">Frequency</label>
                  <select
                    value={localConfig.rebalance_frequency}
                    onChange={(e) => setLocalConfig({
                      ...localConfig,
                      rebalance_frequency: e.target.value as 'daily' | 'weekly' | 'monthly'
                    })}
                    disabled={!editMode}
                    className="input mt-2"
                  >
                    <option value="daily">Daily</option>
                    <option value="weekly">Weekly</option>
                    <option value="monthly">Monthly</option>
                  </select>
                </div>
                
                <div>
                  <label className="text-xs text-neutral-400 uppercase tracking-wider">Last Rebalance</label>
                  <div className="input mt-2 bg-white/[0.05] cursor-not-allowed">
                    {localConfig.last_rebalance 
                      ? new Date(localConfig.last_rebalance).toLocaleDateString('en-US', {
                          year: 'numeric',
                          month: 'short',
                          day: 'numeric',
                          hour: '2-digit',
                          minute: '2-digit'
                        })
                      : "Never"
                    }
                  </div>
                </div>
              </div>
            </div>

            {/* AI Status */}
            <AnimatePresence>
              {localConfig.ai_adjusted && (
                <motion.div
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                  className="p-4 bg-gradient-to-r from-purple-500/10 to-pink-500/10 rounded-lg border border-purple-500/20"
                >
                  <div className="flex items-start gap-3">
                    <div className="mt-1">
                      <motion.div 
                        animate={{ rotate: 360 }}
                        transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                        className="w-8 h-8 rounded-full bg-gradient-to-r from-purple-500 to-pink-500 flex items-center justify-center"
                      >
                        <span className="text-white text-xs font-bold">AI</span>
                      </motion.div>
                    </div>
                    <div className="flex-1">
                      <h4 className="font-medium text-purple-300 mb-1">AI-Optimized Configuration</h4>
                      <p className="text-sm text-neutral-300">{localConfig.ai_adjustment_reason}</p>
                      <div className="mt-2 flex items-center gap-4">
                        <div className="flex items-center gap-2">
                          <div className="w-full bg-white/10 rounded-full h-2 w-24">
                            <div 
                              className="bg-gradient-to-r from-purple-500 to-pink-500 h-2 rounded-full"
                              style={{ width: `${(localConfig.ai_confidence_score || 0) * 100}%` }}
                            />
                          </div>
                          <span className="text-xs text-neutral-400">
                            {((localConfig.ai_confidence_score || 0) * 100).toFixed(0)}% confidence
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        )}
      </motion.div>
    </div>
  );
}