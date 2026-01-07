import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

interface ApiContextType {
  apiBase: string;
  setApiBase: (url: string) => void;
}

const ApiContext = createContext<ApiContextType | undefined>(undefined);

const STORAGE_KEY = 'sigmatch_api_base';
const DEFAULT_API_BASE = 'http://localhost:8000';

export function ApiProvider({ children }: { children: ReactNode }) {
  const [apiBase, setApiBaseState] = useState<string>(() => {
    const stored = localStorage.getItem(STORAGE_KEY);
    return stored || DEFAULT_API_BASE;
  });

  const setApiBase = (url: string) => {
    localStorage.setItem(STORAGE_KEY, url);
    setApiBaseState(url);
    // Dispatch event so api.ts can pick up changes
    window.dispatchEvent(new Event('apibase-changed'));
  };

  return (
    <ApiContext.Provider value={{ apiBase, setApiBase }}>
      {children}
    </ApiContext.Provider>
  );
}

export function useApi() {
  const context = useContext(ApiContext);
  if (context === undefined) {
    throw new Error('useApi must be used within an ApiProvider');
  }
  return context;
}

export function getApiBase(): string {
  return localStorage.getItem(STORAGE_KEY) || DEFAULT_API_BASE;
}
