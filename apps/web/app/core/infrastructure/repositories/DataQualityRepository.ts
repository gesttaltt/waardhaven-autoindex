import { 
  IDataQualityRepository, 
  RawQualityData, 
  RefreshOptions 
} from '../../domain/repositories/IDataQualityRepository';
import { ApiClient } from '../api/ApiClient';
import { diagnosticsService } from '../../../services/api/diagnostics';
import { manualService } from '../../../services/api/manual';

export class DataQualityRepository implements IDataQualityRepository {
  private apiClient: ApiClient;

  constructor() {
    this.apiClient = ApiClient.getInstance();
  }

  async getRawQualityData(): Promise<RawQualityData> {
    try {
      const [refreshStatus, dbStatus] = await Promise.all([
        diagnosticsService.getRefreshStatus(),
        diagnosticsService.getDatabaseStatus()
      ]);

      const daysOld = refreshStatus.prices.days_old || 0;
      const totalAssets = refreshStatus.assets.count || 0;
      
      // Mock some data that would come from a real API
      // In production, these would come from actual validation endpoints
      const errorRate = Math.random() * 0.05; // 0-5% error rate
      const validationsPassed = Math.floor(20 * (1 - errorRate));
      const sectors = Math.floor(Math.random() * 8) + 3; // 3-10 sectors
      const regions = Math.floor(Math.random() * 5) + 2; // 2-6 regions

      return {
        daysOld,
        lastUpdate: refreshStatus.prices.latest_date || 'Never',
        totalAssets,
        errorRate,
        validationsPassed,
        totalValidations: 20,
        hasBenchmark: refreshStatus.assets.has_benchmark,
        sectors,
        regions
      };
    } catch (error) {
      // Return default values on error
      return {
        daysOld: 999,
        lastUpdate: 'Unknown',
        totalAssets: 0,
        errorRate: 1,
        validationsPassed: 0,
        totalValidations: 20,
        hasBenchmark: false,
        sectors: 0,
        regions: 0
      };
    }
  }

  async triggerDataRefresh(options: RefreshOptions): Promise<void> {
    await manualService.smartRefresh({
      force: options.force,
      mode: options.mode === 'full' ? 'full' : 
            options.mode === 'minimal' ? 'minimal' : 'auto'
    });
  }
}