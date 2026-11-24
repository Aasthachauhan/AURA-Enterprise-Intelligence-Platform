/**
 * Page 3: Document Management System with drag-and-drop, multi-file upload, preview & retry.
 */
import React, { useState, useEffect } from 'react';
import {
  Upload,
  Files,
  Search,
  Filter,
  CheckCircle2,
  AlertCircle,
  Clock,
  Trash2,
  RotateCw,
  Eye,
  X,
  FileText
} from 'lucide-react';
import { api, DocumentItem, DocumentChunk } from '../api/endpoints';
import { useAuth } from '../context/AuthContext';

export const DocumentsPage: React.FC = () => {
  const { activeWorkspace } = useAuth();
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('all');
  const [statusFilter, setStatusFilter] = useState('all');
  
  // Upload modal state
  const [isUploadOpen, setIsUploadOpen] = useState(false);
  const [isDragging, setIsDragging] = useState(false);
  const [uploadCategory, setUploadCategory] = useState('General');
  const [uploadingFiles, setUploadingFiles] = useState(false);
  
  // Preview modal state
  const [previewDoc, setPreviewDoc] = useState<DocumentItem | null>(null);
  const [previewChunks, setPreviewChunks] = useState<DocumentChunk[]>([]);
  const [isLoadingPreview, setIsLoadingPreview] = useState(false);

  const fetchDocuments = async () => {
    setIsLoading(true);
    try {
      const res = await api.listDocuments({
        search: search || undefined,
        category: categoryFilter !== 'all' ? categoryFilter : undefined,
        status: statusFilter !== 'all' ? statusFilter : undefined,
      });
      setDocuments(Array.isArray(res) ? res : (res?.items || []));
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchDocuments();
  }, [categoryFilter, statusFilter, activeWorkspace?.id]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    fetchDocuments();
  };

  const handleFileUpload = async (files: FileList | null) => {
    if (!files || files.length === 0) return;
    setUploadingFiles(true);
    const formData = new FormData();
    for (let i = 0; i < files.length; i++) {
      formData.append('files', files[i]);
    }
    formData.append('category', uploadCategory);

    try {
      await api.uploadBatch(formData);
      setIsUploadOpen(false);
      await fetchDocuments();
    } catch (err: any) {
      alert(`Upload error: ${err.message}`);
    } finally {
      setUploadingFiles(false);
    }
  };

  const handleReprocess = async (id: string) => {
    try {
      await api.reprocessDocument(id);
      fetchDocuments();
    } catch (err) {
      console.error(err);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to delete this document?')) return;
    try {
      await api.deleteDocument(id);
      setDocuments(documents.filter((d) => d.id !== id));
    } catch (err) {
      console.error(err);
    }
  };

  const handleOpenPreview = async (doc: DocumentItem) => {
    setPreviewDoc(doc);
    setIsLoadingPreview(true);
    try {
      const chunks = await api.getDocumentPreview(doc.id, 15);
      setPreviewChunks(chunks);
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoadingPreview(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Document Management</h1>
          <p className="text-sm text-slate-400">Upload, parse, normalize, and index business documents into the RAG vector store.</p>
        </div>
        <button
          onClick={() => setIsUploadOpen(true)}
          className="px-4 py-2.5 rounded-lg bg-blue-600 hover:bg-blue-500 font-medium text-white text-sm flex items-center gap-2 shadow-lg shadow-blue-600/20 transition-all self-start sm:self-auto"
        >
          <Upload className="w-4 h-4" /> Upload Documents
        </button>
      </div>

      {/* Filter and Search Bar */}
      <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 flex flex-col sm:flex-row gap-3 items-center justify-between">
        <form onSubmit={handleSearchSubmit} className="relative w-full sm:w-80">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search by title or filename..."
            className="w-full pl-9 pr-4 py-2 rounded-lg bg-slate-800/80 border border-slate-700 text-xs text-slate-200 placeholder-slate-400 focus:outline-none focus:ring-1 focus:ring-blue-500"
          />
        </form>

        <div className="flex items-center gap-3 w-full sm:w-auto">
          <select
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value)}
            className="px-3 py-2 rounded-lg bg-slate-800 border border-slate-700 text-xs text-slate-300"
          >
            <option value="all">All Categories</option>
            <option value="General">General</option>
            <option value="Requirements">Requirements</option>
            <option value="QA & Testing">QA & Testing</option>
            <option value="Finance">Finance</option>
            <option value="Legal">Legal</option>
          </select>

          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-3 py-2 rounded-lg bg-slate-800 border border-slate-700 text-xs text-slate-300"
          >
            <option value="all">All Statuses</option>
            <option value="completed">Completed</option>
            <option value="processing">Processing</option>
            <option value="failed">Failed</option>
          </select>
        </div>
      </div>

      {/* Document Table */}
      <div className="rounded-xl bg-slate-900 border border-slate-800 overflow-hidden shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-950/60 border-b border-slate-800 text-slate-400 uppercase tracking-wider font-semibold">
              <tr>
                <th className="py-3 px-4">Document Title</th>
                <th className="py-3 px-4">Category</th>
                <th className="py-3 px-4">Type</th>
                <th className="py-3 px-4">Size</th>
                <th className="py-3 px-4">Chunks</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/80">
              {documents.length === 0 ? (
                <tr>
                  <td colSpan={7} className="py-8 text-center text-slate-500">
                    No documents found. Click "Upload Documents" to begin.
                  </td>
                </tr>
              ) : (
                documents.map((doc) => (
                  <tr key={doc.id} className="hover:bg-slate-800/40 transition-colors">
                    <td className="py-3 px-4 font-semibold text-slate-200">
                      <div className="flex items-center gap-2">
                        <FileText className="w-4 h-4 text-blue-400 shrink-0" />
                        <span className="truncate max-w-xs">{doc.title}</span>
                      </div>
                    </td>
                    <td className="py-3 px-4 text-slate-400">{doc.category}</td>
                    <td className="py-3 px-4">
                      <span className="px-2 py-0.5 rounded uppercase font-bold text-[10px] bg-slate-800 text-slate-300 border border-slate-700">
                        {doc.file_type}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-slate-400">{Math.round(doc.file_size_bytes / 1024)} KB</td>
                    <td className="py-3 px-4 text-slate-400">{doc.chunk_count}</td>
                    <td className="py-3 px-4">
                      {doc.status === 'completed' && (
                        <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 flex items-center gap-1 w-fit">
                          <CheckCircle2 className="w-3 h-3" /> Indexed
                        </span>
                      )}
                      {doc.status === 'processing' && (
                        <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-blue-500/10 text-blue-400 border border-blue-500/20 flex items-center gap-1 w-fit">
                          <Clock className="w-3 h-3 animate-spin" /> Ingestion
                        </span>
                      )}
                      {doc.status === 'failed' && (
                        <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-rose-500/10 text-rose-400 border border-rose-500/20 flex items-center gap-1 w-fit" title={doc.error_message}>
                          <AlertCircle className="w-3 h-3" /> Failed
                        </span>
                      )}
                    </td>
                    <td className="py-3 px-4 text-right">
                      <div className="flex items-center justify-end gap-2">
                        <button
                          onClick={() => handleOpenPreview(doc)}
                          className="p-1 hover:text-blue-400 transition-colors"
                          title="Preview Chunks"
                        >
                          <Eye className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => handleReprocess(doc.id)}
                          className="p-1 hover:text-emerald-400 transition-colors"
                          title="Retry / Reprocess"
                        >
                          <RotateCw className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => handleDelete(doc.id)}
                          className="p-1 hover:text-rose-400 transition-colors"
                          title="Delete"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Upload Modal */}
      {isUploadOpen && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="w-full max-w-lg bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl p-6 space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h3 className="font-bold text-white text-base">Upload Documents</h3>
              <button onClick={() => setIsUploadOpen(false)} className="text-slate-400 hover:text-white">
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="space-y-2">
              <label className="text-xs font-semibold text-slate-400">Document Category</label>
              <select
                value={uploadCategory}
                onChange={(e) => setUploadCategory(e.target.value)}
                className="w-full px-3 py-2 rounded-lg bg-slate-800 border border-slate-700 text-xs text-slate-200"
              >
                <option value="General">General</option>
                <option value="Requirements">Requirements (PRD / Specs)</option>
                <option value="QA & Testing">QA & Testing Coverage</option>
                <option value="Finance">Finance & Spreadsheets</option>
                <option value="Legal">Legal & Contracts</option>
              </select>
            </div>

            {/* Drag & Drop Box */}
            <div
              onDragOver={(e) => {
                e.preventDefault();
                setIsDragging(true);
              }}
              onDragLeave={() => setIsDragging(false)}
              onDrop={(e) => {
                e.preventDefault();
                setIsDragging(false);
                handleFileUpload(e.dataTransfer.files);
              }}
              className={`border-2 border-dashed rounded-xl p-8 text-center transition-all ${
                isDragging ? 'border-blue-500 bg-blue-500/10' : 'border-slate-700 bg-slate-950/40 hover:border-slate-600'
              }`}
            >
              <Upload className="w-8 h-8 text-slate-400 mx-auto mb-2" />
              <p className="text-xs font-semibold text-slate-200">Drag and drop documents here</p>
              <p className="text-[10px] text-slate-500 mt-1">Supports PDF, DOCX, XLSX, CSV, TXT, MD, HTML (up to 50MB)</p>
              <input
                type="file"
                multiple
                id="file-input"
                className="hidden"
                onChange={(e) => handleFileUpload(e.target.files)}
              />
              <label
                htmlFor="file-input"
                className="mt-4 inline-block px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-medium text-white cursor-pointer transition-colors"
              >
                {uploadingFiles ? 'Uploading & Ingesting...' : 'Browse Local Files'}
              </label>
            </div>
          </div>
        </div>
      )}

      {/* Document Chunk Preview Modal */}
      {previewDoc && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="w-full max-w-2xl bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl p-6 space-y-4 max-h-[85vh] flex flex-col">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div>
                <h3 className="font-bold text-white text-base">{previewDoc.title}</h3>
                <p className="text-xs text-slate-400">Indexed Chunks & Semantic Metadata</p>
              </div>
              <button onClick={() => setPreviewDoc(null)} className="text-slate-400 hover:text-white">
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="flex-1 overflow-y-auto space-y-3 pr-2">
              {isLoadingPreview ? (
                <p className="text-xs text-slate-400 text-center py-8">Loading document chunks...</p>
              ) : previewChunks.length === 0 ? (
                <p className="text-xs text-slate-500 text-center py-8">No chunk records found.</p>
              ) : (
                previewChunks.map((chunk) => (
                  <div key={chunk.id} className="p-3 rounded-lg bg-slate-950/80 border border-slate-800 text-xs space-y-1">
                    <div className="flex items-center justify-between text-[10px] text-blue-400 font-semibold uppercase">
                      <span>Chunk #{chunk.chunk_index + 1}</span>
                      <span>
                        {chunk.page_number ? `Page ${chunk.page_number}` : chunk.sheet_name ? `Sheet: ${chunk.sheet_name}` : chunk.section_title || ''}
                      </span>
                    </div>
                    <p className="text-slate-300 font-mono text-[11px] whitespace-pre-wrap">{chunk.content}</p>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
