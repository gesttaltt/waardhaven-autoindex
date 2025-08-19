import { ISystemHealthRepository } from '../../domain/repositories/ISystemHealthRepository';
import { SystemHealth, HealthStatus } from '../../domain/entities/SystemHealth';
import { ApiClient } from '../api/ApiClient';
import { diagnosticsService } from '../../../services/api/diagnostics';

export class SystemHealthRepository implements ISystemHealthRepository {
  private apiClient: ApiClient;

  constructor() {
    this.apiClient = ApiClient.getInstance();
  }

  async getSystemHealth(): Promise<SystemHealth> {
    const [database, cache, dataFreshness] = await Promise.all([
      this.checkDatabaseHealth(),
      this.checkCacheHealth(),
      this.checkDataFreshness()
    ]);

    return {
      overall: HealthStatus.UNKNOWN, // Will be calculated by use case
      database,
      cache,
      dataFreshness,
      timestamp: new Date()
    };
  }

  async checkDatabaseHealth(): Promise<SystemHealth['database']> {
    try {
      const dbStatus = await diagnosticsService.getDatabaseStatus();
      
      const totalRecords = Object.values(dbStatus.tables)
        .reduce((sum, table) => sum + table.count, 0);

      return {
        status: dbStatus.simulation_ready ? HealthStatus.HEALTHY : HealthStatus.ERROR,
        recordCount: totalRecords,
        simulationReady: dbStatus.simulation_ready,
        message: dbStatus.message
      };
    } catch (error) {
      return {
        status: HealthStatus.ERROR,
        recordCount: 0,
        simulationReady: false,
        message: 'Failed to check database health'
      };
    }
  }

  async checkCacheHealth(): Promise<SystemHealth['cache']> {
    try {
      const cacheStatus = await diagnosticsService.getCacheStatus();
      
      const status = cacheStatus.status === 'connected' 
        ? HealthStatus.HEALTHY 
        : cacheStatus.status === 'disconnected' 
        ? HealthStatus.WARNING 
        : HealthStatus.ERROR;

      return {
        status,
        hitRate: cacheStatus.stats?.hit_rate,
        totalEntries: cacheStatus.stats?.total_entries || 0,
        memoryUsage: cacheStatus.stats?.memory_usage
      };
    } catch (error) {
      return {
        status: HealthStatus.ERROR,
        totalEntries: 0
      };
    }
  }

  async checkDataFreshness(): Promise<SystemHealth['dataFreshness']> {
    try {
      const refreshStatus = await diagnosticsService.getRefreshStatus();
      
      return {
        daysOld: refreshStatus.prices.days_old || 0,
        needsUpdate: refreshStatus.prices.needs_update,
        lastUpdate: refreshStatus.prices.latest_date 
          ? new Date(refreshStatus.prices.latest_date) 
          : undefined
      };
    } catch (error) {
      return {
        daysOld: 999,
        needsUpdate: true
      };
    }
  }
}