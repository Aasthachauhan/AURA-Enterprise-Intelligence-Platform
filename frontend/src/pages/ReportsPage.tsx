/**
 * Page 7: Comprehensive Intelligence Reports Library & Report Reader.
 */
import React, { useState, useEffect } from 'react';
import {
  FileText,
  Download,
  Trash2,
  Bookmark,
  CheckCircle2,
  AlertTriangle,
  Plus,
  X
} from 'lucide-react';
import { api, ReportItem, DocumentItem } from '../api/endpoints';
import { useAuth } from '../context/AuthContext';

export const ReportsPage: React.FC = () => {
  const { activeWorkspace } = useAuth();
  const [reports, setReports] = useState<ReportItem[]>([]);
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [selectedReport, setSelectedReport] = useState<ReportItem | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  
  // Generator wizard modal state
  const [isWizardOpen, setIsWizardOpen] = useState(false);
  const [wizardTitle, setWizardTitle] = useState('Product Requirements & QA Assessment');
  const [wizardFocus, setWizardFocus] = useState('Analyze product requirements, test coverage, and release risks.');
  const [wizardDocIds, setWizardDocIds] = useState<string[]>([]);
  const [isGenerating, setIsGenerating] = useState(false);

  const fetchReports = async () => {
    setIsLoading(true);
    try {
      const [repList, docRes] = await Promise.all([
        api.listReports(),
        api.listDocuments({ limit: 50 }),
      ]);
      setReports(repList);
      setDocuments(Array.isArray(docRes) ? docRes : (docRes?.items || []));
      if (repList.length > 0 && !selectedReport) {
        setSelectedReport(repList[0]);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchReports();
  }, [activeWorkspace?.id]);

  const handleGenerate = async () => {
    if (wizardDocIds.length === 0) {
      alert('Please select at least one document');
      return;
    }
    setIsGenerating(true);
    try {
      const rep = await api.generateReport({
        title: wizardTitle,
        report_type: 'qa_assessment',
        document_ids: wizardDocIds,
        query_or_focus: wizardFocus,
      });
      setReports([rep, ...reports]);
      setSelectedReport(rep);
      setIsWizardOpen(false);
    } catch (err: any) {
      alert(`Report generation error: ${err.message}`);
    } finally {
      setIsGenerating(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Delete this report?')) return;
    try {
      await api.deleteReport(id);
      const remaining = reports.filter((r) => r.id !== id);
      setReports(remaining);
      if (selectedReport?.id === id) {
        setSelectedReport(remaining[0] || null);
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleDownloadMarkdown = (report: ReportItem) => {
    const blob = new Blob([report.markdown_content], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${report.title.replace(/\s+/g, '_')}.md`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Intelligence Reports</h1>
          <p className="text-sm text-slate-400">Evidence-backed executive briefs, gap assessments, and cross-document comparison reports.</p>
        </div>
        <button
          onClick={() => setIsWizardOpen(true)}
          className="px-4 py-2.5 rounded-lg bg-blue-600 hover:bg-blue-500 font-medium text-white text-sm flex items-center gap-2 shadow-lg shadow-blue-600/20 transition-all self-start sm:self-auto"
        >
          <Plus className="w-4 h-4" /> Generate New Report
        </button>
      </div>

      {/* Main Split Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Reports Index Sidebar */}
        <div className="p-4 rounded-2xl bg-slate-900 border border-slate-800 space-y-3">
          <h2 className="text-xs font-bold text-slate-400 uppercase tracking-wider">Reports Library</h2>
          <div className="space-y-2 overflow-y-auto max-h-[600px] pr-1">
            {reports.length === 0 ? (
              <p className="text-xs text-slate-500 py-8 text-center">No reports generated yet.</p>
            ) : (
              reports.map((r) => (
                <div
                  key={r.id}
                  onClick={() => setSelectedReport(r)}
                  className={`p-3 rounded-xl border cursor-pointer transition-all ${
                    selectedReport?.id === r.id
                      ? 'bg-blue-600/10 border-blue-500/80 shadow-md'
                      : 'bg-slate-950/60 border-slate-800 hover:border-slate-700'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-xs text-white truncate max-w-[180px]">{r.title}</span>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDelete(r.id);
                      }}
                      className="text-slate-500 hover:text-rose-400 p-1"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                  <p className="text-[11px] text-slate-400 mt-1 line-clamp-2">{r.executive_summary}</p>
                  <div className="flex items-center justify-between text-[10px] text-slate-500 mt-2">
                    <span className="capitalize">{r.report_type.replace('_', ' ')}</span>
                    <span>{new Date(r.created_at).toLocaleDateString()}</span>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Report Reader Pane */}
        <div className="lg:col-span-2 p-6 rounded-2xl bg-slate-900 border border-slate-800 space-y-6">
          {selectedReport ? (
            <>
              <div className="flex items-center justify-between border-b border-slate-800 pb-4">
                <div>
                  <h2 className="text-xl font-bold text-white">{selectedReport.title}</h2>
                  <p className="text-xs text-slate-400 mt-1">Generated: {new Date(selectedReport.created_at).toLocaleString()}</p>
                </div>
                <button
                  onClick={() => handleDownloadMarkdown(selectedReport)}
                  className="px-3 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-slate-200 flex items-center gap-2 border border-slate-700 transition-colors"
                >
                  <Download className="w-3.5 h-3.5" /> Export Markdown
                </button>
              </div>

              {/* Executive Summary */}
              <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800 space-y-2">
                <h3 className="text-xs font-bold text-blue-400 uppercase tracking-wider">Executive Summary</h3>
                <p className="text-xs text-slate-300 leading-relaxed">{selectedReport.executive_summary}</p>
              </div>

              {/* Markdown Body */}
              <div className="p-5 rounded-xl bg-slate-950/60 border border-slate-800/80 text-xs text-slate-200 font-mono whitespace-pre-wrap leading-relaxed max-h-[450px] overflow-y-auto">
                {selectedReport.markdown_content}
              </div>

              {/* Citations Panel */}
              {selectedReport.citations && selectedReport.citations.length > 0 && (
                <div className="space-y-2">
                  <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
                    <Bookmark className="w-3.5 h-3.5 text-blue-400" /> Source Citations
                  </h4>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                    {selectedReport.citations.map((c, i) => (
                      <div key={i} className="p-2.5 rounded-lg bg-slate-950/80 border border-slate-800 text-xs">
                        <p className="font-semibold text-white">{c.document_title}</p>
                        <p className="text-[11px] text-slate-400 italic mt-0.5">"{c.excerpt}"</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </>
          ) : (
            <p className="text-xs text-slate-500 py-12 text-center">Select a report from the list to view its contents.</p>
          )}
        </div>
      </div>

      {/* Generator Wizard Modal */}
      {isWizardOpen && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="w-full max-w-lg bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl p-6 space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h3 className="font-bold text-white text-base">Generate Intelligence Report</h3>
              <button onClick={() => setIsWizardOpen(false)} className="text-slate-400 hover:text-white">
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="space-y-3">
              <div>
                <label className="text-xs font-semibold text-slate-400">Report Title</label>
                <input
                  type="text"
                  value={wizardTitle}
                  onChange={(e) => setWizardTitle(e.target.value)}
                  className="w-full mt-1 p-2.5 rounded-lg bg-slate-800 border border-slate-700 text-xs text-white"
                />
              </div>

              <div>
                <label className="text-xs font-semibold text-slate-400">Analysis Focus / Prompt</label>
                <textarea
                  rows={3}
                  value={wizardFocus}
                  onChange={(e) => setWizardFocus(e.target.value)}
                  className="w-full mt-1 p-2.5 rounded-lg bg-slate-800 border border-slate-700 text-xs text-white"
                />
              </div>

              <div>
                <label className="text-xs font-semibold text-slate-400">Select Source Documents ({wizardDocIds.length} selected)</label>
                <div className="mt-1 space-y-1.5 max-h-36 overflow-y-auto">
                  {documents.map((d) => (
                    <label key={d.id} className="flex items-center gap-2 text-xs text-slate-300 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={wizardDocIds.includes(d.id)}
                        onChange={(e) => {
                          setWizardDocIds(
                            e.target.checked ? [...wizardDocIds, d.id] : wizardDocIds.filter((id) => id !== d.id)
                          );
                        }}
                        className="rounded border-slate-700 bg-slate-800 text-blue-600"
                      />
                      <span className="truncate">{d.title}</span>
                    </label>
                  ))}
                </div>
              </div>
            </div>

            <button
              onClick={handleGenerate}
              disabled={isGenerating || wizardDocIds.length === 0}
              className="w-full py-2.5 rounded-lg bg-blue-600 hover:bg-blue-500 font-semibold text-white text-xs disabled:opacity-40 transition-all shadow-md"
            >
              {isGenerating ? 'Generating Evidence-Backed Report...' : 'Generate Report'}
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
