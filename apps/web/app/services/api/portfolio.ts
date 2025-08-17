// Portfolio API service

import { ApiService } from './base';
import {
  SeriesPoint,
  AllocationItem,
  SimulationRequest,
  SimulationResult,
  RiskMetric,
} from '../../types/portfolio';
import { CurrencyMap } from '../../types/api';

interface IndexHistoryResponse {
  series: SeriesPoint[];
}

interface IndexCurrentResponse {
  date: string;
  allocations: AllocationItem[];
}

interface SimulationResponse extends SimulationResult {
  start_date: string;
  end_date: string;
  start_value: number;
  end_value: number;
  amount_initial: number;
  series: SeriesPoint[];
}

interface RiskMetricsResponse {
  metrics: RiskMetric[];
}

class PortfolioService extends ApiService {
  async getIndexHistory(): Promise<IndexHistoryResponse> {
    return this.get<IndexHistoryResponse>('/api/v1/index/history');
  }

  async getCurrentAllocations(): Promise<IndexCurrentResponse> {
    return this.get<IndexCurrentResponse>('/api/v1/index/current');
  }

  async getAssetHistory(symbol: string): Promise<IndexHistoryResponse> {
    return this.get<IndexHistoryResponse>(`/api/v1/index/assets/${symbol}/history`);
  }

  async runSimulation(request: SimulationRequest): Promise<SimulationResponse> {
    const payload = {
      amount: request.amount,
      start_date: request.startDate,
      currency: request.currency,
    };
    return this.post<SimulationResponse>('/api/v1/index/simulate', payload);
  }

  async getCurrencies(): Promise<CurrencyMap> {
    return this.get<CurrencyMap>('/api/v1/index/currencies');
  }

  async getRiskMetrics(): Promise<RiskMetricsResponse> {
    return this.get<RiskMetricsResponse>('/api/v1/strategy/risk-metrics');
  }

  async refreshPortfolio(): Promise<any> {
    return this.post('/api/v1/tasks/refresh');
  }
}

export const portfolioService = new PortfolioService();