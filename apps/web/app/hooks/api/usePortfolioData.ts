import { useState, useEffect } from 'react';
import { portfolioService } from '../../services/api/portfolio';
import { useApiCall } from './useApiCall';

export interface PortfolioData {
  indexSeries: any[];
  allocations: any[];
  currentValue: number;
  lastUpdated: string;
}

export function usePortfolioData() {
  const { data: history, loading: historyLoading, error: historyError, refetch: refetchHistory } = 
    useApiCall(() => portfolioService.getIndexHistory());
    
  const { data: current, loading: currentLoading, error: currentError, refetch: refetchCurrent } = 
    useApiCall(() => portfolioService.getCurrentAllocations());

  const loading = historyLoading || currentLoading;
  const error = historyError || currentError;

  const refetch = async () => {
    await Promise.all([refetchHistory(), refetchCurrent()]);
  };

  return {
    indexSeries: history?.series || [],
    allocations: current?.allocations || [],
    loading,
    error,
    refetch,
  };
}

export function useAssetHistory(symbol: string, enabled: boolean = true) {
  return useApiCall(
    () => portfolioService.getAssetHistory(symbol),
    { immediate: enabled }
  );
}