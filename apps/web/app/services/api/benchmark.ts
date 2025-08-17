// Benchmark API Service

import { ApiService } from './base';

export interface SeriesPoint {
  date: string;
  value: number;
}

export interface BenchmarkResponse {
  series: SeriesPoint[];
}

export interface PerformanceComparison {
  autoindex: {
    start_value: number;
    end_value: number;
    total_return: number;
    annualized_return: number;
    volatility: number;
    sharpe_ratio: number;
  };
  sp500: {
    start_value: number;
    end_value: number;
    total_return: number;
    annualized_return: number;
    volatility: number;
    sharpe_ratio: number;
  };
  outperformance: {
    total: number;
    annualized: number;
    information_ratio: number;
  };
}

export class BenchmarkService extends ApiService {
  async getSP500Data(): Promise<BenchmarkResponse> {
    return this.get<BenchmarkResponse>('/api/v1/benchmark/sp500');
  }

  async comparePerformance(
    startDate?: string, 
    endDate?: string
  ): Promise<PerformanceComparison> {
    const params = new URLSearchParams();
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    
    const query = params.toString() ? `?${params.toString()}` : '';
    return this.get<PerformanceComparison>(`/api/v1/benchmark/compare${query}`);
  }
}

export const benchmarkService = new BenchmarkService();