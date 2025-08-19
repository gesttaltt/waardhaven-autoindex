// Repository interface for data quality
export interface RawQualityData {
  daysOld: number;
  lastUpdate: string;
  totalAssets: number;
  errorRate: number;
  validationsPassed: number;
  totalValidations: number;
  hasBenchmark: boolean;
  sectors: number;
  regions: number;
}

export interface IDataQualityRepository {
  getRawQualityData(): Promise<RawQualityData>;
  triggerDataRefresh(options: RefreshOptions): Promise<void>;
}

export interface RefreshOptions {
  force?: boolean;
  mode?: 'full' | 'partial' | 'minimal';
}