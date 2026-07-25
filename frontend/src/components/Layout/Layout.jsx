import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Gavel, Eye, FileText, History, Zap, Settings, RefreshCw, X, Shield, Menu } from 'lucide-react';
import { api } from '../../services/api';

export const Layout = ({ children }) => {
  const location = useLocation();
  const [systemActive, setSystemActive] = useState(true);
  const [totalSessions, setTotalSessions] = useState(0);

  useEffect(() => {
    // Fetch stats
    api.getSessions(1)
      .then(res => {
        setTotalSessions(res.total || 0);
      })
      .catch(() => {});
  }, [location.pathname]);

  const isActive = (path) => {
    return location.pathname === path;
  };

  return (
    <div className="bg-surface text-on-surface min-h-screen font-body-md relative select-none">
      {/* Top Navbar */}
      <nav className="fixed top-0 w-full h-16 z-50 flex justify-between items-center px-margin-mobile md:px-margin-desktop py-4 bg-surface/80 backdrop-blur-xl border-b border-white/10 shadow-sm">
        <div className="flex items-center gap-8">
          <Link to="/" className="font-display-lg text-headline-md tracking-tighter text-primary font-bold">
            ARBITER AI
          </Link>
          <div className="hidden md:flex items-center gap-6">
            <Link 
              to="/" 
              className={`font-body-md text-body-md transition-colors ${isActive('/') ? 'text-primary font-bold border-b-2 border-primary pb-1' : 'text-on-surface-variant font-medium hover:text-primary'}`}
            >
              Home
            </Link>
            <Link 
              to="/history" 
              className={`font-body-md text-body-md transition-colors ${isActive('/history') ? 'text-primary font-bold border-b-2 border-primary pb-1' : 'text-on-surface-variant font-medium hover:text-primary'}`}
            >
              History
            </Link>
          </div>
        </div>
        <div className="flex items-center gap-4">
          <Link to="/history" className="hidden md:block font-body-md text-body-md font-medium text-on-surface-variant hover:text-primary transition-colors">
            Sessions History
          </Link>
        </div>
      </nav>

      {/* Sidebar - Desktop Only */}
      <aside className="hidden md:flex flex-col fixed left-0 top-0 h-full w-[280px] z-40 bg-surface-container-lowest border-r border-white/10 pt-24 pb-8 px-6">
        <div className="flex items-center gap-3 mb-12">
          <div className="relative">
            <div className="w-12 h-12 rounded-full bg-primary-container/20 flex items-center justify-center border border-primary/30 text-primary">
              <Shield className="w-6 h-6 animate-pulse" />
            </div>
            <div className="absolute bottom-0 right-0 w-3 h-3 bg-emerald-500 rounded-full border-2 border-surface-container-lowest"></div>
          </div>
          <div>
            <h3 className="font-headline-md text-body-md text-primary leading-tight font-semibold">Arbiter AI</h3>
            <p className="font-label-caps text-[10px] text-on-surface-variant uppercase tracking-widest">Precision Intelligence</p>
          </div>
        </div>

        <div className="space-y-2 flex-grow">
          <Link 
            to="/" 
            className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-all hover:translate-x-1 ${isActive('/') ? 'text-primary border-l-4 border-primary-container bg-primary-container/10 font-bold' : 'text-on-surface-variant hover:bg-surface-container-high'}`}
          >
            <Gavel className="w-5 h-5" />
            <span className="font-label-caps text-label-caps">Home</span>
          </Link>
          <Link 
            to="/history" 
            className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-all hover:translate-x-1 ${isActive('/history') ? 'text-primary border-l-4 border-primary-container bg-primary-container/10 font-bold' : 'text-on-surface-variant hover:bg-surface-container-high'}`}
          >
            <History className="w-5 h-5" />
            <span className="font-label-caps text-label-caps">Archive</span>
          </Link>
        </div>

        <div className="mt-auto pt-6 border-t border-white/5">
          <div className="flex items-center justify-between text-on-surface-variant mb-4">
            <span className="font-label-caps text-[10px] uppercase">Agent Status</span>
            <span className="text-[10px] font-data-mono text-emerald-400">OPERATIONAL</span>
          </div>
          <div className="w-full h-1 bg-surface-container-high rounded-full overflow-hidden">
            <div className="w-full h-full bg-primary shadow-[0_0_8px_rgba(210,187,255,0.5)]"></div>
          </div>
        </div>
      </aside>

      {/* Main Canvas */}
      <main className="md:ml-[280px] pt-24 pb-24 md:pb-8 px-margin-mobile md:px-margin-desktop min-h-screen relative z-10">
        {children}
      </main>

      {/* Bottom Navigation Bar - Mobile Only */}
      <nav className="md:hidden fixed bottom-0 w-full z-50 flex justify-around items-center px-4 py-2 bg-surface-container/90 backdrop-blur-lg border-t border-white/10 shadow-lg rounded-t-xl">
        <Link 
          to="/" 
          className={`flex flex-col items-center justify-center p-2 rounded-xl transition-colors ${isActive('/') ? 'text-primary bg-primary-container/20' : 'text-on-surface-variant'}`}
        >
          <Gavel className="w-5 h-5" />
          <span className="font-label-caps text-[10px]">Home</span>
        </Link>
        <Link 
          to="/history" 
          className={`flex flex-col items-center justify-center p-2 rounded-xl transition-colors ${isActive('/history') ? 'text-primary bg-primary-container/20' : 'text-on-surface-variant'}`}
        >
          <History className="w-5 h-5" />
          <span className="font-label-caps text-[10px]">Archive</span>
        </Link>
      </nav>
    </div>
  );
};
export { }
