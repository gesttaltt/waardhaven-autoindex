// Strategy API service

import { ApiService } from './base';

export interface StrategyConfig {
  min_market_cap?: number;
  max_assets?: number;
  rebalance_frequency?: string;
  volatility_threshold?: number;
  correlation_threshold?: number;
  use_momentum?: boolean;
  use_value?: boolean;
  risk_tolerance?: string;
  exclude_sectors?: string[];
  include_commodities?: boolean;
  include_bonds?: boolean;
}

export interface RiskMetric {
  volatility: number;
  sharpe_ratio: number;
  max_drawdown: number;
  beta: number;
  alpha: number;
  correlation_with_market: number;
}

interface RiskMetrics {
  volatility: number;
  sharpe_ratio: number;
  max_drawdown: number;
  beta: number;
  alpha: number;
  correlation_with_market: number;
}

class StrategyService extends ApiService {
  async getConfig(): Promise<StrategyConfig> {
    return this.get<StrategyConfig>('/api/v1/strategy/config');
  }

  async updateConfig(config: StrategyConfig): Promise<StrategyConfig> {
    return this.post<StrategyConfig>('/api/v1/strategy/config', config);
  }

  async rebalance(): Promise<any> {
    return this.post('/api/v1/strategy/rebalance');
  }

  async getRiskMetrics(): Promise<RiskMetrics> {
    return this.get<RiskMetrics>('/api/v1/strategy/risk-metrics');
  }

  async aiAdjust(marketCondition: string): Promise<StrategyConfig> {
    return this.post<StrategyConfig>('/api/v1/strategy/config/ai-adjust', {
      market_condition: marketCondition
    });
  }
}

export const strategyService = new StrategyService();