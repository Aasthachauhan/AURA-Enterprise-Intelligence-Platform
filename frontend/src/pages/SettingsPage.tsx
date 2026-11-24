/**
 * Page 11: Settings, Workspace Management & AI Provider Configuration.
 */
import React, { useState } from 'react';
import {
  Settings as SettingsIcon,
  User,
  Shield,
  Key,
  Layers,
  Save,
  Check
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { api } from '../api/endpoints';

export const SettingsPage: React.FC = () => {
  const { user, activeWorkspace } = useAuth();
  const [fullName, setFullName] = useState(user?.full_name || '');
  const [selectedModel, setSelectedModel] = useState('gpt-4o');
  const [savedSuccess, setSavedSuccess] = useState(false);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.updateProfile({ full_name: fullName });
      setSavedSuccess(true);
      setTimeout(() => setSavedSuccess(false), 3000);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="space-y-6 max-w-4xl">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight">Platform Settings</h1>
        <p className="text-sm text-slate-400">Manage user profile, active workspace, AI models, and enterprise security policies.</p>
      </div>

      {/* Profile Settings */}
      <form onSubmit={handleSave} className="p-6 rounded-2xl bg-slate-900 border border-slate-800 space-y-4">
        <h2 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
          <User className="w-4 h-4 text-blue-400" /> User Profile & Identity
        </h2>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
          <div>
            <label className="text-slate-400 font-medium">Full Name</label>
            <input
              type="text"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              className="w-full mt-1 p-2.5 rounded-lg bg-slate-800 border border-slate-700 text-white"
            />
          </div>

          <div>
            <label className="text-slate-400 font-medium">Email Address</label>
            <input
              type="email"
              disabled
              value={user?.email || ''}
              className="w-full mt-1 p-2.5 rounded-lg bg-slate-800/50 border border-slate-700/50 text-slate-400 cursor-not-allowed"
            />
          </div>
        </div>

        <button
          type="submit"
          className="px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold flex items-center gap-2 shadow-md transition-all"
        >
          {savedSuccess ? <Check className="w-3.5 h-3.5" /> : <Save className="w-3.5 h-3.5" />}
          {savedSuccess ? 'Profile Updated!' : 'Save Changes'}
        </button>
      </form>

      {/* Model & AI Settings */}
      <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 space-y-4">
        <h2 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
          <Key className="w-4 h-4 text-purple-400" /> AI Provider & Model Configuration
        </h2>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
          <div>
            <label className="text-slate-400 font-medium">Default Reasoning Model</label>
            <select
              value={selectedModel}
              onChange={(e) => setSelectedModel(e.target.value)}
              className="w-full mt-1 p-2.5 rounded-lg bg-slate-800 border border-slate-700 text-white"
            >
              <option value="gpt-4o">OpenAI GPT-4o</option>
              <option value="gemini-1.5-pro">Google Gemini 1.5 Pro</option>
              <option value="claude-3-5-sonnet">Anthropic Claude 3.5 Sonnet</option>
              <option value="mock_local">AURA Local Grounded Synthesizer (Offline Mode)</option>
            </select>
          </div>

          <div>
            <label className="text-slate-400 font-medium">RAG Hybrid Search Balance</label>
            <div className="mt-2 text-slate-300 flex items-center justify-between text-xs">
              <span>Dense Vector (50%)</span>
              <span>BM25 Keyword (50%)</span>
            </div>
          </div>
        </div>
      </div>

      {/* Security Policies */}
      <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 space-y-3">
        <h2 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
          <Shield className="w-4 h-4 text-emerald-400" /> Enterprise Security & Guardrails
        </h2>
        <div className="space-y-2 text-xs text-slate-300">
          <p className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
            Indirect prompt-injection sanitization enabled on all uploaded files.
          </p>
          <p className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
            Strict workspace tenant isolation enforced at the database query layer.
          </p>
          <p className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
            Human-in-the-loop authorization required for any state-modifying operations.
          </p>
        </div>
      </div>
    </div>
  );
};
