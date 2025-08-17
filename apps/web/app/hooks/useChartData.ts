import { useMemo } from 'react';
import { SeriesPoint } from '../types/portfolio';
import { ChartDataPoint, TimeRange } from '../types/chart';
import { CHART_CONFIG } from '../constants/config';

export interface UseChartDataProps {
  indexSeries: SeriesPoint[];
  spSeries: SeriesPoint[];
  timeRange: TimeRange;
  showComparison: boolean;
  showMovingAverage: boolean;
  showVolatilityBands: boolean;
  individualAssets?: { [symbol: string]: SeriesPoint[] };
}

export interface UseChartDataReturn {
  filteredIndexSeries: SeriesPoint[];
  filteredSpSeries: SeriesPoint[];
  alignedChartData: ChartDataPoint[];
}

export function useChartData({
  indexSeries,
  spSeries,
  timeRange,
  showComparison,
  showMovingAverage,
  showVolatilityBands,
  individualAssets = {},
}: UseChartDataProps): UseChartDataReturn {
  // Filter data based on time range
  const filterDataByRange = (data: SeriesPoint[]): SeriesPoint[] => {
    if (timeRange === 'all' || data.length === 0) return data;
    
    const now = new Date();
    const cutoffDate = new Date();
    
    switch (timeRange) {
      case '1y':
        cutoffDate.setFullYear(now.getFullYear() - 1);
        break;
      case '6m':
        cutoffDate.setMonth(now.getMonth() - 6);
        break;
      case '3m':
        cutoffDate.setMonth(now.getMonth() - 3);
        break;
      case '1m':
        cutoffDate.setMonth(now.getMonth() - 1);
        break;
      default:
        return data;
    }
    
    return data.filter(point => new Date(point.date) >= cutoffDate);
  };

  // Calculate moving average
  const calculateMovingAverage = (data: SeriesPoint[], period: number = CHART_CONFIG.MOVING_AVERAGE_PERIOD): (number | null)[] => {
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

  // Calculate volatility bands
  const calculateVolatilityBands = (
    data: SeriesPoint[],
    period: number = CHART_CONFIG.VOLATILITY_BAND_PERIOD,
    multiplier: number = CHART_CONFIG.VOLATILITY_BAND_MULTIPLIER
  ): { upper: number | null; lower: number | null }[] => {
    const ma = calculateMovingAverage(data, period);
    
    return data.map((point, index) => {
      if (index < period - 1) return { upper: null, lower: null };
      
      const avg = ma[index];
      if (!avg) return { upper: null, lower: null };
      
      const periodData = data.slice(index - period + 1, index + 1);
      const variance = periodData.reduce((sum, p) => 
        sum + Math.pow(p.value - avg, 2), 0) / period;
      const stdDev = Math.sqrt(variance);
      
      return {
        upper: avg + (stdDev * multiplier),
        lower: avg - (stdDev * multiplier),
      };
    });
  };

  // Memoize filtered data
  const filteredIndexSeries = useMemo(
    () => filterDataByRange(indexSeries),
    [indexSeries, timeRange]
  );

  const filteredSpSeries = useMemo(
    () => filterDataByRange(spSeries),
    [spSeries, timeRange]
  );

  // Create aligned chart data
  const alignedChartData = useMemo(() => {
    if (!filteredIndexSeries || filteredIndexSeries.length === 0) return [];
    
    // Create a map of SP500 data by date for efficient lookup
    const spDataMap = new Map<string, number>();
    if (filteredSpSeries && filteredSpSeries.length > 0) {
      filteredSpSeries.forEach(point => {
        spDataMap.set(point.date, point.value);
      });
    }
    
    // Create maps for individual asset data by date
    const assetDataMaps = new Map<string, Map<string, number>>();
    Object.entries(individualAssets).forEach(([symbol, data]) => {
      if (data) {
        const filteredAssetData = filterDataByRange(data);
        const assetMap = new Map<string, number>();
        filteredAssetData.forEach(point => {
          assetMap.set(point.date, point.value);
        });
        assetDataMaps.set(symbol, assetMap);
      }
    });
    
    // Calculate technical indicators
    const movingAverage = showMovingAverage 
      ? calculateMovingAverage(filteredIndexSeries)
      : [];
    const volatilityBands = showVolatilityBands 
      ? calculateVolatilityBands(filteredIndexSeries)
      : [];
    
    // Map index data and align all data by date
    return filteredIndexSeries.map((point, index) => {
      const dataPoint: ChartDataPoint = {
        date: point.date,
        value: point.value,
        sp: showComparison ? (spDataMap.get(point.date) || null) : undefined,
        ma: showMovingAverage && movingAverage[index] !== null 
          ? movingAverage[index] 
          : undefined,
        upperBand: showVolatilityBands && volatilityBands[index]?.upper !== null 
          ? volatilityBands[index]?.upper 
          : undefined,
        lowerBand: showVolatilityBands && volatilityBands[index]?.lower !== null 
          ? volatilityBands[index]?.lower 
          : undefined,
      };
      
      // Add individual asset data
      assetDataMaps.forEach((assetMap, symbol) => {
        dataPoint[symbol] = assetMap.get(point.date) || null;
      });
      
      return dataPoint;
    });
  }, [
    filteredIndexSeries,
    filteredSpSeries,
    showComparison,
    showMovingAverage,
    showVolatilityBands,
    individualAssets,
  ]);

  return {
    filteredIndexSeries,
    filteredSpSeries,
    alignedChartData,
  };
}