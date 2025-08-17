// Portfolio related types and interfaces

export interface SeriesPoint {
  date: string;
  value: number;
}

export interface AllocationItem {
  symbol: string;
  weight: number;
  name?: string;
  sector?: string;
}

export interface PortfolioAllocation extends AllocationItem {
  id?: number;
  assetId?: number;
}

export interface IndexValue {
  id?: number;
  date: string;
  value: number;
}

export interface SimulationRequest {
  amount: number;
  startDate: string;
  currency: string;
}

export interface SimulationResult {
  amount_final: number;
  roi_pct: number;
  currency: string;
  start_date?: string;
  end_date?: string;
  start_value?: number;
  end_value?: number;
  series?: SeriesPoint[];
}

export interface PerformanceMetrics {
  indexReturn: number;
  spReturn: number;
  outperformance: number;
  indexValue: number;
  spValue: number;
}

export interface RiskMetric {
  id?: number;
  date?: string;
  total_return: number;
  annualized_return: number;
  volatility: number;
  sharpe_ratio: number;
  max_drawdown: number;
  current_drawdown: number;
  win_rate: number;
  avg_win: number;
  avg_loss: number;
  best_day: number;
  worst_day: number;
  var_95: number;
  cvar_95: number;
  beta?: number;
  alpha?: number;
  correlation?: number;
}

export interface Asset {
  id: number;
  symbol: string;
  name?: string;
  sector?: string;
}

export interface Price {
  id?: number;
  assetId: number;
  date: string;
  close: number;
}