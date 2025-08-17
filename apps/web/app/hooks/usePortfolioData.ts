import { useState, useEffect } from 'react';
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

export function usePortfolioData(): UsePortfolioDataReturn {
  const [indexSeries, setIndexSeries] = useState<SeriesPoint[]>([]);
  const [spSeries, setSpSeries] = useState<SeriesPoint[]>([]);
  const [allocations, setAllocations] = useState<AllocationItem[]>([]);
  const [riskMetrics, setRiskMetrics] = useState<RiskMetric | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);

      const [indexData, spData, allocData, metricsData] = await Promise.allSettled([
        portfolioService.getIndexHistory(),
        marketService.getSP500History(),
        portfolioService.getCurrentAllocations(),
        portfolioService.getRiskMetrics(),
      ]);

      if (indexData.status === 'fulfilled') {
        setIndexSeries(indexData.value.series);
      } else {
        console.error('Failed to fetch index history:', indexData.reason);
      }

      if (spData.status === 'fulfilled') {
        setSpSeries(spData.value.series);
      } else {
        console.warn('S&P 500 data not available');
        setSpSeries([]);
      }

      if (allocData.status === 'fulfilled') {
        setAllocations(allocData.value.allocations);
      } else {
        console.error('Failed to fetch allocations:', allocData.reason);
      }

      if (metricsData.status === 'fulfilled' && metricsData.value.metrics?.length > 0) {
        setRiskMetrics(metricsData.value.metrics[0]);
      }
    } catch (err) {
      console.error('Failed to fetch portfolio data:', err);
      setError('Failed to load portfolio data. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

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