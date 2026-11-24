/**
 * Strongly-typed API client service methods.
 */
import { apiRequest } from './client';

export interface User {
  id: string;
  email: string;
  full_name: string;
  role: string;
  avatar_url?: string;
}

export interface Workspace {
  id: string;
  name: string;
  description?: string;
  is_default: boolean;
  document_count: number;
}

export interface DocumentItem {
  id: string;
  workspace_id: string;
  title: string;
  filename: string;
  file_type: string;
  file_size_bytes: number;
  category: string;
  status: string;
  error_message?: string;
  version: number;
  page_count: number;
  chunk_count: number;
  created_at: string;
  updated_at: string;
}

export interface DocumentChunk {
  id: string;
  chunk_index: number;
  content: string;
  page_number?: number;
  sheet_name?: string;
  section_title?: string;
}

export interface Conversation {
  id: string;
  workspace_id: string;
  title: string;
  is_pinned: boolean;
  created_at: string;
  updated_at: string;
  message_count?: number;
}

export interface Citation {
  document_id: string;
  document_title: string;
  page_number?: number;
  sheet_name?: string;
  section_title?: string;
  excerpt: string;
  similarity_score?: number;
}

export interface Message {
  id: string;
  conversation_id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  citations_json: Citation[];
  agent_steps_json: any[];
  tool_calls_json: any[];
  tokens_prompt: number;
  tokens_completion: number;
  total_tokens: number;
  latency_ms: number;
  feedback_rating?: number;
  feedback_notes?: string;
  created_at: string;
}

export interface ReportItem {
  id: string;
  workspace_id: string;
  title: string;
  report_type: string;
  executive_summary: string;
  findings: any[];
  risk_analysis: any[];
  recommendations: any[];
  limitations?: string;
  citations: any[];
  markdown_content: string;
  created_at: string;
}

export interface OverviewMetrics {
  total_documents: number;
  processed_documents: number;
  failed_documents: number;
  total_conversations: number;
  total_ai_queries: number;
  total_reports: number;
  agent_tasks_completed: number;
  avg_response_time_ms: number;
  total_tokens_consumed: number;
  estimated_api_cost: number;
  processing_queue_status: string;
  recent_activities: any[];
  documents_by_type: Record<string, number>;
  query_trends: any[];
}

export const api = {
  // Auth
  register: (data: any) => apiRequest('/auth/register', { method: 'POST', body: JSON.stringify(data) }),
  login: (data: any) => apiRequest('/auth/login', { method: 'POST', body: JSON.stringify(data) }),
  getMe: () => apiRequest<User>('/auth/me'),
  updateProfile: (data: any) => apiRequest<User>('/users/me', { method: 'PATCH', body: JSON.stringify(data) }),
  
  // Workspaces
  listWorkspaces: () => apiRequest<Workspace[]>('/workspaces'),
  createWorkspace: (data: { name: string; description?: string }) => 
    apiRequest<Workspace>('/workspaces', { method: 'POST', body: JSON.stringify(data) }),

  // Documents
  listDocuments: (params: Record<string, any> = {}) => {
    const cleanParams: Record<string, string> = {};
    for (const [key, val] of Object.entries(params)) {
      if (val !== undefined && val !== null && val !== '' && val !== 'all') {
        cleanParams[key] = String(val);
      }
    }
    const qs = new URLSearchParams(cleanParams).toString();
    return apiRequest<{ items: DocumentItem[]; total: number }>(`/documents${qs ? `?${qs}` : ''}`);
  },
  uploadDocument: (formData: FormData) => apiRequest<DocumentItem>('/documents/upload', { method: 'POST', body: formData }),
  uploadBatch: (formData: FormData) => apiRequest<DocumentItem[]>('/documents/upload-batch', { method: 'POST', body: formData }),
  getDocumentPreview: (id: string, limit = 10) => apiRequest<DocumentChunk[]>(`/documents/${id}/preview?limit=${limit}`),
  reprocessDocument: (id: string) => apiRequest(`/documents/${id}/reprocess`, { method: 'POST' }),
  deleteDocument: (id: string) => apiRequest(`/documents/${id}`, { method: 'DELETE' }),

  // Chat
  listConversations: () => apiRequest<Conversation[]>('/chat/conversations'),
  createConversation: (title?: string) => 
    apiRequest<Conversation>('/chat/conversations', { method: 'POST', body: JSON.stringify({ title }) }),
  getConversation: (id: string) => apiRequest<{ id: string; title: string; is_pinned: boolean; messages: Message[] }>(`/chat/conversations/${id}`),
  updateConversation: (id: string, data: any) => 
    apiRequest<Conversation>(`/chat/conversations/${id}`, { method: 'PATCH', body: JSON.stringify(data) }),
  deleteConversation: (id: string) => apiRequest(`/chat/conversations/${id}`, { method: 'DELETE' }),
  sendMessage: (convId: string, data: { content: string; selected_document_ids?: string[]; use_agents?: boolean }) =>
    apiRequest<Message>(`/chat/conversations/${convId}/messages`, { method: 'POST', body: JSON.stringify(data) }),
  submitFeedback: (messageId: string, rating: number, notes?: string) =>
    apiRequest<Message>(`/chat/messages/${messageId}/feedback`, { method: 'POST', body: JSON.stringify({ rating, notes }) }),

  // Agents
  listAgentRuns: () => apiRequest<any[]>('/agents/runs'),
  listToolExecutions: () => apiRequest<any[]>('/agents/tools/executions'),
  executeAgentMission: (data: { query: string; agent_type?: string; document_ids?: string[] }) =>
    apiRequest<any>('/agents/execute', { method: 'POST', body: JSON.stringify(data) }),
  submitApproval: (runId: string, approved: boolean, reason?: string) =>
    apiRequest(`/agents/approval/${runId}`, { method: 'POST', body: JSON.stringify({ approved, reason }) }),

  // Workflows
  listWorkflows: () => apiRequest<any[]>('/workflows'),
  executeWorkflow: (data: { workflow_id: string; document_ids: string[]; custom_instructions?: string }) =>
    apiRequest<any>('/workflows/execute', { method: 'POST', body: JSON.stringify(data) }),

  // Reports
  listReports: () => apiRequest<ReportItem[]>('/reports'),
  getReport: (id: string) => apiRequest<ReportItem>(`/reports/${id}`),
  generateReport: (data: any) => apiRequest<ReportItem>('/reports', { method: 'POST', body: JSON.stringify(data) }),
  deleteReport: (id: string) => apiRequest(`/reports/${id}`, { method: 'DELETE' }),

  // Knowledge Base
  getGraph: (limit = 60) => apiRequest<{ nodes: any[]; edges: any[] }>(`/knowledge-base/graph?limit=${limit}`),
  triggerExtraction: (documentId: string) => apiRequest(`/knowledge-base/extract/${documentId}`, { method: 'POST' }),
  extractAllEntities: () => apiRequest<{ message: string; entities_extracted: number }>('/knowledge-base/extract-all', { method: 'POST' }),

  // Evaluations
  listEvalDatasets: () => apiRequest<any[]>('/evaluations/datasets'),
  createEvalDataset: (data: any) => apiRequest<any>('/evaluations/datasets', { method: 'POST', body: JSON.stringify(data) }),
  listEvalRuns: () => apiRequest<any[]>('/evaluations/runs'),
  triggerEvalRun: (data: any) => apiRequest<any>('/evaluations/runs', { method: 'POST', body: JSON.stringify(data) }),

  // MCP Tools
  listMCPTools: () => apiRequest<any[]>('/mcp/tools'),
  executeMCPTool: (toolName: string, args: any) => 
    apiRequest<any>('/mcp/execute', { method: 'POST', body: JSON.stringify({ tool_name: toolName, arguments: args }) }),

  // Analytics
  getOverviewMetrics: () => apiRequest<OverviewMetrics>('/analytics/overview'),
  
  // Health
  getHealth: () => apiRequest<any>('/health'),
};
