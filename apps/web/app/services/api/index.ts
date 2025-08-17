// Unified API service exports
// This file consolidates all API services for easier imports

export { ApiService } from './base';
export { portfolioService } from './portfolio';
export { backgroundTaskService } from './background';
export { diagnosticsService } from './diagnostics';
export { benchmarkService } from './benchmark';
export { marketService } from './market';
export { strategyService } from './strategy';
export { manualService } from './manual';

// Re-export types
export type {
  RefreshRequest,
  ComputeRequest,
  ReportRequest,
  CleanupRequest,
  TaskResponse,
  TaskStatus,
  ActiveTasks
} from './background';

export type {
  DatabaseStatus,
  RefreshStatus,
  CacheStatus,
  CacheInvalidateResponse,
  TestRefreshResult,
  RecalculateResult
} from './diagnostics';

export type {
  SeriesPoint,
  BenchmarkResponse,
  PerformanceComparison
} from './benchmark';

export type {
  StrategyConfig,
  RiskMetric,
  RiskMetricsResponse,
  AIAdjustmentRequest,
  RebalanceResponse
} from './strategy';

export type {
  RefreshResponse,
  SmartRefreshOptions
} from './manual';