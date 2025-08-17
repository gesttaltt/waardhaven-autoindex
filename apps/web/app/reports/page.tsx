"use client";

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { motion, AnimatePresence } from 'framer-motion';
import { backgroundTaskService, TaskStatus } from '../services/api/background';

interface ReportTask {
  id: string;
  type: 'performance' | 'allocation' | 'risk';
  period: number;
  status: 'generating' | 'completed' | 'failed';
  createdAt: string;
  completedAt?: string;
  downloadUrl?: string;
}

export default function ReportsPage() {
  const router = useRouter();
  const [reportType, setReportType] = useState<'performance' | 'allocation' | 'risk'>('performance');
  const [periodDays, setPeriodDays] = useState(30);
  const [generating, setGenerating] = useState(false);
  const [reportTasks, setReportTasks] = useState<ReportTask[]>([]);
  const [activeTaskId, setActiveTaskId] = useState<string | null>(null);
  
  const token = typeof window !== "undefined" ? localStorage.getItem("token") : null;

  useEffect(() => {
    if (!token) {
      router.push("/login");
      return;
    }
    
    // Load saved report tasks from localStorage
    const savedTasks = localStorage.getItem('reportTasks');
    if (savedTasks) {
      setReportTasks(JSON.parse(savedTasks));
    }
  }, [token, router]);

  useEffect(() => {
    // Poll for active task status
    if (activeTaskId) {
      const interval = setInterval(async () => {
        try {
          const status = await backgroundTaskService.getTaskStatus(activeTaskId);
          updateTaskStatus(activeTaskId, status);
          
          if (status.status === 'SUCCESS' || status.status === 'FAILURE') {
            setActiveTaskId(null);
          }
        } catch (error) {
          console.error('Failed to poll task status:', error);
        }
      }, 2000);
      
      return () => clearInterval(interval);
    }
  }, [activeTaskId]);

  const updateTaskStatus = (taskId: string, status: TaskStatus) => {
    setReportTasks(prev => {
      const updated = prev.map(task => {
        if (task.id === taskId) {
          const newStatus: ReportTask['status'] = status.status === 'SUCCESS' ? 'completed' : 
                                                   status.status === 'FAILURE' ? 'failed' : 'generating';
          return {
            ...task,
            status: newStatus,
            completedAt: status.status === 'SUCCESS' || status.status === 'FAILURE' 
              ? new Date().toISOString() : undefined
          } as ReportTask;
        }
        return task;
      });
      
      // Save to localStorage
      localStorage.setItem('reportTasks', JSON.stringify(updated));
      return updated;
    });
  };

  const handleGenerateReport = async () => {
    setGenerating(true);
    try {
      const response = await backgroundTaskService.generateReport({
        report_type: reportType,
        period_days: periodDays
      });
      
      const newTask: ReportTask = {
        id: response.task_id,
        type: reportType,
        period: periodDays,
        status: 'generating',
        createdAt: new Date().toISOString()
      };
      
      setReportTasks(prev => {
        const updated = [newTask, ...prev];
        localStorage.setItem('reportTasks', JSON.stringify(updated));
        return updated;
      });
      
      setActiveTaskId(response.task_id);
    } catch (error: any) {
      alert('Failed to generate report: ' + (error.message || 'Unknown error'));
    } finally {
      setGenerating(false);
    }
  };

  const getReportIcon = (type: string) => {
    switch (type) {
      case 'performance': return '📈';
      case 'allocation': return '🎯';
      case 'risk': return '⚠️';
      default: return '📊';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'text-green-400';
      case 'generating': return 'text-blue-400';
      case 'failed': return 'text-red-400';
      default: return 'text-neutral-400';
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <main className="min-h-screen relative">
      <div className="fixed inset-0 gradient-bg opacity-5" />
      
      <div className="max-w-7xl mx-auto px-6 py-10 relative">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          {/* Header */}
          <div className="flex justify-between items-start mb-8">
            <div>
              <h1 className="text-4xl font-bold mb-2 gradient-text">Reports & Analytics</h1>
              <p className="text-neutral-400">Generate and manage portfolio reports</p>
            </div>
            <div className="flex items-center gap-3 mt-2">
              <button
                onClick={() => router.push("/dashboard")}
                className="btn-ghost btn-sm"
              >
                Back to Dashboard
              </button>
            </div>
          </div>

          {/* Report Generator */}
          <motion.section
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="card mb-6"
          >
            <h2 className="text-xl font-semibold gradient-text mb-4">Generate New Report</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div>
                <label className="text-sm text-neutral-300">Report Type</label>
                <select
                  value={reportType}
                  onChange={(e) => setReportType(e.target.value as any)}
                  className="input mt-1"
                >
                  <option value="performance">Performance Report</option>
                  <option value="allocation">Allocation Report</option>
                  <option value="risk">Risk Analysis Report</option>
                </select>
              </div>
              
              <div>
                <label className="text-sm text-neutral-300">Period (Days)</label>
                <select
                  value={periodDays}
                  onChange={(e) => setPeriodDays(Number(e.target.value))}
                  className="input mt-1"
                >
                  <option value="7">Last 7 Days</option>
                  <option value="30">Last 30 Days</option>
                  <option value="90">Last 90 Days</option>
                  <option value="180">Last 6 Months</option>
                  <option value="365">Last Year</option>
                </select>
              </div>
              
              <div>
                <label className="text-sm text-neutral-300">Format</label>
                <select className="input mt-1" disabled>
                  <option>PDF (Default)</option>
                  <option>Excel (Coming Soon)</option>
                  <option>CSV (Coming Soon)</option>
                </select>
              </div>
              
              <div className="flex items-end">
                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={handleGenerateReport}
                  disabled={generating}
                  className="btn-primary w-full"
                >
                  {generating ? (
                    <span className="flex items-center justify-center gap-2">
                      <motion.div
                        animate={{ rotate: 360 }}
                        transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                        className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full"
                      />
                      Generating...
                    </span>
                  ) : (
                    "Generate Report"
                  )}
                </motion.button>
              </div>
            </div>

            <div className="mt-4 p-4 bg-white/5 rounded-lg border border-white/10">
              <h3 className="text-sm font-medium text-neutral-300 mb-2">Report Contents</h3>
              <div className="text-xs text-neutral-400">
                {reportType === 'performance' && (
                  <ul className="space-y-1">
                    <li>• Portfolio value trends and growth metrics</li>
                    <li>• Comparison with S&P 500 benchmark</li>
                    <li>• Top performing assets</li>
                    <li>• Return on investment calculations</li>
                  </ul>
                )}
                {reportType === 'allocation' && (
                  <ul className="space-y-1">
                    <li>• Current portfolio composition</li>
                    <li>• Sector distribution analysis</li>
                    <li>• Asset weight breakdown</li>
                    <li>• Rebalancing recommendations</li>
                  </ul>
                )}
                {reportType === 'risk' && (
                  <ul className="space-y-1">
                    <li>• Risk metrics (Sharpe, Sortino ratios)</li>
                    <li>• Maximum drawdown analysis</li>
                    <li>• Volatility measurements</li>
                    <li>• Value at Risk (VaR) calculations</li>
                  </ul>
                )}
              </div>
            </div>
          </motion.section>

          {/* Report History */}
          <motion.section
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="card"
          >
            <h2 className="text-xl font-semibold gradient-text mb-4">Report History</h2>
            
            {reportTasks.length === 0 ? (
              <div className="text-center py-12 text-neutral-400">
                <p className="text-lg mb-2">No reports generated yet</p>
                <p className="text-sm">Generate your first report to see it here</p>
              </div>
            ) : (
              <div className="space-y-3">
                <AnimatePresence>
                  {reportTasks.map((task) => (
                    <motion.div
                      key={task.id}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      exit={{ opacity: 0, x: 20 }}
                      className="bg-white/5 rounded-lg p-4 border border-white/10"
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-4">
                          <div className="text-3xl">{getReportIcon(task.type)}</div>
                          <div>
                            <h3 className="font-medium text-white capitalize">
                              {task.type} Report - {task.period} Days
                            </h3>
                            <p className="text-xs text-neutral-400">
                              Created: {formatDate(task.createdAt)}
                            </p>
                            {task.completedAt && (
                              <p className="text-xs text-neutral-400">
                                Completed: {formatDate(task.completedAt)}
                              </p>
                            )}
                          </div>
                        </div>
                        
                        <div className="flex items-center gap-3">
                          <span className={`text-sm font-medium ${getStatusColor(task.status)}`}>
                            {task.status === 'generating' && (
                              <span className="flex items-center gap-2">
                                <motion.div
                                  animate={{ rotate: 360 }}
                                  transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                                  className="w-3 h-3 border-2 border-blue-400/30 border-t-blue-400 rounded-full"
                                />
                                Generating
                              </span>
                            )}
                            {task.status === 'completed' && 'Completed'}
                            {task.status === 'failed' && 'Failed'}
                          </span>
                          
                          {task.status === 'completed' && (
                            <motion.button
                              whileHover={{ scale: 1.05 }}
                              whileTap={{ scale: 0.95 }}
                              className="btn-secondary btn-sm"
                              onClick={() => alert('Download functionality coming soon!')}
                            >
                              Download
                            </motion.button>
                          )}
                        </div>
                      </div>
                      
                      {task.status === 'generating' && (
                        <div className="mt-3">
                          <div className="w-full bg-white/10 rounded-full h-2 overflow-hidden">
                            <motion.div
                              className="h-full bg-gradient-to-r from-blue-500 to-purple-500"
                              initial={{ width: 0 }}
                              animate={{ width: '60%' }}
                              transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
                            />
                          </div>
                        </div>
                      )}
                    </motion.div>
                  ))}
                </AnimatePresence>
              </div>
            )}
          </motion.section>

          {/* Quick Report Templates */}
          <motion.section
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="card mt-6"
          >
            <h2 className="text-xl font-semibold gradient-text mb-4">Quick Templates</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => {
                  setReportType('performance');
                  setPeriodDays(30);
                  handleGenerateReport();
                }}
                className="p-4 bg-white/5 rounded-lg border border-white/10 hover:bg-white/10 transition-all text-left"
              >
                <div className="text-2xl mb-2">📊</div>
                <h3 className="text-sm font-medium text-white">Monthly Performance</h3>
                <p className="text-xs text-neutral-400 mt-1">
                  Last 30 days performance overview
                </p>
              </motion.button>

              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => {
                  setReportType('risk');
                  setPeriodDays(90);
                  handleGenerateReport();
                }}
                className="p-4 bg-white/5 rounded-lg border border-white/10 hover:bg-white/10 transition-all text-left"
              >
                <div className="text-2xl mb-2">🛡️</div>
                <h3 className="text-sm font-medium text-white">Quarterly Risk</h3>
                <p className="text-xs text-neutral-400 mt-1">
                  90-day risk analysis report
                </p>
              </motion.button>

              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => {
                  setReportType('allocation');
                  setPeriodDays(7);
                  handleGenerateReport();
                }}
                className="p-4 bg-white/5 rounded-lg border border-white/10 hover:bg-white/10 transition-all text-left"
              >
                <div className="text-2xl mb-2">🎯</div>
                <h3 className="text-sm font-medium text-white">Weekly Allocation</h3>
                <p className="text-xs text-neutral-400 mt-1">
                  Current portfolio distribution
                </p>
              </motion.button>
            </div>
          </motion.section>
        </motion.div>
      </div>
    </main>
  );
}