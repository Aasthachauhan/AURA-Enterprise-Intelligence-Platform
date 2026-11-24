/**
 * Authentication Context managing user sessions, workspaces, and tenant context.
 */
import React, { createContext, useContext, useState, useEffect } from 'react';
import { api, User, Workspace } from '../api/endpoints';

interface AuthContextType {
  user: User | null;
  workspaces: Workspace[];
  activeWorkspace: Workspace | null;
  isLoading: boolean;
  login: (data: any) => Promise<void>;
  register: (data: any) => Promise<void>;
  logout: () => void;
  setActiveWorkspace: (ws: Workspace) => void;
  refreshWorkspaces: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [workspaces, setWorkspaces] = useState<Workspace[]>([]);
  const [activeWorkspace, setActiveWorkspaceState] = useState<Workspace | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const initAuth = async () => {
    const token = localStorage.getItem('aura_access_token');
    if (!token) {
      setIsLoading(false);
      return;
    }

    try {
      const me = await api.getMe();
      setUser(me);

      const wsList = await api.listWorkspaces();
      setWorkspaces(wsList);

      const savedWsId = localStorage.getItem('aura_workspace_id');
      const currentWs = wsList.find((w) => w.id === savedWsId) || wsList[0] || null;
      if (currentWs) {
        setActiveWorkspaceState(currentWs);
        localStorage.setItem('aura_workspace_id', currentWs.id);
      }
    } catch (err) {
      console.error('Failed to load user session', err);
      localStorage.removeItem('aura_access_token');
      localStorage.removeItem('aura_refresh_token');
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    initAuth();
  }, []);

  const login = async (credentials: any) => {
    const res = await api.login(credentials);
    localStorage.setItem('aura_access_token', res.access_token);
    localStorage.setItem('aura_refresh_token', res.refresh_token);
    if (res.user.active_workspace_id) {
      localStorage.setItem('aura_workspace_id', res.user.active_workspace_id);
    }
    await initAuth();
  };

  const register = async (userData: any) => {
    const res = await api.register(userData);
    localStorage.setItem('aura_access_token', res.access_token);
    localStorage.setItem('aura_refresh_token', res.refresh_token);
    if (res.user.active_workspace_id) {
      localStorage.setItem('aura_workspace_id', res.user.active_workspace_id);
    }
    await initAuth();
  };

  const logout = () => {
    localStorage.removeItem('aura_access_token');
    localStorage.removeItem('aura_refresh_token');
    localStorage.removeItem('aura_workspace_id');
    setUser(null);
    setWorkspaces([]);
    setActiveWorkspaceState(null);
    window.location.href = '/login';
  };

  const setActiveWorkspace = (ws: Workspace) => {
    setActiveWorkspaceState(ws);
    localStorage.setItem('aura_workspace_id', ws.id);
    window.location.reload();
  };

  const refreshWorkspaces = async () => {
    const wsList = await api.listWorkspaces();
    setWorkspaces(wsList);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        workspaces,
        activeWorkspace,
        isLoading,
        login,
        register,
        logout,
        setActiveWorkspace,
        refreshWorkspaces,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
