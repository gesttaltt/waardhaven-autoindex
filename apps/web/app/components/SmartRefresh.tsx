"use client";

import { useState, useEffect } from "react";
import { marketDataApi, DatabaseStatus, SmartRefreshResponse, RefreshStatusResponse } from "../utils/api";

interface SmartRefreshProps {
  onRefreshComplete?: () => void;
}

const RefreshModeInfo = {
  auto: {
    name: "Auto",
    description: "Intelligently chooses the best strategy based on your API plan",
    icon: "AUTO",
    color: "blue"
  },
  minimal: {
    name: "Minimal",
    description: "Fetches only priority assets (optimized for free tier)",
    icon: "MIN",
    color: "green"
  },
  cached: {
    name: "Cached",
    description: "Uses cached data only (no API calls)",
    icon: "CACHE",
    color: "gray"
  },
  full: {
    name: "Full",
    description: "Complete refresh with rate limiting protection",
    icon: "FULL",
    color: "purple"
  }
};

export default function SmartRefresh({ onRefreshComplete }: SmartRefreshProps) {
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [refreshStatus, setRefreshStatus] = useState<RefreshStatusResponse | null>(null);
  const [databaseStatus, setDatabaseStatus] = useState<DatabaseStatus | null>(null);
  const [selectedMode, setSelectedMode] = useState<'auto' | 'minimal' | 'cached' | 'full'>('auto');
  const [lastRefreshResult, setLastRefreshResult] = useState<SmartRefreshResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Load initial status
  useEffect(() => {
    loadStatus();
  }, []);

  const loadStatus = async () => {
    try {
      const [refreshRes, dbRes] = await Promise.all([
        marketDataApi.getRefreshStatus(),
        marketDataApi.getDatabaseStatus()
      ]);
      
      setRefreshStatus(refreshRes.data);
      setDatabaseStatus(dbRes.data);
      setError(null);
    } catch (err: any) {
      console.error('Error loading status:', err);
      setError('Failed to load status: ' + (err.response?.data?.detail || err.message));
    }
  };

  const handleSmartRefresh = async () => {
    setIsRefreshing(true);
    setError(null);
    setLastRefreshResult(null);

    try {
      const response = await marketDataApi.triggerSmartRefresh(selectedMode);
      setLastRefreshResult(response.data);
      
      // Wait a moment then reload status
      setTimeout(() => {
        loadStatus();
        if (onRefreshComplete) {
          onRefreshComplete();
        }
      }, 2000);
      
    } catch (err: any) {
      console.error('Smart refresh failed:', err);
      setError('Smart refresh failed: ' + (err.response?.data?.detail || err.message));
    } finally {
      setIsRefreshing(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'OK': return 'text-green-400';
      case 'EMPTY': return 'text-yellow-400';
      case 'ERROR': return 'text-red-400';
      default: return 'text-neutral-400';
    }
  };

  const isDataStale = refreshStatus?.prices.days_old && refreshStatus.prices.days_old > 1;
  const needsRefresh = refreshStatus?.prices.needs_update || !databaseStatus?.simulation_ready;

  return (
    <div className="card">
      <div className="border-b border-white/10 pb-4">
        <h2 className="text-xl font-semibold gradient-text flex items-center gap-2">
          Smart Market Data Refresh
        </h2>
        <p className="text-sm text-neutral-400 mt-1">
          Intelligent market data management with rate limiting protection
        </p>
      </div>

      {/* Current Status */}
      {refreshStatus && (
        <div className="bg-white/5 rounded-lg p-4">
          <h3 className="font-medium text-neutral-200 mb-3">Current Status</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-neutral-400">Assets:</span>
              <span className="ml-2 font-medium text-white">{refreshStatus.assets.count} symbols</span>
            </div>
            <div>
              <span className="text-neutral-400">Latest data:</span>
              <span className="ml-2 font-medium text-white">
                {refreshStatus.prices.latest_date || 'No data'}
                {refreshStatus.prices.days_old && (
                  <span className={`ml-1 ${isDataStale ? 'text-yellow-400' : 'text-green-400'}`}>
                    ({refreshStatus.prices.days_old} days old)
                  </span>
                )}
              </span>
            </div>
            <div className="md:col-span-2">
              <span className="text-neutral-400">Recommendation:</span>
              <span className={`ml-2 font-medium ${needsRefresh ? 'text-orange-400' : 'text-green-400'}`}>
                {refreshStatus.recommendation}
              </span>
            </div>
          </div>
        </div>
      )}

      {/* Database Status */}
      {databaseStatus && (
        <div className="bg-white/5 rounded-lg p-4">
          <h3 className="font-medium text-neutral-200 mb-3">Database Status</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
            {Object.entries(databaseStatus.tables).map(([table, info]) => (
              <div key={table} className="text-center">
                <div className={`font-medium ${getStatusColor(info.status)}`}>
                  {info.count.toLocaleString()}
                </div>
                <div className="text-neutral-400 capitalize">{table}</div>
              </div>
            ))}
          </div>
          <div className={`mt-3 text-sm font-medium ${
            databaseStatus.simulation_ready ? 'text-green-400' : 'text-orange-400'
          }`}>
            {databaseStatus.message}
          </div>
        </div>
      )}

      {/* Refresh Mode Selection */}
      <div>
        <h3 className="font-medium text-neutral-200 mb-3">Refresh Mode</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {Object.entries(RefreshModeInfo).map(([mode, info]) => (
            <button
              key={mode}
              onClick={() => setSelectedMode(mode as any)}
              className={`p-3 rounded-lg border-2 text-left transition-all ${
                selectedMode === mode
                  ? 'border-purple-500 bg-purple-500/20'
                  : 'border-white/20 hover:border-white/30 bg-white/5'
              }`}
            >
              <div className="flex items-center gap-2 mb-1">
                <span className="text-xs font-mono bg-white/10 px-1.5 py-0.5 rounded">{info.icon}</span>
                <span className="font-medium text-white">{info.name}</span>
              </div>
              <p className="text-xs text-neutral-400">{info.description}</p>
            </button>
          ))}
        </div>
      </div>

      {/* Action Button */}
      <div className="space-y-3">
        <button
          onClick={handleSmartRefresh}
          disabled={isRefreshing}
          className={`btn-primary w-full ${
            isRefreshing
              ? 'opacity-50 cursor-not-allowed'
              : ''
          }`}
        >
          {isRefreshing ? (
            <span className="flex items-center justify-center gap-2">
              <div className="animate-spin h-4 w-4 border-2 border-white border-t-transparent rounded-full"></div>
              Refreshing in {RefreshModeInfo[selectedMode].name} mode...
            </span>
          ) : (
`Start ${RefreshModeInfo[selectedMode].name} Refresh`
          )}
        </button>

        <button
          onClick={loadStatus}
          className="btn-ghost w-full btn-sm"
        >
Refresh Status
        </button>
      </div>

      {/* Results */}
      {lastRefreshResult && (
        <div className="bg-green-500/20 border border-green-500/30 rounded-lg p-4">
          <h4 className="font-medium text-green-400 mb-2">Refresh Started</h4>
          <p className="text-sm text-green-300 mb-2">{lastRefreshResult.message}</p>
          <div className="text-xs text-green-400">
            <div><strong>Mode:</strong> {lastRefreshResult.mode}</div>
            <div><strong>Features:</strong> {lastRefreshResult.features.join(', ')}</div>
            <div className="mt-1 italic">{lastRefreshResult.note}</div>
          </div>
        </div>
      )}

      {/* Error Display */}
      {error && (
        <div className="bg-red-500/20 border border-red-500/30 rounded-lg p-4">
          <h4 className="font-medium text-red-400 mb-2">Error</h4>
          <p className="text-sm text-red-300">{error}</p>
        </div>
      )}

      {/* Help Text */}
      <div className="text-xs text-neutral-500 space-y-1">
        <p><strong>Tip:</strong> Use "Minimal" mode for free TwelveData plans to avoid rate limits.</p>
        <p><strong>Performance:</strong> Smart refresh automatically handles caching and rate limiting.</p>
        <p><strong>Background:</strong> Refresh runs in the background - you can continue using the app.</p>
      </div>
    </div>
  );
}