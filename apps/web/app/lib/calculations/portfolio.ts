/**
 * Portfolio calculation utilities
 */

export interface PerformanceMetrics {
  totalReturn: number;
  annualizedReturn: number;
  volatility: number;
  sharpeRatio: number;
  maxDrawdown: number;
  currentDrawdown: number;
}

export function calculateReturns(prices: number[]): number[] {
  if (prices.length < 2) return [];
  
  const returns: number[] = [];
  for (let i = 1; i < prices.length; i++) {
    const dailyReturn = (prices[i] - prices[i - 1]) / prices[i - 1];
    returns.push(dailyReturn);
  }
  
  return returns;
}

export function calculateTotalReturn(startValue: number, endValue: number): number {
  return ((endValue - startValue) / startValue) * 100;
}

export function calculateAnnualizedReturn(
  totalReturn: number,
  periodInDays: number
): number {
  const yearsElapsed = periodInDays / 365;
  return (Math.pow(1 + totalReturn / 100, 1 / yearsElapsed) - 1) * 100;
}

export function calculateVolatility(returns: number[]): number {
  if (returns.length === 0) return 0;
  
  const mean = returns.reduce((sum, r) => sum + r, 0) / returns.length;
  const variance = returns.reduce((sum, r) => sum + Math.pow(r - mean, 2), 0) / returns.length;
  const dailyVolatility = Math.sqrt(variance);
  
  // Annualize the volatility
  return dailyVolatility * Math.sqrt(252) * 100;
}

export function calculateSharpeRatio(
  annualizedReturn: number,
  volatility: number,
  riskFreeRate: number = 2
): number {
  if (volatility === 0) return 0;
  return (annualizedReturn - riskFreeRate) / volatility;
}

export function calculateMaxDrawdown(values: number[]): {
  maxDrawdown: number;
  currentDrawdown: number;
} {
  if (values.length === 0) {
    return { maxDrawdown: 0, currentDrawdown: 0 };
  }
  
  let maxDrawdown = 0;
  let peak = values[0];
  let currentDrawdown = 0;
  
  for (const value of values) {
    if (value > peak) {
      peak = value;
    }
    
    const drawdown = (peak - value) / peak;
    maxDrawdown = Math.max(maxDrawdown, drawdown);
    currentDrawdown = drawdown;
  }
  
  return {
    maxDrawdown: maxDrawdown * 100,
    currentDrawdown: currentDrawdown * 100,
  };
}

export function calculatePortfolioMetrics(
  values: number[],
  periodInDays: number
): PerformanceMetrics {
  if (values.length < 2) {
    return {
      totalReturn: 0,
      annualizedReturn: 0,
      volatility: 0,
      sharpeRatio: 0,
      maxDrawdown: 0,
      currentDrawdown: 0,
    };
  }
  
  const returns = calculateReturns(values);
  const totalReturn = calculateTotalReturn(values[0], values[values.length - 1]);
  const annualizedReturn = calculateAnnualizedReturn(totalReturn, periodInDays);
  const volatility = calculateVolatility(returns);
  const sharpeRatio = calculateSharpeRatio(annualizedReturn, volatility);
  const { maxDrawdown, currentDrawdown } = calculateMaxDrawdown(values);
  
  return {
    totalReturn,
    annualizedReturn,
    volatility,
    sharpeRatio,
    maxDrawdown,
    currentDrawdown,
  };
}