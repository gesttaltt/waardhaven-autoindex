import { SystemHealth, SystemHealthAssessment } from '../entities/SystemHealth';
import { ISystemHealthRepository } from '../repositories/ISystemHealthRepository';

export interface MonitorSystemHealthRequest {
  includeDetails?: boolean;
}

export interface MonitorSystemHealthResponse {
  health: SystemHealth;
  message: string;
  requiresAction: boolean;
}

export class MonitorSystemHealthUseCase {
  constructor(
    private readonly systemHealthRepository: ISystemHealthRepository
  ) {}

  async execute(request: MonitorSystemHealthRequest): Promise<MonitorSystemHealthResponse> {
    // Fetch system health data from repository
    const health = await this.systemHealthRepository.getSystemHealth();
    
    // Apply business rules
    const overallHealth = SystemHealthAssessment.calculateOverallHealth(
      health.database,
      health.cache,
      health.dataFreshness
    );
    
    // Update overall status
    health.overall = overallHealth;
    
    // Get appropriate message
    const message = SystemHealthAssessment.getHealthMessage(overallHealth);
    
    // Determine if action is required
    const requiresAction = overallHealth !== 'healthy';
    
    return {
      health,
      message,
      requiresAction
    };
  }
}