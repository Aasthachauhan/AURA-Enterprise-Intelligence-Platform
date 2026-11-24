/**
 * Page 5: AI Agents Monitor & Human-in-the-Loop Approval Manager.
 */
import React, { useState, useEffect } from 'react';
import {
  Bot,
  CheckCircle2,
  AlertCircle,
  Clock,
  ShieldAlert,
  ArrowRight,
  RefreshCw,
  Cpu,
  Layers
} from 'lucide-react';
import { api } from '../api/endpoints';
import { useAuth } from '../context/AuthContext';

export const AgentsPage: React.FC = () => {
  const { activeWorkspace } = useAuth();
  const [agentRuns, setAgentRuns] = useState<any[]>([]);
  const [toolExecutions, setToolExecutions] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedRun, setSelectedRun] = useState<any | null>(null);
  
  // Mission dispatch state
  const [missionQuery, setMissionQuery] = useState('');
  const [selectedAgentType, setSelectedAgentType] = useState('supervisor');
  const [isDispatching, setIsDispatching] = useState(false);

  const fetchAgentData = async () => {
    setIsLoading(true);
    try {
      const [runs, tools] = await Promise.all([
        api.listAgentRuns(),
        api.listToolExecutions(),
      ]);
      setAgentRuns(runs);
      setToolExecutions(tools);
      if (runs.length > 0 && !selectedRun) {
        setSelectedRun(runs[0]);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDispatchMission = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!missionQuery.trim()) return;
    setIsDispatching(true);
    try {
      const run = await api.executeAgentMission({
        query: missionQuery,
        agent_type: selectedAgentType,
      });
      setMissionQuery('');
      await fetchAgentData();
      setSelectedRun(run);
    } catch (err: any) {
      alert(`Mission error: ${err.message}`);
    } finally {
      setIsDispatching(false);
    }
  };

  useEffect(() => {
    fetchAgentData();
  }, [activeWorkspace?.id]);

  const handleApproval = async (runId: string, approved: boolean) => {
    try {
      await api.submitApproval(runId, approved, approved ? 'Approved by human administrator' : 'Rejected');
      fetchAgentData();
    } catch (err) {
      console.error(err);
    }
  };

  const agents = [
    { name: 'Supervisor Agent', role: 'Task breakdown & orchestration', status: 'Active' },
    { name: 'Research Agent', role: 'Document retrieval & evidence search', status: 'Active' },
    { name: 'Document Intelligence', role: 'Entity, table & fact extraction', status: 'Active' },
    { name: 'Analytical Agent', role: 'Pattern recognition & gap analysis', status: 'Active' },
    { name: 'Execution Agent', role: 'MCP & API tool invocation', status: 'Guarded' },
    { name: 'Report Generation', role: 'Synthesis & executive brief export', status: 'Active' },
    { name: 'Verification Agent', role: 'Grounding & hallucination prevention', status: 'Active' },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">AI Agent Orchestration</h1>
          <p className="text-sm text-slate-400">Monitor multi-agent execution traces, subtask plans, and human-in-the-loop checkpoints.</p>
        </div>
        <button
          onClick={fetchAgentData}
          className="p-2 rounded-lg bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-300 hover:text-white transition-colors self-start sm:self-auto"
        >
          <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
        </button>
      </div>

      {/* Agents Roster Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
        {agents.map((ag) => (
          <div key={ag.name} className="p-4 rounded-xl bg-slate-900 border border-slate-800 space-y-1.5 shadow-sm">
            <div className="flex items-center justify-between">
              <span className="font-semibold text-xs text-white flex items-center gap-1.5">
                <Bot className="w-3.5 h-3.5 text-blue-400" /> {ag.name}
              </span>
              <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                {ag.status}
              </span>
            </div>
            <p className="text-[11px] text-slate-400">{ag.role}</p>
          </div>
        ))}
      </div>

      {/* Autonomous Mission Dispatch Panel */}
      <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-3 shadow-md">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Cpu className="w-4 h-4 text-blue-400" />
            <h3 className="font-bold text-white text-xs uppercase tracking-wider">Dispatch Autonomous Agent Mission</h3>
          </div>
          <span className="text-[10px] text-slate-500">Autonomous multi-agent task execution</span>
        </div>
        <form onSubmit={handleDispatchMission} className="space-y-3">
          <div className="flex flex-col sm:flex-row gap-3">
            <input
              type="text"
              value={missionQuery}
              onChange={(e) => setMissionQuery(e.target.value)}
              placeholder="Describe the enterprise task or goal (e.g. 'Cross-examine cloud migration specs against security audit findings')..."
              className="flex-1 px-4 py-2.5 rounded-xl bg-slate-950/80 border border-slate-800 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
            />
            <select
              value={selectedAgentType}
              onChange={(e) => setSelectedAgentType(e.target.value)}
              className="px-3 py-2.5 rounded-xl bg-slate-950/80 border border-slate-800 text-xs text-slate-300 focus:outline-none focus:ring-1 focus:ring-blue-500"
            >
              <option value="supervisor">Supervisor (Full Team)</option>
              <option value="research">Research Agent</option>
              <option value="analytical">Analytical Agent</option>
              <option value="verification">Verification Agent</option>
            </select>
            <button
              type="submit"
              disabled={isDispatching || !missionQuery.trim()}
              className="px-5 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-semibold text-xs flex items-center justify-center gap-2 shadow-lg shadow-blue-600/20 disabled:opacity-40 transition-all"
            >
              <Bot className={`w-3.5 h-3.5 ${isDispatching ? 'animate-spin' : ''}`} />
              {isDispatching ? 'Orchestrating...' : 'Dispatch Mission'}
            </button>
          </div>
          {/* Quick preset chips */}
          <div className="flex items-center gap-2 flex-wrap text-[11px] text-slate-400">
            <span>Quick Missions:</span>
            <button
              type="button"
              onClick={() => setMissionQuery("Perform gap analysis between cloud architecture specs and security standards")}
              className="px-2.5 py-1 rounded-lg bg-slate-800/60 hover:bg-slate-800 border border-slate-700/60 text-slate-300 transition-colors"
            >
              Cloud vs Security Audit
            </button>
            <button
              type="button"
              onClick={() => setMissionQuery("Verify HIPAA data encryption and breach notification controls")}
              className="px-2.5 py-1 rounded-lg bg-slate-800/60 hover:bg-slate-800 border border-slate-700/60 text-slate-300 transition-colors"
            >
              HIPAA Encryption Check
            </button>
            <button
              type="button"
              onClick={() => setMissionQuery("Identify single points of failure in multi-region database failover")}
              className="px-2.5 py-1 rounded-lg bg-slate-800/60 hover:bg-slate-800 border border-slate-700/60 text-slate-300 transition-colors"
            >
              RPO/RTO Failover Review
            </button>
          </div>
        </form>
      </div>

      {/* Main Execution Split View */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Agent Runs List */}
        <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-3">
          <h2 className="text-xs font-bold text-slate-400 uppercase tracking-wider flex items-center gap-2">
            <Layers className="w-4 h-4 text-blue-400" /> Recent Agent Executions
          </h2>
          <div className="space-y-2 overflow-y-auto max-h-[500px] pr-1">
            {agentRuns.length === 0 ? (
              <p className="text-xs text-slate-500 py-6 text-center">No agent runs recorded yet.</p>
            ) : (
              agentRuns.map((run) => (
                <div
                  key={run.id}
                  onClick={() => setSelectedRun(run)}
                  className={`p-3 rounded-xl border cursor-pointer transition-all ${
                    selectedRun?.id === run.id
                      ? 'bg-blue-600/10 border-blue-500/60 shadow-md'
                      : 'bg-slate-950/60 border-slate-800/80 hover:border-slate-700'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-xs text-white capitalize">{run.workflow_name || run.agent_type}</span>
                    <span
                      className={`text-[10px] font-bold px-2 py-0.5 rounded capitalize ${
                        run.status === 'completed'
                          ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                          : run.status === 'waiting_approval'
                          ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20 animate-pulse'
                          : 'bg-blue-500/10 text-blue-400 border border-blue-500/20'
                      }`}
                    >
                      {run.status.replace('_', ' ')}
                    </span>
                  </div>
                  <p className="text-[11px] text-slate-400 mt-1 truncate">
                    {run.input_payload?.query || 'Enterprise task execution'}
                  </p>
                  <div className="flex items-center justify-between text-[10px] text-slate-500 mt-2">
                    <span>{run.duration_ms} ms</span>
                    <span>{new Date(run.created_at).toLocaleTimeString()}</span>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Selected Run Details & Subtask Steps */}
        <div className="lg:col-span-2 p-6 rounded-2xl bg-slate-900 border border-slate-800 space-y-4">
          {selectedRun ? (
            <>
              <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                <div>
                  <h3 className="font-bold text-white text-base">Execution Trace #{selectedRun.id.slice(0, 8)}</h3>
                  <p className="text-xs text-slate-400 capitalize">Agent: {selectedRun.agent_type} • Status: {selectedRun.status}</p>
                </div>
                {selectedRun.status === 'waiting_approval' && (
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => handleApproval(selectedRun.id, true)}
                      className="px-3 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-xs font-semibold text-white transition-colors"
                    >
                      Approve Action
                    </button>
                    <button
                      onClick={() => handleApproval(selectedRun.id, false)}
                      className="px-3 py-1.5 rounded-lg bg-rose-600 hover:bg-rose-500 text-xs font-semibold text-white transition-colors"
                    >
                      Reject
                    </button>
                  </div>
                )}
              </div>

              {/* Subtask Steps Timeline */}
              <div className="space-y-3">
                <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider">Subtask Decomposition Plan</h4>
                <div className="space-y-2">
                  {selectedRun.plan_steps && selectedRun.plan_steps.length > 0 ? (
                    selectedRun.plan_steps.map((st: any, i: number) => (
                      <div key={i} className="p-3 rounded-lg bg-slate-950/80 border border-slate-800 flex items-center justify-between text-xs">
                        <div className="flex items-center gap-2.5">
                          <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                          <span className="font-medium text-slate-200">{st.name || st.step || `Step ${i + 1}`}</span>
                        </div>
                        <span className="text-[10px] text-slate-400 uppercase font-semibold">{st.agent || 'Automated'}</span>
                      </div>
                    ))
                  ) : (
                    <p className="text-xs text-slate-500">Standard direct reasoning path without discrete subtasks.</p>
                  )}
                </div>
              </div>

              {/* Input & Output payloads */}
              <div className="space-y-2">
                <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider">Payload Inspector</h4>
                <div className="p-3 rounded-lg bg-slate-950/90 border border-slate-800 text-xs font-mono text-slate-300 overflow-x-auto max-h-48">
                  {JSON.stringify(selectedRun.output_payload || selectedRun.input_payload, null, 2)}
                </div>
              </div>
            </>
          ) : (
            <p className="text-xs text-slate-500 py-12 text-center">Select an agent execution run on the left to inspect details.</p>
          )}
        </div>
      </div>
    </div>
  );
};
