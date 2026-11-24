/**
 * Primary Sidebar Navigation with all 11 functional modules and workspace selection.
 */
import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  MessageSquare,
  Files,
  Network,
  Bot,
  GitBranch,
  FileText,
  BarChart2,
  TrendingUp,
  Cpu,
  Settings,
  Sparkles,
  ChevronDown
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

export const navigationItems = [
  { name: 'Overview', path: '/', icon: LayoutDashboard },
  { name: 'AI Workspace', path: '/chat', icon: MessageSquare },
  { name: 'Documents', path: '/documents', icon: Files },
  { name: 'Knowledge Base', path: '/knowledge-base', icon: Network },
  { name: 'AI Agents', path: '/agents', icon: Bot },
  { name: 'Workflows', path: '/workflows', icon: GitBranch },
  { name: 'Reports', path: '/reports', icon: FileText },
  { name: 'Evaluations', path: '/evaluations', icon: BarChart2 },
  { name: 'Analytics', path: '/analytics', icon: TrendingUp },
  { name: 'Integrations', path: '/integrations', icon: Cpu },
  { name: 'Settings', path: '/settings', icon: Settings },
];

export const Sidebar: React.FC = () => {
  const { workspaces, activeWorkspace, setActiveWorkspace } = useAuth();
  const [wsDropdownOpen, setWsDropdownOpen] = React.useState(false);

  return (
    <aside className="w-64 bg-slate-900 border-r border-slate-800 flex flex-col h-screen fixed left-0 top-0 z-30 select-none">
      {/* Brand Header */}
      <div className="h-16 px-5 border-b border-slate-800 flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-blue-600 via-aura-500 to-indigo-500 flex items-center justify-center shadow-lg shadow-blue-500/20">
            <Sparkles className="w-5 h-5 text-white animate-pulse" />
          </div>
          <div>
            <h1 className="font-bold text-lg text-white tracking-tight flex items-center gap-1.5">
              AURA
              <span className="text-[10px] font-semibold uppercase tracking-wider px-1.5 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20">Enterprise</span>
            </h1>
          </div>
        </div>
      </div>

      {/* Workspace Switcher */}
      <div className="p-3 border-b border-slate-800/80 relative">
        <label className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider px-2">Active Workspace</label>
        <button
          onClick={() => setWsDropdownOpen(!wsDropdownOpen)}
          className="w-full mt-1 px-3 py-2 rounded-lg bg-slate-800/80 hover:bg-slate-800 border border-slate-700/60 flex items-center justify-between text-left transition-all"
        >
          <span className="text-sm font-medium text-slate-200 truncate">
            {activeWorkspace?.name || 'Default Workspace'}
          </span>
          <ChevronDown className={`w-4 h-4 text-slate-400 transition-transform ${wsDropdownOpen ? 'rotate-180' : ''}`} />
        </button>

        {wsDropdownOpen && (
          <div className="absolute left-3 right-3 top-full mt-1 bg-slate-800 border border-slate-700 rounded-lg shadow-xl z-50 overflow-hidden py-1">
            {workspaces.map((ws) => (
              <button
                key={ws.id}
                onClick={() => {
                  setActiveWorkspace(ws);
                  setWsDropdownOpen(false);
                }}
                className={`w-full text-left px-3 py-2 text-xs transition-colors flex items-center justify-between ${
                  ws.id === activeWorkspace?.id ? 'bg-blue-600/20 text-blue-400 font-semibold' : 'text-slate-300 hover:bg-slate-700/50'
                }`}
              >
                <span className="truncate">{ws.name}</span>
                <span className="text-[10px] opacity-60">{ws.document_count} docs</span>
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Navigation List */}
      <nav className="flex-1 overflow-y-auto p-3 space-y-1">
        {navigationItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            end={item.path === '/'}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${
                isActive
                  ? 'bg-blue-600 text-white shadow-md shadow-blue-600/30 font-semibold'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
              }`
            }
          >
            <item.icon className="w-4 h-4 shrink-0" />
            <span className="truncate">{item.name}</span>
          </NavLink>
        ))}
      </nav>

      {/* System Status Footer */}
      <div className="p-3 border-t border-slate-800 bg-slate-900/50">
        <div className="flex items-center gap-2 px-2 py-1.5 rounded-md bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></span>
          <span className="font-medium">System Online • v1.0.0</span>
        </div>
      </div>
    </aside>
  );
};
