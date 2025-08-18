"use client";

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { diagnosticsService } from '../../services/api';

interface SystemHealth {
  overall: 'healthy' | 'warning' | 'error';
  database: {
    status: string;
    recordCount: number;
    simulationReady: boolean;
  };
  cache: {
    status: string;
    hitRate?: number;
    totalEntries: number;
  };
  dataFreshness: {
    daysOld: number;
    needsUpdate: boolean;
  };
}

interface SystemHealthIndicatorProps {
  className?: string;
}

export default function SystemHealthIndicator({ className = '' }: SystemHealthIndicatorProps) {
  const [health, setHealth] = useState<SystemHealth | null>(null);
  const [loading, setLoading] = useState(true);
  const [expanded, setExpanded] = useState(false);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());

  useEffect(() => {
    checkSystemHealth();
    const interval = setInterval(checkSystemHealth, 60000); // Check every minute
    return () => clearInterval(interval);
  }, []);

  const checkSystemHealth = async () => {
    try {
      const [dbStatus, cacheStatus, refreshStatus] = await Promise.all([
        diagnosticsService.getDatabaseStatus(),
        diagnosticsService.getCacheStatus(),
        diagnosticsService.getRefreshStatus()
      ]);

      // Calculate total records
      const totalRecords = Object.values(dbStatus.tables)
        .reduce((sum, table) => sum + table.count, 0);

      // Determine overall health
      let overall: 'healthy' | 'warning' | 'error' = 'healthy';
      
      if (!dbStatus.simulation_ready || 
          cacheStatus.status === 'error' || 
          refreshStatus.prices.days_old > 7) {
        overall = 'error';
      } else if (refreshStatus.prices.needs_update || 
                 (cacheStatus.stats?.hit_rate && cacheStatus.stats.hit_rate < 0.5) ||
                 refreshStatus.prices.days_old > 2) {
        overall = 'warning';
      }

      setHealth({
        overall,
        database: {
          status: dbStatus.simulation_ready ? 'connected' : 'error',
          recordCount: totalRecords,
          simulationReady: dbStatus.simulation_ready
        },
        cache: {
          status: cacheStatus.status,
          hitRate: cacheStatus.stats?.hit_rate,
          totalEntries: cacheStatus.stats?.total_entries || 0
        },
        dataFreshness: {
          daysOld: refreshStatus.prices.days_old || 0,
          needsUpdate: refreshStatus.prices.needs_update
        }
      });

      setLastUpdate(new Date());
    } catch (error) {
      console.error('Failed to check system health:', error);
      setHealth({
        overall: 'error',
        database: { status: 'error', recordCount: 0, simulationReady: false },
        cache: { status: 'error', totalEntries: 0 },
        dataFreshness: { daysOld: 999, needsUpdate: true }
      });
    } finally {
      setLoading(false);
    }
  };

  const getHealthColor = (status: 'healthy' | 'warning' | 'error') => {
    switch (status) {
      case 'healthy': return 'text-green-400';
      case 'warning': return 'text-yellow-400';
      case 'error': return 'text-red-400';
      default: return 'text-gray-400';
    }
  };

  const getHealthIcon = (status: 'healthy' | 'warning' | 'error') => {
    switch (status) {
      case 'healthy': return '●';
      case 'warning': return '◐';
      case 'error': return '●';
      default: return '○';
    }
  };

  const getHealthBg = (status: 'healthy' | 'warning' | 'error') => {
    switch (status) {
      case 'healthy': return 'bg-green-500/10 border-green-500/30';
      case 'warning': return 'bg-yellow-500/10 border-yellow-500/30';
      case 'error': return 'bg-red-500/10 border-red-500/30';
      default: return 'bg-gray-500/10 border-gray-500/30';
    }
  };

  if (loading) {
    return (
      <div className={`p-3 bg-gray-800/50 rounded-lg border border-gray-700 animate-pulse ${className}`}>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 bg-gray-600 rounded-full" />
          <div className="h-4 bg-gray-600 rounded w-20" />
        </div>
      </div>
    );
  }

  return (
    <motion.div
      className={`relative ${className}`}
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
    >
      {/* Main Health Indicator */}
      <motion.button
        onClick={() => setExpanded(!expanded)}
        className={`w-full p-3 rounded-lg border backdrop-blur-sm transition-all ${
          health ? getHealthBg(health.overall) : 'bg-gray-500/10 border-gray-500/30'
        } hover:shadow-lg`}
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className={`text-lg ${health ? getHealthColor(health.overall) : 'text-gray-400'}`}>
              {health ? getHealthIcon(health.overall) : '○'}
            </span>
            <div className="text-left">
              <p className="text-sm font-medium text-white">
                System Status
              </p>
              <p className="text-xs text-gray-400">
                {health?.overall === 'healthy' ? 'All systems operational' :
                 health?.overall === 'warning' ? 'Minor issues detected' :
                 'Critical issues detected'}
              </p>
            </div>
          </div>
          <div className="text-right">
            <p className="text-xs text-gray-500">
              Updated {lastUpdate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
            </p>
            <motion.div
              animate={{ rotate: expanded ? 180 : 0 }}
              transition={{ duration: 0.2 }}
              className="text-gray-400 text-sm"
            >
              ▼
            </motion.div>
          </div>
        </div>
      </motion.button>

      {/* Expanded Details */}
      <AnimatePresence>
        {expanded && health && (
          <motion.div
            initial={{ opacity: 0, height: 0, y: -10 }}
            animate={{ opacity: 1, height: 'auto', y: 0 }}
            exit={{ opacity: 0, height: 0, y: -10 }}
            transition={{ duration: 0.3 }}
            className="absolute top-full left-0 right-0 z-50 mt-2 p-4 bg-gray-900/95 backdrop-blur-sm rounded-lg border border-gray-700 shadow-xl"
          >
            <div className="space-y-4">
              {/* Database Status */}
              <div className="flex justify-between items-center">
                <div>
                  <p className="text-sm font-medium text-white">Database</p>
                  <p className="text-xs text-gray-400">
                    {health.database.recordCount.toLocaleString()} records
                  </p>
                </div>
                <div className="text-right">
                  <span className={`text-sm ${
                    health.database.simulationReady ? 'text-green-400' : 'text-red-400'
                  }`}>
                    {health.database.simulationReady ? '✓ Ready' : '✗ Not Ready'}
                  </span>
                </div>
              </div>

              {/* Cache Status */}
              <div className="flex justify-between items-center">
                <div>
                  <p className="text-sm font-medium text-white">Cache</p>
                  <p className="text-xs text-gray-400">
                    {health.cache.totalEntries.toLocaleString()} entries
                  </p>
                </div>
                <div className="text-right">
                  <span className={`text-sm ${
                    health.cache.status === 'connected' ? 'text-green-400' : 'text-red-400'
                  }`}>
                    {health.cache.hitRate ? `${(health.cache.hitRate * 100).toFixed(0)}% hit rate` : 'Disconnected'}
                  </span>
                </div>
              </div>

              {/* Data Freshness */}
              <div className="flex justify-between items-center">
                <div>
                  <p className="text-sm font-medium text-white">Data Freshness</p>
                  <p className="text-xs text-gray-400">
                    Last updated {health.dataFreshness.daysOld} days ago
                  </p>
                </div>
                <div className="text-right">
                  <span className={`text-sm ${
                    health.dataFreshness.daysOld <= 1 ? 'text-green-400' :
                    health.dataFreshness.daysOld <= 3 ? 'text-yellow-400' : 'text-red-400'
                  }`}>
                    {health.dataFreshness.needsUpdate ? '⚠ Needs Update' : '✓ Fresh'}
                  </span>
                </div>
              </div>

              {/* Quick Actions */}
              <div className="pt-2 border-t border-gray-700">
                <div className="flex gap-2">
                  <button
                    onClick={() => {
                      checkSystemHealth();
                      setExpanded(false);
                    }}
                    className="flex-1 px-3 py-1 text-xs bg-purple-600/20 hover:bg-purple-600/30 text-purple-300 rounded transition-colors"
                  >
                    Refresh
                  </button>
                  <button
                    onClick={() => {
                      window.open('/diagnostics', '_blank');
                      setExpanded(false);
                    }}
                    className="flex-1 px-3 py-1 text-xs bg-blue-600/20 hover:bg-blue-600/30 text-blue-300 rounded transition-colors"
                  >
                    Details
                  </button>
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}