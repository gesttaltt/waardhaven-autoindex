// Strategy API Service

import { ApiService } from './base';

export interface StrategyConfig {
  momentum_weight: number;
  market_cap_weight: number;
  risk_parity_weight: number;
  min_price_threshold: number;
  max_daily_return: number;
  min_daily_return: number;
  max_forward_fill_days: number;
  outlier_std_threshold: number;
  rebalance_frequency: 'daily' | 'weekly' | 'monthly';
  daily_drop_threshold: number;
  ai_adjusted?: boolean;
  ai_adjustment_reason?: string;
  ai_confidence_score?: number;
  last_rebalance?: string;
  updated_at?: string;
}

export interface RiskMetric {
  date: string;
  total_return: number;
  annualized_return?: number;
  sharpe_ratio: number;
  sortino_ratio: number;
  max_drawdown: number;
  current_drawdown: number;
  volatility?: number;
  var_95?: number;
  var_99?: number;
  beta_sp500?: number;
  correlation_sp500?: number;
}

export interface RiskMetricsResponse {
  metrics: RiskMetric[];
  message?: string;
}

export interface AIAdjustmentRequest {
  adjustments: Partial<StrategyConfig>;
  reason: string;
  confidence: number;
}

export interface RebalanceResponse {
  status: 'success' | 'skipped' | 'error';
  message: string;
  rebalanced?: boolean;
  next_rebalance?: string;
  allocations?: Array<{
    symbol: string;
    old_weight: number;
    new_weight: number;
  }>;
}

export class StrategyService extends ApiService {
  async getConfig(): Promise<StrategyConfig> {
    return this.get<StrategyConfig>('/api/v1/strategy/config');
  }

  async updateConfig(
    config: Partial<StrategyConfig>, 
    recompute: boolean = true
  ): Promise<StrategyConfig> {
    const params = new URLSearchParams();
    params.append('recompute', String(recompute));
    
    return this.put<StrategyConfig>(`/api/v1/strategy/config?${params.toString()}`, config);
  }

  async aiAdjust(request: AIAdjustmentRequest): Promise<StrategyConfig> {
    return this.post<StrategyConfig>('/api/v1/strategy/config/ai-adjust', request);
  }

  async getRiskMetrics(limit: number = 30): Promise<RiskMetricsResponse> {
    const params = new URLSearchParams();
    params.append('limit', String(limit));
    
    return this.get<RiskMetricsResponse>(`/api/v1/strategy/risk-metrics?${params.toString()}`);
  }

  async triggerRebalance(force: boolean = false): Promise<RebalanceResponse> {
    const params = new URLSearchParams();
    params.append('force', String(force));
    
    return this.post<RebalanceResponse>(`/api/v1/strategy/rebalance?${params.toString()}`);
  }
}

export const strategyService = new StrategyService();