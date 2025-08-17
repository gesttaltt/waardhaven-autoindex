import { useMemo } from 'react';
import { calculatePortfolioMetrics } from '../lib/calculations/portfolio';

interface SeriesPoint {
  date: string;
  value: number;
}

export function usePortfolioMetrics(
  series: SeriesPoint[],
  timeRange: 'all' | '1M' | '3M' | '6M' | '1Y' | 'YTD' = 'all'
) {
  const filteredSeries = useMemo(() => {
    if (!series || series.length === 0) return [];
    
    if (timeRange === 'all') return series;
    
    const now = new Date();
    let startDate: Date;
    
    switch (timeRange) {
      case '1M':
        startDate = new Date(now);
        startDate.setMonth(now.getMonth() - 1);
        break;
      case '3M':
        startDate = new Date(now);
        startDate.setMonth(now.getMonth() - 3);
        break;
      case '6M':
        startDate = new Date(now);
        startDate.setMonth(now.getMonth() - 6);
        break;
      case '1Y':
        startDate = new Date(now);
        startDate.setFullYear(now.getFullYear() - 1);
        break;
      case 'YTD':
        startDate = new Date(now.getFullYear(), 0, 1);
        break;
      default:
        return series;
    }
    
    return series.filter(point => new Date(point.date) >= startDate);
  }, [series, timeRange]);
  
  const metrics = useMemo(() => {
    if (filteredSeries.length < 2) {
      return {
        totalReturn: 0,
        annualizedReturn: 0,
        volatility: 0,
        sharpeRatio: 0,
        maxDrawdown: 0,
        currentDrawdown: 0,
      };
    }
    
    const values = filteredSeries.map(p => p.value);
    const firstDate = new Date(filteredSeries[0].date);
    const lastDate = new Date(filteredSeries[filteredSeries.length - 1].date);
    const periodInDays = Math.floor((lastDate.getTime() - firstDate.getTime()) / (1000 * 60 * 60 * 24));
    
    return calculatePortfolioMetrics(values, periodInDays);
  }, [filteredSeries]);
  
  const currentValue = filteredSeries[filteredSeries.length - 1]?.value || 0;
  const initialValue = filteredSeries[0]?.value || 0;
  
  return {
    series: filteredSeries,
    metrics,
    currentValue,
    initialValue,
    period: {
      start: filteredSeries[0]?.date,
      end: filteredSeries[filteredSeries.length - 1]?.date,
      days: filteredSeries.length,
    },
  };
}