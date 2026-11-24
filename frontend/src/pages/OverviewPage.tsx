/**
 * Page 1: Overview Dashboard with real database-backed metrics, queue status, trends & activity.
 */
import React, { useState, useEffect } from 'react';
import {
  Files,
  CheckCircle2,
  AlertCircle,
  MessageSquare,
  FileText,
  Bot,
  Clock,
  Zap,
  DollarSign,
  RefreshCw,
  Search,
  Filter
} from 'lucide-react';
import { api, OverviewMetrics } from '../api/endpoints';
import { useAuth } from '../context/AuthContext';

export const OverviewPage: React.FC = () => {
  const { activeWorkspace } = useAuth();
  const [metrics, setMetrics] = useState<OverviewMetrics | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [dateFilter, setDateFilter] = useState('7d');

  const fetchMetrics = async () => {
    setIsLoading(true);
    try {
      const data = await api.getOverviewMetrics();
      setMetrics(data);
    } catch (err) {
      console.error('Failed to load overview metrics', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchMetrics();
  }, [activeWorkspace?.id]);

  return (
    <div className="space-y-6">
      {/* Top Header & Controls */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Platform Overview</h1>
          <p className="text-sm text-slate-400">Live enterprise telemetry, document ingestion health, and agent activity.</p>
        </div>
        <div className="flex items-center gap-2">
          <select
            value={dateFilter}
            onChange={(e) => setDateFilter(e.target.value)}
            className="px-3 py-2 rounded-lg bg-slate-900 border border-slate-800 text-xs text-slate-300 focus:outline-none focus:ring-1 focus:ring-blue-500"
          >
            <option value="24h">Last 24 Hours</option>
            <option value="7d">Last 7 Days</option>
            <option value="30d">Last 30 Days</option>
            <option value="all">All Time</option>
          </select>
          <button
            onClick={fetchMetrics}
            disabled={isLoading}
            className="p-2 rounded-lg bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-300 hover:text-white transition-colors"
            title="Refresh metrics"
          >
            <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="p-5 rounded-xl bg-slate-900/90 border border-slate-800 shadow-sm relative overflow-hidden">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">Total Documents</span>
            <div className="w-8 h-8 rounded-lg bg-blue-500/10 flex items-center justify-center text-blue-400">
              <Files className="w-4 h-4" />
            </div>
          </div>
          <p className="text-2xl font-bold text-white mt-2">{metrics?.total_documents ?? 0}</p>
          <div className="flex items-center gap-2 mt-2 text-xs">
            <span className="text-emerald-400 flex items-center gap-1">
              <CheckCircle2 className="w-3 h-3" /> {metrics?.processed_documents ?? 0} processed
            </span>
            {metrics?.failed_documents ? (
              <span className="text-rose-400 flex items-center gap-1">
                <AlertCircle className="w-3 h-3" /> {metrics.failed_documents} failed
              </span>
            ) : null}
          </div>
        </div>

        <div className="p-5 rounded-xl bg-slate-900/90 border border-slate-800 shadow-sm relative overflow-hidden">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">AI Queries Executed</span>
            <div className="w-8 h-8 rounded-lg bg-indigo-500/10 flex items-center justify-center text-indigo-400">
              <MessageSquare className="w-4 h-4" />
            </div>
          </div>
          <p className="text-2xl font-bold text-white mt-2">{metrics?.total_ai_queries ?? 0}</p>
          <p className="text-xs text-slate-400 mt-2">Across {metrics?.total_conversations ?? 0} active workspaces</p>
        </div>

        <div className="p-5 rounded-xl bg-slate-900/90 border border-slate-800 shadow-sm relative overflow-hidden">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">Agent Tasks Completed</span>
            <div className="w-8 h-8 rounded-lg bg-purple-500/10 flex items-center justify-center text-purple-400">
              <Bot className="w-4 h-4" />
            </div>
          </div>
          <p className="text-2xl font-bold text-white mt-2">{metrics?.agent_tasks_completed ?? 0}</p>
          <p className="text-xs text-slate-400 mt-2">{metrics?.total_reports ?? 0} intelligence reports generated</p>
        </div>

        <div className="p-5 rounded-xl bg-slate-900/90 border border-slate-800 shadow-sm relative overflow-hidden">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">Avg Latency & Tokens</span>
            <div className="w-8 h-8 rounded-lg bg-emerald-500/10 flex items-center justify-center text-emerald-400">
              <Zap className="w-4 h-4" />
            </div>
          </div>
          <p className="text-2xl font-bold text-white mt-2">{metrics?.avg_response_time_ms ?? 0} ms</p>
          <div className="flex items-center justify-between mt-2 text-xs text-slate-400">
            <span>{metrics?.total_tokens_consumed.toLocaleString() ?? 0} tokens</span>
            <span className="text-emerald-400 font-medium">${metrics?.estimated_api_cost ?? '0.00'}</span>
          </div>
        </div>
      </div>

      {/* Middle Row: Document Breakdown & Processing Queue */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Processing Queue Status */}
        <div className="p-5 rounded-xl bg-slate-900 border border-slate-800 lg:col-span-1">
          <h2 className="text-sm font-semibold text-white uppercase tracking-wider mb-4 flex items-center gap-2">
            <Clock className="w-4 h-4 text-blue-400" /> Ingestion Status
          </h2>
          <div className="space-y-4">
            <div className="p-3 rounded-lg bg-slate-800/60 border border-slate-700/60 flex items-center justify-between">
              <div>
                <p className="text-xs text-slate-400 font-medium">Pipeline Queue</p>
                <p className="text-sm font-semibold text-emerald-400 mt-0.5">{metrics?.processing_queue_status || 'Operational'}</p>
              </div>
              <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse"></span>
            </div>
            <div className="space-y-2">
              <div className="flex justify-between text-xs text-slate-400">
                <span>Ingestion Completion Rate</span>
                <span>
                  {metrics?.total_documents
                    ? Math.round((metrics.processed_documents / metrics.total_documents) * 100)
                    : 100}
                  %
                </span>
              </div>
              <div className="w-full h-2 rounded-full bg-slate-800 overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-blue-500 to-emerald-500 rounded-full"
                  style={{
                    width: `${
                      metrics?.total_documents
                        ? Math.round((metrics.processed_documents / metrics.total_documents) * 100)
                        : 100
                    }%`,
                  }}
                ></div>
              </div>
            </div>
          </div>
        </div>

        {/* Documents by Type */}
        <div className="p-5 rounded-xl bg-slate-900 border border-slate-800 lg:col-span-2">
          <h2 className="text-sm font-semibold text-white uppercase tracking-wider mb-4 flex items-center gap-2">
            <Files className="w-4 h-4 text-indigo-400" /> Formats Processed
          </h2>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            {Object.entries(metrics?.documents_by_type || {}).map(([ext, count]) => (
              <div key={ext} className="p-3 rounded-lg bg-slate-800/50 border border-slate-800 text-center">
                <p className="text-xs font-semibold text-slate-400">{ext}</p>
                <p className="text-lg font-bold text-white mt-1">{count}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Recent Activities Feed */}
      <div className="p-5 rounded-xl bg-slate-900 border border-slate-800">
        <h2 className="text-sm font-semibold text-white uppercase tracking-wider mb-4">Live System Activity Audit</h2>
        <div className="divide-y divide-slate-800/80">
          {metrics?.recent_activities && metrics.recent_activities.length > 0 ? (
            metrics.recent_activities.map((act: any) => (
              <div key={act.id} className="py-3 flex items-center justify-between text-xs">
                <div className="flex items-center gap-3">
                  <span
                    className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider ${
                      act.status === 'SUCCESS' ? 'bg-emerald-500/10 text-emerald-400' : 'bg-rose-500/10 text-rose-400'
                    }`}
                  >
                    {act.action}
                  </span>
                  <span className="text-slate-300 font-medium">{act.resource}</span>
                </div>
                <span className="text-slate-500">{new Date(act.timestamp).toLocaleTimeString()}</span>
              </div>
            ))
          ) : (
            <p className="text-xs text-slate-500 py-4 text-center">No recent activity logs found.</p>
          )}
        </div>
      </div>
    </div>
  );
};
