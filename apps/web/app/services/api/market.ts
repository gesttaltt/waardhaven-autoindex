// Market data API service

import { ApiService } from './base';
import { SeriesPoint } from '../../types/portfolio';

interface BenchmarkResponse {
  series: SeriesPoint[];
}

class MarketService extends ApiService {
  async getSP500History(): Promise<BenchmarkResponse> {
    return this.get<BenchmarkResponse>('/api/v1/benchmark/sp500');
  }

  async refreshMarketData(): Promise<any> {
    return this.post('/api/v1/manual/refresh');
  }

  async getDiagnostics(): Promise<any> {
    return this.get('/api/v1/diagnostics/status');
  }
}

export const marketService = new MarketService();