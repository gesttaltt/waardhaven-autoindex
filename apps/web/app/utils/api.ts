import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests if it exists
api.interceptors.request.use(
  (config) => {
    const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null;
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Handle auth errors globally
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      if (typeof window !== 'undefined') {
        localStorage.removeItem('token');
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

// API client methods for market data management
export const marketDataApi = {
  // Get database status and diagnostics
  getDatabaseStatus: () => api.get('/api/v1/diagnostics/database-status'),
  
  // Trigger standard refresh
  triggerRefresh: () => api.post('/api/v1/manual/trigger-refresh'),
  
  // Trigger smart refresh with rate limiting protection
  triggerSmartRefresh: (mode: 'auto' | 'full' | 'minimal' | 'cached' = 'auto') => 
    api.post(`/api/v1/manual/smart-refresh?mode=${mode}`),
  
  // Trigger minimal refresh (for testing/debugging)
  triggerMinimalRefresh: () => api.post('/api/v1/manual/minimal-refresh'),
  
  // Test refresh process
  testRefresh: () => api.post('/api/v1/diagnostics/test-refresh'),
  
  // Check refresh requirements and status
  getRefreshStatus: () => api.get('/api/v1/diagnostics/refresh-status'),
  
  // Recalculate AutoIndex with proper normalization
  recalculateIndex: () => api.post('/api/v1/diagnostics/recalculate-index'),
};

// API client methods for strategy management
export const strategyApi = {
  // Get current strategy configuration
  getConfig: () => api.get<StrategyConfig>('/api/v1/strategy/config'),
  
  // Update strategy configuration
  updateConfig: (config: Partial<StrategyConfig>, recompute: boolean = true) => 
    api.put('/api/v1/strategy/config', config, { params: { recompute } }),
  
  // Apply AI-suggested adjustments
  aiAdjust: (adjustments: Partial<StrategyConfig>, reason: string, confidence: number) =>
    api.post('/api/v1/strategy/config/ai-adjust', { adjustments, reason, confidence }),
  
  // Get risk metrics
  getRiskMetrics: (limit: number = 30) => 
    api.get<RiskMetricsResponse>('/api/v1/strategy/risk-metrics', { params: { limit } }),
  
  // Trigger rebalancing
  triggerRebalance: (force: boolean = false) =>
    api.post('/api/v1/strategy/rebalance', null, { params: { force } }),
};

// Types for API responses
export interface DatabaseStatus {
  timestamp: string;
  tables: {
    [tableName: string]: {
      count: number;
      status: 'OK' | 'EMPTY' | 'ERROR';
      earliest_date?: string;
      latest_date?: string;
      error?: string;
    };
  };
  simulation_ready: boolean;
  message: string;
}

export interface SmartRefreshResponse {
  status: string;
  message: string;
  mode: string;
  features: string[];
  note: string;
}

export interface RefreshStatusResponse {
  assets: {
    count: number;
    symbols: string[];
    has_benchmark: boolean;
  };
  prices: {
    latest_date?: string;
    days_old?: number;
    needs_update: boolean;
  };
  recommendation: string;
}

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

export default api;