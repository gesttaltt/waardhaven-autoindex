// Chart related types and interfaces

export interface ChartDataPoint {
  date: string;
  value: number;
  sp?: number | null;
  ma?: number;
  upperBand?: number;
  lowerBand?: number;
  [key: string]: string | number | null | undefined; // For dynamic asset data
}

export interface ChartConfig {
  showComparison: boolean;
  showMovingAverage: boolean;
  showVolatilityBands: boolean;
  showVolume: boolean;
  timeRange: TimeRange;
}

export type TimeRange = '1m' | '3m' | '6m' | '1y' | 'all';

export interface ChartColors {
  primary: string;
  secondary: string;
  success: string;
  warning: string;
  danger: string;
  info: string;
  [key: string]: string;
}

export interface TechnicalIndicators {
  movingAverage: (number | null)[];
  volatilityBands: { upper: number | null; lower: number | null }[];
}

export interface ChartTooltipProps {
  active?: boolean;
  payload?: any[];
  label?: string;
}

export interface ChartTimeRangeOption {
  key: TimeRange;
  label: string;
}