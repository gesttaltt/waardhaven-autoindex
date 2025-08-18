export interface Asset {
  id: string;
  symbol: string;
  name: string;
  type: AssetType;
  sector?: string;
  marketCap?: number;
  currentPrice: number;
  priceChange24h?: number;
  priceChangePercentage24h?: number;
}

export enum AssetType {
  STOCK = 'stock',
  ETF = 'etf',
  COMMODITY = 'commodity',
  CRYPTO = 'crypto',
  BOND = 'bond'
}

export interface Allocation {
  assetId: string;
  symbol: string;
  weight: number;
  value: number;
  shares?: number;
}

export interface Portfolio {
  id: string;
  userId: string;
  name: string;
  totalValue: number;
  allocations: Allocation[];
  performance: PortfolioPerformance;
  createdAt: Date;
  updatedAt: Date;
}

export interface PortfolioPerformance {
  totalReturn: number;
  totalReturnPercentage: number;
  dayReturn: number;
  dayReturnPercentage: number;
  weekReturn: number;
  monthReturn: number;
  yearReturn: number;
  sharpeRatio: number;
  volatility: number;
  maxDrawdown: number;
}