// Background Task API Service

import { ApiService } from './base';

export interface RefreshRequest {
  mode: 'smart' | 'full' | 'minimal';
}

export interface ComputeRequest {
  momentum_weight?: number;
  market_cap_weight?: number;
  risk_parity_weight?: number;
}

export interface ReportRequest {
  report_type: 'performance' | 'allocation' | 'risk';
  period_days: number;
}

export interface CleanupRequest {
  days_to_keep: number;
}

export interface TaskResponse {
  task_id: string;
  status: string;
  message: string;
}

export interface TaskStatus {
  task_id: string;
  status: 'PENDING' | 'STARTED' | 'SUCCESS' | 'FAILURE' | 'RETRY' | 'REVOKED';
  result?: any;
  error?: string;
  traceback?: string;
  current?: number;
  total?: number;
}

export interface ActiveTasks {
  active: Record<string, any[]>;
  scheduled: Record<string, any[]>;
  reserved: Record<string, any[]>;
  stats: {
    total_active: number;
    total_scheduled: number;
    total_reserved: number;
  };
}

export class BackgroundTaskService extends ApiService {
  async triggerRefresh(request: RefreshRequest): Promise<TaskResponse> {
    return this.post<TaskResponse>('/api/v1/background/refresh', request);
  }

  async triggerCompute(request: ComputeRequest): Promise<TaskResponse> {
    return this.post<TaskResponse>('/api/v1/background/compute', request);
  }

  async generateReport(request: ReportRequest): Promise<TaskResponse> {
    return this.post<TaskResponse>('/api/v1/background/report', request);
  }

  async cleanupData(request: CleanupRequest): Promise<TaskResponse> {
    return this.post<TaskResponse>('/api/v1/background/cleanup', request);
  }

  async getTaskStatus(taskId: string): Promise<TaskStatus> {
    return this.get<TaskStatus>(`/api/v1/background/status/${taskId}`);
  }

  async getActiveTasks(): Promise<ActiveTasks> {
    return this.get<ActiveTasks>('/api/v1/background/active');
  }

  // Polling helper for task completion
  async pollTaskStatus(
    taskId: string, 
    onProgress?: (status: TaskStatus) => void,
    intervalMs: number = 1000,
    maxAttempts: number = 300
  ): Promise<TaskStatus> {
    let attempts = 0;
    
    return new Promise((resolve, reject) => {
      const poll = async () => {
        try {
          const status = await this.getTaskStatus(taskId);
          
          if (onProgress) {
            onProgress(status);
          }
          
          if (status.status === 'SUCCESS' || status.status === 'FAILURE') {
            resolve(status);
            return;
          }
          
          attempts++;
          if (attempts >= maxAttempts) {
            reject(new Error('Task polling timeout'));
            return;
          }
          
          setTimeout(poll, intervalMs);
        } catch (error) {
          reject(error);
        }
      };
      
      poll();
    });
  }
}

export const backgroundTaskService = new BackgroundTaskService();