import { BrowserRouter, Routes, Route, Navigate, Link, useLocation } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { IncidentList } from '@/pages/IncidentList';
import { IncidentAnalysis } from '@/pages/IncidentAnalysis';
import { Overview } from '@/pages/Overview';
import { Layout, Activity, Server } from 'lucide-react';
import { cn } from '@/lib/utils';
import React from 'react';

const queryClient = new QueryClient();

// Sidebar Link Component
const NavItem = ({ to, icon: Icon, children }: { to: string, icon: any, children: React.ReactNode }) => {
  const location = useLocation();
  const isActive = location.pathname.startsWith(to);

  return (
    <Link
      to={to}
      className={cn(
        "flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-lg transition-colors",
        isActive
          ? "bg-indigo-500/10 text-indigo-400 border border-indigo-500/20"
          : "text-slate-400 hover:text-slate-200 hover:bg-white/5"
      )}
    >
      <Icon size={18} />
      {children}
    </Link>
  );
};

// Simple Sidebar Layout
const AppLayout = ({ children }: { children: React.ReactNode }) => (
  <div className="flex h-screen w-full bg-[#0a0e17] text-slate-200">
    {/* Sidebar */}
    <aside className="w-64 border-r border-white/5 bg-[#0f141e]/50 backdrop-blur-xl flex flex-col">
      <div className="p-6">
        <Link to="/" className="flex items-center gap-2 hover:opacity-80 transition-opacity">
          <div className="h-6 w-6 bg-indigo-500 rounded-lg animate-pulse-subtle" />
          <span className="font-bold tracking-tight text-white">PRODSENTINEL</span>
        </Link>
      </div>

      <nav className="flex-1 px-4 space-y-1">
        <NavItem to="/overview" icon={Activity}>Overview</NavItem>
        <NavItem to="/incidents" icon={Layout}>Incidents</NavItem>
        <a href="#" className="flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-lg text-slate-400 hover:text-slate-200 hover:bg-white/5 transition-colors">
          <Server size={18} />
          Services
        </a>
      </nav>

      <div className="p-4 border-t border-white/5">
        <div className="text-xs text-slate-500 font-mono">v1.0.0-phase4</div>
      </div>
    </aside>

    {/* Main Content */}
    <main className="flex-1 overflow-auto relative scanline">
      {children}
    </main>
  </div>
);

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <AppLayout>
          <Routes>
            <Route path="/" element={<Navigate to="/overview" replace />} />
            <Route path="/overview" element={<Overview />} />
            <Route path="/incidents" element={<IncidentList />} />
            <Route path="/incidents/:id" element={<IncidentAnalysis />} />
          </Routes>
        </AppLayout>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;
