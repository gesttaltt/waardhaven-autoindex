import { SystemHealth } from '../entities/SystemHealth';

// Repository interface - Domain layer defines what it needs
// Implementation details are in the infrastructure layer
export interface ISystemHealthRepository {
  getSystemHealth(): Promise<SystemHealth>;
  checkDatabaseHealth(): Promise<SystemHealth['database']>;
  checkCacheHealth(): Promise<SystemHealth['cache']>;
  checkDataFreshness(): Promise<SystemHealth['dataFreshness']>;
}