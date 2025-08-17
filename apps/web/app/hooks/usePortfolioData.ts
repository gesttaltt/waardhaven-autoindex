import { useState, useEffect, useCallback } from 'react';
import { SeriesPoint, AllocationItem, RiskMetric } from '../types/portfolio';
import { portfolioService } from '../services/api/portfolio';
import { marketService } from '../services/api/market';

export interface UsePortfolioDataReturn {
  indexSeries: SeriesPoint[];
  spSeries: SeriesPoint[];
  allocations: AllocationItem[];
  riskMetrics: RiskMetric | null;
  loading: boolean;
  error: string | null;
  refresh: () => Promise<void>;
}

/**
 * Custom hook for fetching and managing portfolio data
 * Follows clean architecture principles with separation of concerns
 */
export function usePortfolioData(): UsePortfolioDataReturn {
  const [indexSeries, setIndexSeries] = useState<SeriesPoint[]>([]);
  const [spSeries, setSpSeries] = useState<SeriesPoint[]>([]);
  const [allocations, setAllocations] = useState<AllocationItem[]>([]);
  const [riskMetrics, setRiskMetrics] = useState<RiskMetric | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      // Parallel fetch with error handling for each request
      const [indexData, spData, allocData, metricsData] = await Promise.allSettled([
        portfolioService.getIndexHistory(),
        marketService.getSP500History(),
        portfolioService.getCurrentAllocations(),
        portfolioService.getRiskMetrics(),
      ]);

      // Handle index data
      if (indexData.status === 'fulfilled') {
        setIndexSeries(indexData.value.series);
      } else {
        console.error('Failed to fetch index history:', indexData.reason);
        setError('Failed to load index data');
      }

      // Handle S&P 500 data (optional - don't fail if unavailable)
      if (spData.status === 'fulfilled') {
        setSpSeries(spData.value.series);
      } else {
        console.warn('S&P 500 data not available');
        setSpSeries([]);
      }

      // Handle allocation data
      if (allocData.status === 'fulfilled') {
        setAllocations(allocData.value.allocations);
      } else {
        console.error('Failed to fetch allocations:', allocData.reason);
      }

      // Handle risk metrics (optional)
      if (metricsData.status === 'fulfilled' && metricsData.value.metrics?.length > 0) {
        setRiskMetrics(metricsData.value.metrics[0]);
      }

      // Only show error if critical data failed
      if (indexData.status === 'rejected' && allocData.status === 'rejected') {
        setError('Failed to load portfolio data. Please try again.');
      }
    } catch (err) {
      console.error('Failed to fetch portfolio data:', err);
      setError('An unexpected error occurred. Please try again.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return {
    indexSeries,
    spSeries,
    allocations,
    riskMetrics,
    loading,
    error,
    refresh: fetchData,
  };
}

/**
 * Hook for fetching individual asset history
 */
export function useAssetHistory(symbol: string, enabled: boolean = true) {
  const [data, setData] = useState<SeriesPoint[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchAssetData = useCallback(async () => {
    if (!enabled || !symbol) return;
    
    try {
      setLoading(true);
      setError(null);
      const response = await portfolioService.getAssetHistory(symbol);
      setData(response.series);
    } catch (err) {
      console.error(`Failed to fetch data for ${symbol}:`, err);
      setError(`Failed to load ${symbol} data`);
    } finally {
      setLoading(false);
    }
  }, [symbol, enabled]);

  useEffect(() => {
    fetchAssetData();
  }, [fetchAssetData]);

  return { data, loading, error, refetch: fetchAssetData };
}