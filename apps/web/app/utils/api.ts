import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests if it exists
api.interceptors.request.use(
  (config) => {
    const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null;
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Handle auth errors globally
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      if (typeof window !== 'undefined') {
        localStorage.removeItem('token');
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

// API client methods for market data management
export const marketDataApi = {
  // Get database status and diagnostics
  getDatabaseStatus: () => api.get('/api/v1/diagnostics/database-status'),
  
  // Trigger standard refresh
  triggerRefresh: () => api.post('/api/v1/manual/trigger-refresh'),
  
  // Trigger smart refresh with rate limiting protection
  triggerSmartRefresh: (mode: 'auto' | 'full' | 'minimal' | 'cached' = 'auto') => 
    api.post(`/api/v1/manual/smart-refresh?mode=${mode}`),
  
  // Trigger minimal refresh (for testing/debugging)
  triggerMinimalRefresh: () => api.post('/api/v1/manual/minimal-refresh'),
  
  // Test refresh process
  testRefresh: () => api.post('/api/v1/diagnostics/test-refresh'),
  
  // Check refresh requirements and status
  getRefreshStatus: () => api.get('/api/v1/diagnostics/refresh-status'),
  
  // Recalculate AutoIndex with proper normalization
  recalculateIndex: () => api.post('/api/v1/diagnostics/recalculate-index'),
};

// Types for API responses
export interface DatabaseStatus {
  timestamp: string;
  tables: {
    [tableName: string]: {
      count: number;
      status: 'OK' | 'EMPTY' | 'ERROR';
      earliest_date?: string;
      latest_date?: string;
      error?: string;
    };
  };
  simulation_ready: boolean;
  message: string;
}

export interface SmartRefreshResponse {
  status: string;
  message: string;
  mode: string;
  features: string[];
  note: string;
}

export interface RefreshStatusResponse {
  assets: {
    count: number;
    symbols: string[];
    has_benchmark: boolean;
  };
  prices: {
    latest_date?: string;
    days_old?: number;
    needs_update: boolean;
  };
  recommendation: string;
}

export default api;