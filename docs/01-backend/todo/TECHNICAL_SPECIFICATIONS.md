# Technical Specifications - Frontend Implementation

## API Service Implementation Specifications

### 1. BackgroundTaskService

```typescript
// apps/web/app/services/api/background.ts

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
```

### 2. DiagnosticsService

```typescript
// apps/web/app/services/api/diagnostics.ts

import { ApiService } from './base';

export interface TableInfo {
  count: number;
  status: 'OK' | 'EMPTY' | 'ERROR';
  earliest_date?: string;
  latest_date?: string;
  error?: string;
}

export interface DatabaseStatus {
  timestamp: string;
  tables: {
    users: TableInfo;
    assets: TableInfo;
    prices: TableInfo;
    index_values: TableInfo;
    allocations: TableInfo;
  };
  simulation_ready: boolean;
  message: string;
}

export interface RefreshStatus {
  assets: {
    count: number;
    symbols: string[];
    has_benchmark: boolean;
  };
  prices: {
    latest_date: string | null;
    days_old: number | null;
    needs_update: boolean;
  };
  recommendation: string;
}

export interface CacheStatus {
  timestamp: string;
  status: 'connected' | 'disconnected' | 'error';
  message: string;
  stats?: {
    total_entries: number;
    memory_usage: string;
    hit_rate: number;
    miss_rate: number;
    keys_by_prefix: Record<string, number>;
  };
  error?: string;
}

export interface CacheInvalidateResponse {
  timestamp: string;
  status: 'success' | 'error';
  invalidated_count: number;
  message: string;
  error?: string;
}

export interface TestRefreshResult {
  timestamp: string;
  steps: Array<{
    step: string;
    status: 'starting' | 'success' | 'failed' | 'skipped';
    [key: string]: any;
  }>;
  overall_status: 'SUCCESS' | 'PARTIAL_SUCCESS' | 'FAILED';
  error?: string;
  traceback?: string;
}

export interface RecalculateResult {
  timestamp: string;
  status: 'starting' | 'success' | 'error';
  before?: {
    index_values: number;
    allocations: number;
  };
  after?: {
    index_values: number;
    allocations: number;
  };
  sample_recent_values?: Array<{
    date: string;
    value: number;
  }>;
  error?: string;
  traceback?: string;
}

export class DiagnosticsService extends ApiService {
  async getDatabaseStatus(): Promise<DatabaseStatus> {
    return this.get<DatabaseStatus>('/api/v1/diagnostics/database-status');
  }

  async getRefreshStatus(): Promise<RefreshStatus> {
    return this.get<RefreshStatus>('/api/v1/diagnostics/refresh-status');
  }

  async getCacheStatus(): Promise<CacheStatus> {
    return this.get<CacheStatus>('/api/v1/diagnostics/cache-status');
  }

  async invalidateCache(pattern: string = '*'): Promise<CacheInvalidateResponse> {
    return this.post<CacheInvalidateResponse>('/api/v1/diagnostics/cache-invalidate', { pattern });
  }

  async testRefresh(): Promise<TestRefreshResult> {
    return this.post<TestRefreshResult>('/api/v1/diagnostics/test-refresh');
  }

  async recalculateIndex(): Promise<RecalculateResult> {
    return this.post<RecalculateResult>('/api/v1/diagnostics/recalculate-index');
  }
}

export const diagnosticsService = new DiagnosticsService();
```

### 3. BenchmarkService

```typescript
// apps/web/app/services/api/benchmark.ts

import { ApiService } from './base';
import { SeriesPoint } from '../../types/portfolio';

export interface BenchmarkResponse {
  series: SeriesPoint[];
}

export interface PerformanceComparison {
  autoindex: {
    start_value: number;
    end_value: number;
    total_return: number;
    annualized_return: number;
    volatility: number;
    sharpe_ratio: number;
  };
  sp500: {
    start_value: number;
    end_value: number;
    total_return: number;
    annualized_return: number;
    volatility: number;
    sharpe_ratio: number;
  };
  outperformance: {
    total: number;
    annualized: number;
    information_ratio: number;
  };
}

export class BenchmarkService extends ApiService {
  async getSP500Data(): Promise<BenchmarkResponse> {
    return this.get<BenchmarkResponse>('/api/v1/benchmark/sp500');
  }

  async comparePerformance(
    startDate?: string, 
    endDate?: string
  ): Promise<PerformanceComparison> {
    const params = new URLSearchParams();
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    
    const query = params.toString() ? `?${params.toString()}` : '';
    return this.get<PerformanceComparison>(`/api/v1/benchmark/compare${query}`);
  }
}

export const benchmarkService = new BenchmarkService();
```

## React Component Specifications

### 1. Task Management Components

```typescript
// apps/web/app/tasks/components/TaskQueue.tsx

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { backgroundTaskService, TaskStatus, ActiveTasks } from '../../services/api/background';

interface TaskQueueProps {
  onTaskComplete?: (taskId: string, status: TaskStatus) => void;
  autoRefresh?: boolean;
  refreshInterval?: number;
}

export function TaskQueue({ 
  onTaskComplete, 
  autoRefresh = true, 
  refreshInterval = 2000 
}: TaskQueueProps) {
  const [activeTasks, setActiveTasks] = useState<ActiveTasks | null>(null);
  const [taskStatuses, setTaskStatuses] = useState<Map<string, TaskStatus>>(new Map());
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch active tasks
  const fetchActiveTasks = async () => {
    try {
      const tasks = await backgroundTaskService.getActiveTasks();
      setActiveTasks(tasks);
      
      // Poll status for each active task
      if (tasks.active) {
        Object.values(tasks.active).flat().forEach(async (task: any) => {
          const status = await backgroundTaskService.getTaskStatus(task.id);
          setTaskStatuses(prev => new Map(prev).set(task.id, status));
        });
      }
    } catch (err) {
      setError('Failed to fetch active tasks');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchActiveTasks();
    
    if (autoRefresh) {
      const interval = setInterval(fetchActiveTasks, refreshInterval);
      return () => clearInterval(interval);
    }
  }, [autoRefresh, refreshInterval]);

  const getTaskProgress = (taskId: string): number => {
    const status = taskStatuses.get(taskId);
    if (!status) return 0;
    if (status.status === 'SUCCESS') return 100;
    if (status.current && status.total) {
      return (status.current / status.total) * 100;
    }
    return status.status === 'STARTED' ? 50 : 0;
  };

  const getStatusColor = (status: string): string => {
    switch (status) {
      case 'SUCCESS': return 'bg-green-500';
      case 'FAILURE': return 'bg-red-500';
      case 'STARTED': return 'bg-blue-500';
      case 'PENDING': return 'bg-yellow-500';
      case 'RETRY': return 'bg-orange-500';
      default: return 'bg-gray-500';
    }
  };

  if (loading) {
    return (
      <div className="space-y-4">
        <div className="h-20 skeleton rounded-lg" />
        <div className="h-20 skeleton rounded-lg" />
        <div className="h-20 skeleton rounded-lg" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-4">
        <p className="text-red-400">{error}</p>
        <button onClick={fetchActiveTasks} className="btn-secondary btn-sm mt-2">
          Retry
        </button>
      </div>
    );
  }

  const totalTasks = activeTasks?.stats.total_active || 0;

  return (
    <div className="space-y-4">
      {/* Summary Stats */}
      <div className="grid grid-cols-3 gap-4">
        <div className="bg-white/5 rounded-lg p-4 border border-white/10">
          <p className="text-xs text-neutral-400">Active Tasks</p>
          <p className="text-2xl font-bold gradient-text">
            {activeTasks?.stats.total_active || 0}
          </p>
        </div>
        <div className="bg-white/5 rounded-lg p-4 border border-white/10">
          <p className="text-xs text-neutral-400">Scheduled</p>
          <p className="text-2xl font-bold text-blue-400">
            {activeTasks?.stats.total_scheduled || 0}
          </p>
        </div>
        <div className="bg-white/5 rounded-lg p-4 border border-white/10">
          <p className="text-xs text-neutral-400">Reserved</p>
          <p className="text-2xl font-bold text-yellow-400">
            {activeTasks?.stats.total_reserved || 0}
          </p>
        </div>
      </div>

      {/* Task List */}
      <div className="space-y-2">
        <AnimatePresence>
          {activeTasks?.active && Object.values(activeTasks.active).flat().map((task: any) => {
            const status = taskStatuses.get(task.id);
            const progress = getTaskProgress(task.id);
            
            return (
              <motion.div
                key={task.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                className="bg-white/5 rounded-lg p-4 border border-white/10"
              >
                <div className="flex justify-between items-start mb-2">
                  <div>
                    <h4 className="font-medium text-white">{task.name}</h4>
                    <p className="text-xs text-neutral-400">ID: {task.id}</p>
                  </div>
                  <span className={`px-2 py-1 rounded text-xs text-white ${
                    status ? getStatusColor(status.status) : 'bg-gray-500'
                  }`}>
                    {status?.status || 'UNKNOWN'}
                  </span>
                </div>
                
                {/* Progress Bar */}
                <div className="w-full bg-white/10 rounded-full h-2 overflow-hidden">
                  <motion.div
                    className="h-full bg-gradient-to-r from-purple-500 to-pink-500"
                    initial={{ width: 0 }}
                    animate={{ width: `${progress}%` }}
                    transition={{ duration: 0.5 }}
                  />
                </div>
                
                {status?.error && (
                  <p className="text-xs text-red-400 mt-2">{status.error}</p>
                )}
              </motion.div>
            );
          })}
        </AnimatePresence>
        
        {totalTasks === 0 && (
          <div className="text-center py-8 text-neutral-400">
            <p>No active tasks</p>
          </div>
        )}
      </div>
    </div>
  );
}
```

### 2. Diagnostics Dashboard Component

```typescript
// apps/web/app/diagnostics/components/SystemHealth.tsx

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  diagnosticsService, 
  DatabaseStatus, 
  CacheStatus, 
  RefreshStatus 
} from '../../services/api/diagnostics';

export function SystemHealthDashboard() {
  const [databaseStatus, setDatabaseStatus] = useState<DatabaseStatus | null>(null);
  const [cacheStatus, setCacheStatus] = useState<CacheStatus | null>(null);
  const [refreshStatus, setRefreshStatus] = useState<RefreshStatus | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAllStatuses();
    const interval = setInterval(fetchAllStatuses, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchAllStatuses = async () => {
    try {
      const [db, cache, refresh] = await Promise.all([
        diagnosticsService.getDatabaseStatus(),
        diagnosticsService.getCacheStatus(),
        diagnosticsService.getRefreshStatus()
      ]);
      
      setDatabaseStatus(db);
      setCacheStatus(cache);
      setRefreshStatus(refresh);
    } catch (error) {
      console.error('Failed to fetch system status:', error);
    } finally {
      setLoading(false);
    }
  };

  const getHealthColor = (status: string): string => {
    switch (status) {
      case 'OK':
      case 'connected':
        return 'text-green-400';
      case 'EMPTY':
      case 'disconnected':
        return 'text-yellow-400';
      case 'ERROR':
      case 'error':
        return 'text-red-400';
      default:
        return 'text-neutral-400';
    }
  };

  const getHealthIcon = (status: string): string => {
    switch (status) {
      case 'OK':
      case 'connected':
        return '✓';
      case 'EMPTY':
      case 'disconnected':
        return '⚠';
      case 'ERROR':
      case 'error':
        return '✗';
      default:
        return '?';
    }
  };

  if (loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="h-48 skeleton rounded-xl" />
        <div className="h-48 skeleton rounded-xl" />
        <div className="h-48 skeleton rounded-xl" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Overall System Status */}
      <div className="bg-white/5 rounded-xl p-6 border border-white/10">
        <h3 className="text-lg font-semibold gradient-text mb-4">System Overview</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Database Health */}
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-white/5 rounded-lg p-4 border border-white/10"
          >
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-neutral-300">Database</span>
              <span className={`text-2xl ${
                databaseStatus?.simulation_ready 
                  ? 'text-green-400' 
                  : 'text-yellow-400'
              }`}>
                {databaseStatus?.simulation_ready ? '✓' : '⚠'}
              </span>
            </div>
            <p className="text-xs text-neutral-400">
              {databaseStatus?.message}
            </p>
          </motion.div>

          {/* Cache Health */}
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.1 }}
            className="bg-white/5 rounded-lg p-4 border border-white/10"
          >
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-neutral-300">Cache</span>
              <span className={`text-2xl ${getHealthColor(cacheStatus?.status || '')}`}>
                {getHealthIcon(cacheStatus?.status || '')}
              </span>
            </div>
            <p className="text-xs text-neutral-400">
              {cacheStatus?.message}
            </p>
            {cacheStatus?.stats && (
              <div className="mt-2 text-xs">
                <span className="text-green-400">
                  Hit: {(cacheStatus.stats.hit_rate * 100).toFixed(1)}%
                </span>
                <span className="text-neutral-400 mx-2">|</span>
                <span className="text-orange-400">
                  Miss: {(cacheStatus.stats.miss_rate * 100).toFixed(1)}%
                </span>
              </div>
            )}
          </motion.div>

          {/* Data Freshness */}
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.2 }}
            className="bg-white/5 rounded-lg p-4 border border-white/10"
          >
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-neutral-300">Data</span>
              <span className={`text-2xl ${
                refreshStatus?.prices.needs_update 
                  ? 'text-yellow-400' 
                  : 'text-green-400'
              }`}>
                {refreshStatus?.prices.needs_update ? '⚠' : '✓'}
              </span>
            </div>
            <p className="text-xs text-neutral-400">
              {refreshStatus?.recommendation}
            </p>
            {refreshStatus?.prices.days_old !== null && (
              <p className="text-xs text-neutral-500 mt-1">
                Last update: {refreshStatus.prices.days_old} days ago
              </p>
            )}
          </motion.div>
        </div>
      </div>

      {/* Database Tables */}
      {databaseStatus && (
        <div className="bg-white/5 rounded-xl p-6 border border-white/10">
          <h3 className="text-lg font-semibold gradient-text mb-4">Database Tables</h3>
          
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            {Object.entries(databaseStatus.tables).map(([table, info]) => (
              <motion.div
                key={table}
                whileHover={{ scale: 1.05 }}
                className={`p-4 rounded-lg border text-center ${
                  info.status === 'OK' 
                    ? 'bg-green-500/10 border-green-500/30'
                    : info.status === 'EMPTY'
                    ? 'bg-yellow-500/10 border-yellow-500/30'
                    : 'bg-red-500/10 border-red-500/30'
                }`}
              >
                <div className={`text-2xl font-bold ${getHealthColor(info.status)}`}>
                  {info.count.toLocaleString()}
                </div>
                <div className="text-xs text-neutral-400 capitalize mt-1">
                  {table.replace('_', ' ')}
                </div>
                {info.latest_date && (
                  <div className="text-xs text-neutral-500 mt-1">
                    {new Date(info.latest_date).toLocaleDateString()}
                  </div>
                )}
              </motion.div>
            ))}
          </div>
        </div>
      )}

      {/* Cache Details */}
      {cacheStatus?.stats && (
        <div className="bg-white/5 rounded-xl p-6 border border-white/10">
          <h3 className="text-lg font-semibold gradient-text mb-4">Cache Statistics</h3>
          
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-white/5 rounded-lg p-4">
              <p className="text-xs text-neutral-400">Total Entries</p>
              <p className="text-xl font-bold text-white">
                {cacheStatus.stats.total_entries.toLocaleString()}
              </p>
            </div>
            <div className="bg-white/5 rounded-lg p-4">
              <p className="text-xs text-neutral-400">Memory Usage</p>
              <p className="text-xl font-bold text-white">
                {cacheStatus.stats.memory_usage}
              </p>
            </div>
            <div className="bg-white/5 rounded-lg p-4">
              <p className="text-xs text-neutral-400">Hit Rate</p>
              <p className="text-xl font-bold text-green-400">
                {(cacheStatus.stats.hit_rate * 100).toFixed(1)}%
              </p>
            </div>
            <div className="bg-white/5 rounded-lg p-4">
              <p className="text-xs text-neutral-400">Miss Rate</p>
              <p className="text-xl font-bold text-orange-400">
                {(cacheStatus.stats.miss_rate * 100).toFixed(1)}%
              </p>
            </div>
          </div>

          {/* Cache Actions */}
          <div className="mt-4 flex gap-2">
            <button
              onClick={async () => {
                await diagnosticsService.invalidateCache('index');
                fetchAllStatuses();
              }}
              className="btn-secondary btn-sm"
            >
              Clear Index Cache
            </button>
            <button
              onClick={async () => {
                await diagnosticsService.invalidateCache('market');
                fetchAllStatuses();
              }}
              className="btn-secondary btn-sm"
            >
              Clear Market Cache
            </button>
            <button
              onClick={async () => {
                if (confirm('Clear all cache entries?')) {
                  await diagnosticsService.invalidateCache('*');
                  fetchAllStatuses();
                }
              }}
              className="btn-ghost btn-sm text-red-400"
            >
              Clear All Cache
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
```

## Integration with Existing Components

### Navigation Update

```typescript
// apps/web/app/components/Navigation.tsx (to be created or updated)

const navigationItems = [
  { name: 'Dashboard', href: '/dashboard', icon: 'chart' },
  { name: 'Tasks', href: '/tasks', icon: 'queue', badge: 'NEW' },
  { name: 'Diagnostics', href: '/diagnostics', icon: 'health', badge: 'NEW' },
  { name: 'Reports', href: '/reports', icon: 'document', badge: 'NEW' },
  { name: 'Risk', href: '/risk', icon: 'shield', badge: 'NEW' },
  { name: 'Strategy', href: '/strategy', icon: 'settings' },
  { name: 'AI Insights', href: '/ai-insights', icon: 'sparkles' },
  { name: 'Admin', href: '/admin', icon: 'lock' },
];
```

### Updated API Index

```typescript
// apps/web/app/services/api/index.ts

export { portfolioService } from './portfolio';
export { marketService } from './market';
export { backgroundTaskService } from './background';
export { diagnosticsService } from './diagnostics';
export { benchmarkService } from './benchmark';
export { reportsService } from './reports';

// Re-export types
export * from './background';
export * from './diagnostics';
export * from './benchmark';
export * from './reports';
```

## Testing Specifications

### Unit Tests

```typescript
// apps/web/__tests__/services/background.test.ts

import { backgroundTaskService } from '../../app/services/api/background';

describe('BackgroundTaskService', () => {
  it('should trigger refresh task', async () => {
    const response = await backgroundTaskService.triggerRefresh({ mode: 'smart' });
    expect(response.task_id).toBeDefined();
    expect(response.status).toBe('started');
  });

  it('should poll task status', async () => {
    const taskId = 'test-task-id';
    const status = await backgroundTaskService.pollTaskStatus(
      taskId,
      (status) => console.log('Progress:', status),
      100,
      10
    );
    expect(status.status).toMatch(/SUCCESS|FAILURE/);
  });
});
```

### Integration Tests

```typescript
// apps/web/__tests__/pages/tasks.test.tsx

import { render, screen, waitFor } from '@testing-library/react';
import TasksPage from '../../app/tasks/page';

describe('TasksPage', () => {
  it('should display active tasks', async () => {
    render(<TasksPage />);
    
    await waitFor(() => {
      expect(screen.getByText(/Active Tasks/i)).toBeInTheDocument();
    });
  });

  it('should refresh tasks on interval', async () => {
    jest.useFakeTimers();
    render(<TasksPage />);
    
    jest.advanceTimersByTime(2000);
    
    await waitFor(() => {
      expect(screen.getByText(/Active Tasks/i)).toBeInTheDocument();
    });
    
    jest.useRealTimers();
  });
});
```

## Performance Optimization

### 1. Memoization Strategy

```typescript
import { useMemo, useCallback } from 'react';

// Memoize expensive calculations
const processedTasks = useMemo(() => {
  return tasks.map(task => ({
    ...task,
    progress: calculateProgress(task),
    timeRemaining: estimateTimeRemaining(task)
  }));
}, [tasks]);

// Memoize callbacks
const handleTaskCancel = useCallback((taskId: string) => {
  backgroundTaskService.cancelTask(taskId);
}, []);
```

### 2. Virtualization for Large Lists

```typescript
import { FixedSizeList } from 'react-window';

<FixedSizeList
  height={600}
  itemCount={tasks.length}
  itemSize={80}
  width="100%"
>
  {({ index, style }) => (
    <div style={style}>
      <TaskCard task={tasks[index]} />
    </div>
  )}
</FixedSizeList>
```

### 3. Lazy Loading

```typescript
const TasksPage = lazy(() => import('./tasks/page'));
const DiagnosticsPage = lazy(() => import('./diagnostics/page'));
const ReportsPage = lazy(() => import('./reports/page'));
```

## Error Handling Strategy

### Global Error Boundary

```typescript
// apps/web/app/components/ErrorBoundary.tsx

export class ErrorBoundary extends Component {
  state = { hasError: false, error: null };

  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
    // Send to error tracking service
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen flex items-center justify-center">
          <div className="card max-w-md">
            <h2 className="text-xl font-bold text-red-400 mb-4">
              Something went wrong
            </h2>
            <p className="text-neutral-300 mb-4">
              {this.state.error?.message}
            </p>
            <button 
              onClick={() => window.location.reload()} 
              className="btn-primary"
            >
              Reload Page
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
```

## Deployment Considerations

### Environment Variables

```bash
# apps/web/.env.local
NEXT_PUBLIC_API_URL=https://api.waardhaven.com
NEXT_PUBLIC_WEBSOCKET_URL=wss://api.waardhaven.com/ws
NEXT_PUBLIC_ENABLE_TASKS=true
NEXT_PUBLIC_ENABLE_DIAGNOSTICS=true
NEXT_PUBLIC_POLLING_INTERVAL=2000
```

### Build Optimization

```json
// apps/web/next.config.js
module.exports = {
  reactStrictMode: true,
  swcMinify: true,
  experimental: {
    optimizeCss: true,
  },
  images: {
    domains: ['api.waardhaven.com'],
  },
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: `${process.env.NEXT_PUBLIC_API_URL}/:path*`,
      },
    ];
  },
};
```

---

This technical specification provides detailed implementation guidelines for all missing frontend features. Each component is designed to integrate seamlessly with the existing codebase while maintaining consistency in design patterns and user experience.