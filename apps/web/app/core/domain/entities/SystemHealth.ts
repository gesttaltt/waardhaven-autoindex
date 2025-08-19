// Domain Entity - Pure business logic, no dependencies
export interface SystemHealth {
  overall: HealthStatus;
  database: DatabaseHealth;
  cache: CacheHealth;
  dataFreshness: DataFreshness;
  timestamp: Date;
}

export enum HealthStatus {
  HEALTHY = 'healthy',
  WARNING = 'warning',
  ERROR = 'error',
  UNKNOWN = 'unknown'
}

export interface DatabaseHealth {
  status: HealthStatus;
  recordCount: number;
  simulationReady: boolean;
  message?: string;
}

export interface CacheHealth {
  status: HealthStatus;
  hitRate?: number;
  totalEntries: number;
  memoryUsage?: string;
}

export interface DataFreshness {
  daysOld: number;
  needsUpdate: boolean;
  lastUpdate?: Date;
}

// Business rules for health assessment
export class SystemHealthAssessment {
  static calculateOverallHealth(
    database: DatabaseHealth,
    cache: CacheHealth,
    dataFreshness: DataFreshness
  ): HealthStatus {
    // Critical errors
    if (!database.simulationReady || 
        cache.status === HealthStatus.ERROR || 
        dataFreshness.daysOld > 7) {
      return HealthStatus.ERROR;
    }
    
    // Warnings
    if (dataFreshness.needsUpdate || 
        (cache.hitRate && cache.hitRate < 0.5) ||
        dataFreshness.daysOld > 2) {
      return HealthStatus.WARNING;
    }
    
    return HealthStatus.HEALTHY;
  }

  static getHealthMessage(status: HealthStatus): string {
    switch (status) {
      case HealthStatus.HEALTHY:
        return 'All systems operational';
      case HealthStatus.WARNING:
        return 'Minor issues detected';
      case HealthStatus.ERROR:
        return 'Critical issues detected';
      default:
        return 'Status unknown';
    }
  }
}