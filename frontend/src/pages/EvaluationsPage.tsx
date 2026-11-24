/**
 * Page 8: AI Evaluation Framework with RAGAS/DeepEval metrics, benchmark datasets, and run comparison.
 */
import React, { useState, useEffect } from 'react';
import {
  BarChart2,
  CheckCircle2,
  AlertCircle,
  Play,
  RotateCw,
  TrendingUp,
  Layers
} from 'lucide-react';
import { api } from '../api/endpoints';
import { useAuth } from '../context/AuthContext';

export const EvaluationsPage: React.FC = () => {
  const { activeWorkspace } = useAuth();
  const [datasets, setDatasets] = useState<any[]>([]);
  const [evalRuns, setEvalRuns] = useState<any[]>([]);
  const [selectedRun, setSelectedRun] = useState<any | null>(null);
  const [isRunning, setIsRunning] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  const fetchEvalData = async () => {
    setIsLoading(true);
    try {
      const [dsList, runList] = await Promise.all([
        api.listEvalDatasets(),
        api.listEvalRuns(),
      ]);
      setDatasets(dsList);
      setEvalRuns(runList);
      if (runList.length > 0 && !selectedRun) {
        setSelectedRun(runList[0]);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchEvalData();
  }, [activeWorkspace?.id]);

  const handleTriggerRun = async () => {
    if (datasets.length === 0) return;
    setIsRunning(true);
    try {
      const run = await api.triggerEvalRun({
        dataset_id: datasets[0].id,
        model_name: 'gpt-4o',
      });
      setEvalRuns([run, ...evalRuns]);
      setSelectedRun(run);
    } catch (err: any) {
      alert(`Evaluation failed: ${err.message}`);
    } finally {
      setIsRunning(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">AI Evaluation Framework</h1>
          <p className="text-sm text-slate-400">RAGAS and DeepEval metrics tracking faithfulness, relevance, precision, recall, and hallucination rates.</p>
        </div>
        <button
          onClick={handleTriggerRun}
          disabled={isRunning || datasets.length === 0}
          className="px-4 py-2.5 rounded-lg bg-blue-600 hover:bg-blue-500 font-semibold text-white text-xs flex items-center gap-2 shadow-lg shadow-blue-600/20 disabled:opacity-40 transition-all self-start sm:self-auto"
        >
          <Play className={`w-3.5 h-3.5 ${isRunning ? 'animate-spin' : ''}`} />
          {isRunning ? 'Evaluating Benchmark Suite...' : 'Run Benchmark Evaluation'}
        </button>
      </div>

      {/* Core Metrics Cards (Based on selected run) */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div className="p-4 rounded-xl bg-slate-900 border border-slate-800">
          <span className="text-[10px] font-semibold uppercase text-slate-400">Faithfulness</span>
          <p className="text-2xl font-bold text-emerald-400 mt-1">
            {selectedRun ? `${Math.round(selectedRun.faithfulness * 100)}%` : '--'}
          </p>
          <p className="text-[10px] text-slate-500 mt-1">Groundedness in source context</p>
        </div>

        <div className="p-4 rounded-xl bg-slate-900 border border-slate-800">
          <span className="text-[10px] font-semibold uppercase text-slate-400">Answer Relevance</span>
          <p className="text-2xl font-bold text-blue-400 mt-1">
            {selectedRun ? `${Math.round(selectedRun.answer_relevance * 100)}%` : '--'}
          </p>
          <p className="text-[10px] text-slate-500 mt-1">Semantic intent alignment</p>
        </div>

        <div className="p-4 rounded-xl bg-slate-900 border border-slate-800">
          <span className="text-[10px] font-semibold uppercase text-slate-400">Context Recall</span>
          <p className="text-2xl font-bold text-indigo-400 mt-1">
            {selectedRun ? `${Math.round(selectedRun.context_recall * 100)}%` : '--'}
          </p>
          <p className="text-[10px] text-slate-500 mt-1">Ground truth concept capture</p>
        </div>

        <div className="p-4 rounded-xl bg-slate-900 border border-slate-800">
          <span className="text-[10px] font-semibold uppercase text-slate-400">Citation Accuracy</span>
          <p className="text-2xl font-bold text-purple-400 mt-1">
            {selectedRun ? `${Math.round(selectedRun.citation_correctness * 100)}%` : '--'}
          </p>
          <p className="text-[10px] text-slate-500 mt-1">Verifiable citation mappings</p>
        </div>
      </div>

      {/* Runs History and Sample Breakdown */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Past Runs */}
        <div className="p-4 rounded-2xl bg-slate-900 border border-slate-800 space-y-3">
          <h2 className="text-xs font-bold text-slate-400 uppercase tracking-wider">Evaluation History</h2>
          <div className="space-y-2 max-h-[500px] overflow-y-auto pr-1">
            {evalRuns.length === 0 ? (
              <p className="text-xs text-slate-500 py-8 text-center">No evaluation runs recorded. Click "Run Benchmark Evaluation" to start.</p>
            ) : (
              evalRuns.map((run) => (
                <div
                  key={run.id}
                  onClick={() => setSelectedRun(run)}
                  className={`p-3 rounded-xl border cursor-pointer transition-all ${
                    selectedRun?.id === run.id
                      ? 'bg-blue-600/10 border-blue-500 text-white shadow-md'
                      : 'bg-slate-950/60 border-slate-800 hover:border-slate-700 text-slate-300'
                  }`}
                >
                  <div className="flex items-center justify-between text-xs font-bold">
                    <span>Model: {run.model_name}</span>
                    <span className="text-emerald-400">{Math.round(run.faithfulness * 100)}% Faithfulness</span>
                  </div>
                  <div className="flex items-center justify-between text-[10px] text-slate-500 mt-2">
                    <span>Latency: {run.avg_latency_ms} ms</span>
                    <span>{new Date(run.created_at).toLocaleDateString()}</span>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Detailed Per-Sample Inspection */}
        <div className="lg:col-span-2 p-6 rounded-2xl bg-slate-900 border border-slate-800 space-y-4">
          <h2 className="text-xs font-bold text-slate-400 uppercase tracking-wider">
            Benchmark Test Case Breakdown
          </h2>

          {selectedRun?.detailed_results && selectedRun.detailed_results.length > 0 ? (
            <div className="space-y-3 max-h-[550px] overflow-y-auto pr-2">
              {selectedRun.detailed_results.map((res: any, idx: number) => (
                <div key={idx} className="p-4 rounded-xl bg-slate-950/80 border border-slate-800 text-xs space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-white text-xs">{res.query}</span>
                    <span
                      className={`text-[10px] font-bold px-2 py-0.5 rounded ${
                        res.metrics?.passed ? 'bg-emerald-500/10 text-emerald-400' : 'bg-rose-500/10 text-rose-400'
                      }`}
                    >
                      {res.metrics?.passed ? 'PASSED' : 'NEEDS_REVISION'}
                    </span>
                  </div>

                  <p className="text-slate-400 text-[11px]">
                    <strong className="text-slate-300">Ground Truth:</strong> {res.ground_truth}
                  </p>

                  <p className="text-slate-300 text-[11px] p-2 rounded bg-slate-900 border border-slate-800">
                    <strong className="text-blue-400">Generated:</strong> {res.generated_answer}
                  </p>

                  <div className="flex flex-wrap gap-3 text-[10px] text-slate-400 pt-1">
                    <span>Faithfulness: <strong className="text-white">{Math.round((res.metrics?.faithfulness || 0) * 100)}%</strong></span>
                    <span>Relevance: <strong className="text-white">{Math.round((res.metrics?.answer_relevance || 0) * 100)}%</strong></span>
                    <span>Context Precision: <strong className="text-white">{Math.round((res.metrics?.context_precision || 0) * 100)}%</strong></span>
                    <span>Latency: <strong className="text-white">{res.metrics?.latency_ms} ms</strong></span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-xs text-slate-500 py-12 text-center">Run an evaluation benchmark to inspect per-sample metrics.</p>
          )}
        </div>
      </div>
    </div>
  );
};
