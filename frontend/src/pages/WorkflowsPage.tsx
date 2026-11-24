/**
 * Page 6: Autonomous Business Workflows Catalog & Execution Runner.
 */
import React, { useState, useEffect } from 'react';
import {
  GitBranch,
  Play,
  CheckCircle2,
  Clock,
  Files,
  FileText,
  AlertCircle,
  X
} from 'lucide-react';
import { api, DocumentItem } from '../api/endpoints';
import { useAuth } from '../context/AuthContext';

export const WorkflowsPage: React.FC = () => {
  const { activeWorkspace } = useAuth();
  const [workflows, setWorkflows] = useState<any[]>([]);
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [selectedWorkflow, setSelectedWorkflow] = useState<any | null>(null);
  const [selectedDocIds, setSelectedDocIds] = useState<string[]>([]);
  const [customInstructions, setCustomInstructions] = useState('');
  const [isExecuting, setIsExecuting] = useState(false);
  const [executionResult, setExecutionResult] = useState<any | null>(null);

  useEffect(() => {
    const init = async () => {
      try {
        const [wfList, docRes] = await Promise.all([
          api.listWorkflows(),
          api.listDocuments({ limit: 50 }),
        ]);
        setWorkflows(wfList);
        setDocuments(Array.isArray(docRes) ? docRes : (docRes?.items || []));
      } catch (err) {
        console.error(err);
      }
    };
    init();
  }, [activeWorkspace?.id]);

  const handleTrigger = async () => {
    if (!selectedWorkflow || selectedDocIds.length === 0) {
      alert('Please select at least one document to analyze');
      return;
    }
    setIsExecuting(true);
    setExecutionResult(null);

    try {
      const res = await api.executeWorkflow({
        workflow_id: selectedWorkflow.id,
        document_ids: selectedDocIds,
        custom_instructions: customInstructions,
      });
      setExecutionResult(res);
    } catch (err: any) {
      alert(`Workflow execution error: ${err.message}`);
    } finally {
      setIsExecuting(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight">Autonomous Business Workflows</h1>
        <p className="text-sm text-slate-400">Preconfigured multi-agent pipelines for PRD gap analysis, financial audits, and compliance checks.</p>
      </div>

      {/* Workflows Catalog Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {workflows.map((wf) => (
          <div
            key={wf.id}
            className={`p-6 rounded-2xl border transition-all flex flex-col justify-between shadow-sm ${
              selectedWorkflow?.id === wf.id
                ? 'bg-blue-600/10 border-blue-500 shadow-blue-500/10'
                : 'bg-slate-900 border-slate-800 hover:border-slate-700'
            }`}
          >
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20">
                  {wf.category}
                </span>
                <span className="text-xs text-slate-500 flex items-center gap-1">
                  <Clock className="w-3 h-3" /> {wf.estimated_duration}
                </span>
              </div>
              <h3 className="font-bold text-base text-white">{wf.name}</h3>
              <p className="text-xs text-slate-400 leading-relaxed">{wf.description}</p>
              
              <div className="space-y-1.5 pt-2">
                <p className="text-[10px] font-semibold uppercase text-slate-500">Pipeline Stages:</p>
                {wf.steps.map((st: string, idx: number) => (
                  <div key={idx} className="flex items-center gap-2 text-xs text-slate-300">
                    <CheckCircle2 className="w-3 h-3 text-blue-400 shrink-0" />
                    <span>{st}</span>
                  </div>
                ))}
              </div>
            </div>

            <button
              onClick={() => {
                setSelectedWorkflow(wf);
                setExecutionResult(null);
              }}
              className={`mt-6 w-full py-2.5 rounded-lg text-xs font-semibold flex items-center justify-center gap-2 transition-all ${
                selectedWorkflow?.id === wf.id
                  ? 'bg-blue-600 text-white shadow-md'
                  : 'bg-slate-800 hover:bg-slate-700 text-slate-200'
              }`}
            >
              <Play className="w-3.5 h-3.5" /> Select Workflow
            </button>
          </div>
        ))}
      </div>

      {/* Execution Configuration Pane */}
      {selectedWorkflow && (
        <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 space-y-5 shadow-xl">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <div>
              <h3 className="font-bold text-white text-base">Configure: {selectedWorkflow.name}</h3>
              <p className="text-xs text-slate-400">Select target documents and provide optional custom focus parameters.</p>
            </div>
            <button onClick={() => setSelectedWorkflow(null)} className="text-slate-400 hover:text-white">
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Document Picker */}
          <div className="space-y-2">
            <label className="text-xs font-semibold text-slate-400">Select Input Documents ({selectedDocIds.length} selected)</label>
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-2 max-h-48 overflow-y-auto p-1">
              {documents.map((doc) => {
                const isSelected = selectedDocIds.includes(doc.id);
                return (
                  <div
                    key={doc.id}
                    onClick={() => {
                      setSelectedDocIds(
                        isSelected ? selectedDocIds.filter((id) => id !== doc.id) : [...selectedDocIds, doc.id]
                      );
                    }}
                    className={`p-2.5 rounded-lg border text-xs cursor-pointer flex items-center gap-2 transition-all ${
                      isSelected
                        ? 'bg-blue-600/20 border-blue-500 text-white font-semibold'
                        : 'bg-slate-800/60 border-slate-700/60 text-slate-300 hover:bg-slate-800'
                    }`}
                  >
                    <Files className="w-4 h-4 text-blue-400 shrink-0" />
                    <span className="truncate">{doc.title}</span>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Custom Instructions */}
          <div className="space-y-2">
            <label className="text-xs font-semibold text-slate-400">Custom Focus / Parameters (Optional)</label>
            <textarea
              rows={3}
              value={customInstructions}
              onChange={(e) => setCustomInstructions(e.target.value)}
              placeholder="E.g., Focus specifically on missing latency constraints and concurrent user scaling edge cases..."
              className="w-full p-3 rounded-lg bg-slate-800/80 border border-slate-700 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
            />
          </div>

          <button
            onClick={handleTrigger}
            disabled={isExecuting || selectedDocIds.length === 0}
            className="px-6 py-2.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white font-semibold text-xs flex items-center gap-2 disabled:opacity-40 transition-all shadow-md"
          >
            {isExecuting ? (
              <>
                <Clock className="w-4 h-4 animate-spin" /> Executing Multi-Agent Pipeline...
              </>
            ) : (
              <>
                <Play className="w-4 h-4" /> Run Autonomous Workflow
              </>
            )}
          </button>

          {/* Execution Result Banner */}
          {executionResult && (
            <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-xs text-slate-200 space-y-2">
              <div className="flex items-center gap-2 font-bold text-emerald-400">
                <CheckCircle2 className="w-4 h-4" /> Workflow Executed Successfully in {executionResult.duration_ms} ms!
              </div>
              <p>Generated report: <strong className="text-white">{executionResult.report_title}</strong></p>
              <a
                href={`/reports`}
                className="inline-block mt-1 font-semibold text-blue-400 hover:underline"
              >
                View Full Report & Analysis &rarr;
              </a>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
