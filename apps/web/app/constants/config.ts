// Application configuration constants

export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const DEFAULT_CURRENCY = 'USD';

export const DEFAULT_SIMULATION_AMOUNT = 10000;

export const DEFAULT_START_DATE = '2019-01-01';

export const REFRESH_INTERVAL = 60000; // 1 minute in milliseconds

export const CHART_CONFIG = {
  DEFAULT_TIME_RANGE: 'all' as const,
  MOVING_AVERAGE_PERIOD: 50,
  VOLATILITY_BAND_PERIOD: 20,
  VOLATILITY_BAND_MULTIPLIER: 2,
  MIN_PRICE_THRESHOLD: 1.0,
  MAX_FORWARD_FILL_DAYS: 2,
  OUTLIER_STD_THRESHOLD: 3.0,
  MAX_DAILY_RETURN: 0.5,
  MIN_DAILY_RETURN: -0.5,
};

export const PORTFOLIO_CONFIG = {
  MAX_ASSETS_DISPLAY: 6,
  TOP_HOLDINGS_COUNT: 5,
  RISK_FREE_RATE: 0.05, // 5% annual
};

export const TIME_RANGE_OPTIONS = [
  { key: '1m' as const, label: '1M' },
  { key: '3m' as const, label: '3M' },
  { key: '6m' as const, label: '6M' },
  { key: '1y' as const, label: '1Y' },
  { key: 'all' as const, label: 'All' },
];

export const PRIORITY_ASSETS = [
  'AAPL',
  'MSFT',
  'GOOGL',
  'AMZN',
  'META',
  'SPY',
  'QQQ',
  'GLD',
] as const;