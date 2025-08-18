import { Portfolio, Asset, Allocation } from '../entities/Portfolio';

export interface IPortfolioRepository {
  getPortfolio(portfolioId: string): Promise<Portfolio>;
  getUserPortfolios(userId: string): Promise<Portfolio[]>;
  createPortfolio(portfolio: Omit<Portfolio, 'id' | 'createdAt' | 'updatedAt'>): Promise<Portfolio>;
  updatePortfolio(portfolioId: string, updates: Partial<Portfolio>): Promise<Portfolio>;
  deletePortfolio(portfolioId: string): Promise<void>;
  
  getAssets(): Promise<Asset[]>;
  getAsset(assetId: string): Promise<Asset>;
  searchAssets(query: string): Promise<Asset[]>;
  
  updateAllocations(portfolioId: string, allocations: Allocation[]): Promise<Portfolio>;
  rebalancePortfolio(portfolioId: string): Promise<Portfolio>;
}