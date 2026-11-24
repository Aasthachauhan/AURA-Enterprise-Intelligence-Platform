/**
 * Page 10: MCP Server Integrations & Interactive Tool Tester.
 */
import React, { useState, useEffect } from 'react';
import {
  Cpu,
  CheckCircle2,
  Play,
  Terminal,
  ShieldCheck,
  RefreshCw,
  Zap
} from 'lucide-react';
import { api } from '../api/endpoints';

export const IntegrationsPage: React.FC = () => {
  const [tools, setTools] = useState<any[]>([]);
  const [selectedTool, setSelectedTool] = useState<any | null>(null);
  const [toolArgs, setToolArgs] = useState('{"query": "PRD requirements"}');
  const [testResult, setTestResult] = useState<any | null>(null);
  const [isExecuting, setIsExecuting] = useState(false);

  useEffect(() => {
    api.listMCPTools().then((t) => {
      setTools(t);
      if (t.length > 0) setSelectedTool(t[0]);
    }).catch(console.error);
  }, []);

  const handleTestTool = async () => {
    if (!selectedTool) return;
    setIsExecuting(true);
    setTestResult(null);
    try {
      const parsedArgs = JSON.parse(toolArgs);
      const res = await api.executeMCPTool(selectedTool.name, parsedArgs);
      setTestResult(res);
    } catch (err: any) {
      setTestResult({ error: err.message });
    } finally {
      setIsExecuting(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight">MCP & External Integrations</h1>
        <p className="text-sm text-slate-400">Configure local Model Context Protocol tools, security boundaries, and live execution testbeds.</p>
      </div>

      {/* Status Card */}
      <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-blue-500/10 flex items-center justify-center text-blue-400">
            <Cpu className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-sm font-bold text-white">Local MCP Server: Active</h2>
            <p className="text-xs text-slate-400">Protocol: JSON-RPC 2.0 • Standard IO & REST Interface</p>
          </div>
        </div>
        <span className="px-3 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 flex items-center gap-1.5">
          <CheckCircle2 className="w-3.5 h-3.5" /> 6 Tools Registered
        </span>
      </div>

      {/* Tool Catalog & Interactive Tester */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Tool List */}
        <div className="p-4 rounded-2xl bg-slate-900 border border-slate-800 space-y-2">
          <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Registered MCP Tools</h3>
          {tools.map((t) => (
            <div
              key={t.name}
              onClick={() => {
                setSelectedTool(t);
                setTestResult(null);
                setToolArgs(JSON.stringify(t.input_schema.properties ? Object.fromEntries(Object.keys(t.input_schema.properties).map(k => [k, ""])) : {}, null, 2));
              }}
              className={`p-3 rounded-xl border text-xs cursor-pointer transition-all ${
                selectedTool?.name === t.name
                  ? 'bg-blue-600/10 border-blue-500 text-white font-semibold'
                  : 'bg-slate-950/60 border-slate-800 hover:border-slate-700 text-slate-300'
              }`}
            >
              <div className="flex items-center justify-between">
                <span>{t.name}</span>
                <span className="text-[10px] text-blue-400">MCP</span>
              </div>
              <p className="text-[11px] text-slate-400 font-normal mt-1 line-clamp-1">{t.description}</p>
            </div>
          ))}
        </div>

        {/* Interactive Runner Pane */}
        <div className="lg:col-span-2 p-6 rounded-2xl bg-slate-900 border border-slate-800 space-y-4">
          {selectedTool ? (
            <>
              <div>
                <h3 className="font-bold text-white text-base font-mono">{selectedTool.name}</h3>
                <p className="text-xs text-slate-400 mt-0.5">{selectedTool.description}</p>
              </div>

              <div className="space-y-2">
                <label className="text-xs font-semibold text-slate-400 flex items-center justify-between">
                  <span>Input Arguments (JSON)</span>
                  <span className="text-[10px] text-slate-500">JSON Schema Validated</span>
                </label>
                <textarea
                  rows={4}
                  value={toolArgs}
                  onChange={(e) => setToolArgs(e.target.value)}
                  className="w-full p-3 rounded-lg bg-slate-950 border border-slate-800 text-xs font-mono text-slate-200 focus:outline-none focus:ring-1 focus:ring-blue-500"
                />
              </div>

              <button
                onClick={handleTestTool}
                disabled={isExecuting}
                className="px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold flex items-center gap-2 shadow-md transition-all"
              >
                <Play className="w-3.5 h-3.5" /> {isExecuting ? 'Executing...' : 'Execute Tool'}
              </button>

              {testResult && (
                <div className="space-y-2 pt-2">
                  <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
                    <Terminal className="w-3.5 h-3.5 text-blue-400" /> Output Result
                  </h4>
                  <pre className="p-4 rounded-xl bg-slate-950 border border-slate-800 text-xs font-mono text-emerald-400 overflow-x-auto max-h-56">
                    {JSON.stringify(testResult, null, 2)}
                  </pre>
                </div>
              )}
            </>
          ) : null}
        </div>
      </div>
    </div>
  );
};
