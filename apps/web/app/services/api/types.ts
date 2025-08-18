export interface ChartDataPoint {
  date: string;
  price: number;
  ma20?: number | null;
  ma50?: number | null;
  ema20?: number | null;
  bandUpper?: number | null;
  bandMiddle?: number | null;
  bandLower?: number | null;
  rsi?: number | null;
  macd?: number | null;
  macdSignal?: number | null;
  macdHistogram?: number | null;
}