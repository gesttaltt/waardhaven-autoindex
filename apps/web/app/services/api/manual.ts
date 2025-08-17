// Manual Operations API Service

import { ApiService } from './base';

export interface RefreshResponse {
  status: 'success' | 'error' | 'rate_limited';
  message: string;
  mode?: string;
  features?: string[];
  note?: string;
  data?: {
    prices_updated?: number;
    assets_updated?: number;
    index_recalculated?: boolean;
  };
}

export interface SmartRefreshOptions {
  mode?: 'auto' | 'full' | 'minimal' | 'cached';
  force?: boolean;
}

export class ManualService extends ApiService {
  async triggerRefresh(): Promise<RefreshResponse> {
    return this.post<RefreshResponse>('/api/v1/manual/trigger-refresh');
  }

  async smartRefresh(options: SmartRefreshOptions = {}): Promise<RefreshResponse> {
    const params = new URLSearchParams();
    if (options.mode) params.append('mode', options.mode);
    if (options.force !== undefined) params.append('force', String(options.force));
    
    const query = params.toString() ? `?${params.toString()}` : '';
    return this.post<RefreshResponse>(`/api/v1/manual/smart-refresh${query}`);
  }

  async minimalRefresh(): Promise<RefreshResponse> {
    return this.post<RefreshResponse>('/api/v1/manual/minimal-refresh');
  }
}

export const manualService = new ManualService();