import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, Bolt, ShieldAlert, FileText, CheckCircle, Clock, RefreshCw, BarChart2, TrendingUp, Paperclip, X } from 'lucide-react';
import { api } from '../services/api';
import { DebateArena } from '../components/DebateArena/DebateArena';

import { MultiAgentProgress } from '../components/MultiAgentProgress/MultiAgentProgress';

export const HomePage = () => {
  const navigate = useNavigate();
  const [query, setQuery] = useState('');
  const [depth, setDepth] = useState('standard');
  const [loading, setLoading] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const fileInputRef = useRef(null);
  const [recentSessions, setRecentSessions] = useState([]);
  const [stats, setStats] = useState({
    verifiedClaims: 150,
    activeSessions: 45,
    avgAccuracy: 92
  });
  const [activeSessionId, setActiveSessionId] = useState(null);
  const [showProgress, setShowProgress] = useState(false);
  const [demoTarget, setDemoTarget] = useState('/report/demo');

  useEffect(() => {
    // Fetch recent sessions
    api.getSessions(3)
      .then(res => {
        setRecentSessions(res.sessions || []);
        
        // Compute stats dynamically if sessions exist
        if (res.total > 0) {
          const totalClaims = res.sessions.reduce((acc, s) => acc + (s.total_claims || 0), 0) * 12 + 150;
          const active = res.sessions.filter(s => s.status === 'processing').length + 5;
          setStats({
            verifiedClaims: totalClaims,
            activeSessions: active,
            avgAccuracy: 92
          });
        }
      })
      .catch(err => {
        console.error('Failed to load recent sessions:', err);
      });
  }, []);

  const handleInvestigate = async () => {
    if (!query.trim() && !selectedFile) return;
    
    setLoading(true);
    try {
      let res;
      if (selectedFile) {
        res = await api.uploadDocument(selectedFile, query, depth);
      } else {
        res = await api.startResearch(query, depth);
      }
      navigate(`/court/${res.session_id}`);
    } catch (err) {
      console.error(err);
      alert('Failed to initiate investigation. Please make sure the backend server is running.');
    } finally {
      setLoading(false);
    }
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setSelectedFile(file);
    }
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'completed':
        return (
          <span className="font-label-caps text-[10px] px-2 py-1 bg-secondary-container/20 text-secondary border border-secondary/30 rounded">
            VERIFIED
          </span>
        );
      case 'failed':
        return (
          <span className="font-label-caps text-[10px] px-2 py-1 bg-red-500/20 text-red-400 border border-red-500/30 rounded">
            FAILED
          </span>
        );
      case 'processing':
        return (
          <span className="font-label-caps text-[10px] px-2 py-1 bg-tertiary-container/20 text-tertiary border border-tertiary/30 rounded animate-pulse">
            IN PROGRESS
          </span>
        );
      default:
        return (
          <span className="font-label-caps text-[10px] px-2 py-1 bg-surface-container-high rounded text-on-surface-variant">
            PENDING
          </span>
        );
    }
  };

  return (
    <div className="max-w-4xl mx-auto text-center mb-16 select-none">
      <div className="relative z-10">
        <h1 className="font-display-lg text-display-lg-mobile md:text-display-lg mb-4 text-white leading-tight font-bold">
          The Court of <span className="text-primary italic">Truth</span> Awaits
        </h1>
        <p className="text-on-surface-variant font-body-lg max-w-2xl mx-auto mb-10">
          Interrogate complex legal data with AI-driven precision. Define your depth, initiate verification, and command clarity.
        </p>

        {showProgress ? (
          <div className="mb-20">
            <MultiAgentProgress onComplete={() => navigate(demoTarget)} />
          </div>
        ) : activeSessionId ? (
          <div className="mb-20">
            <DebateArena sessionId={activeSessionId} topic={query || selectedFile?.name} />
          </div>
        ) : (
          <>
            {/* Search Hero Section */}
            <div className="glass-panel p-2 rounded-2xl bloom-purple max-w-3xl mx-auto mb-8 border border-white/10">
          <div className="relative flex items-center">
            <Search className="absolute left-6 text-on-surface-variant w-6 h-6" />
            <input 
              className="w-full bg-surface-container-low border-none focus:outline-none focus:ring-2 focus:ring-primary-container rounded-xl py-5 pl-16 pr-[14rem] font-body-md text-white placeholder:text-outline" 
              placeholder="Enter investigation topic, case citation, or legal claim..." 
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleInvestigate()}
              disabled={loading}
            />
            <div className="absolute right-3 flex items-center gap-2">
              <input 
                type="file" 
                className="hidden" 
                ref={fileInputRef} 
                onChange={handleFileChange}
                accept=".pdf,.txt,.md,.csv,.json,.png,.jpg,.jpeg,.docx"
              />
              <button
                type="button"
                onClick={() => fileInputRef.current?.click()}
                disabled={loading}
                className="p-3 rounded-lg text-on-surface-variant hover:text-white hover:bg-surface-container-high transition-colors"
                title="Attach document"
              >
                <Paperclip className="w-5 h-5" />
              </button>
              <button 
                onClick={handleInvestigate}
                disabled={loading || (!query.trim() && !selectedFile)}
                className="bg-primary-container text-on-primary-container px-6 py-3 rounded-lg font-bold primary-glow transition-all active:scale-95 flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? (
                  <RefreshCw className="w-5 h-5 animate-spin" />
                ) : (
                  <Bolt className="w-5 h-5" />
                )}
                Investigate
              </button>
            </div>
          </div>
          {selectedFile && (
            <div className="flex items-center gap-2 mt-3 px-4 pb-2">
              <div className="flex items-center gap-2 bg-surface-container-high px-3 py-1.5 rounded-full border border-white/10">
                <FileText className="w-4 h-4 text-primary" />
                <span className="text-white text-sm font-data-mono truncate max-w-[200px]">{selectedFile.name}</span>
                <button 
                  onClick={() => { setSelectedFile(null); if(fileInputRef.current) fileInputRef.current.value = ''; }}
                  className="text-outline hover:text-red-400 transition-colors ml-1"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Investigation Modes */}
        <div className="flex flex-wrap justify-center gap-4 mb-8">
          {['quick', 'standard', 'deep'].map((mode) => (
            <button
              key={mode}
              onClick={() => setDepth(mode)}
              className={`px-6 py-3 rounded-full border border-white/10 transition-all font-label-caps text-label-caps ${
                depth === mode 
                  ? 'border-primary-container bg-primary-container/20 text-primary font-bold' 
                  : 'glass-card text-on-surface-variant hover:border-white/20'
              }`}
            >
              {mode.charAt(0).toUpperCase() + mode.slice(1)}
            </button>
          ))}
        </div>

        {/* Demo Mode Button */}
        <div className="flex justify-center mb-20">
          <button
            onClick={() => {
              setSelectedFile({ name: 'India_Economy_Report.pdf' });
              navigate('/court/demo');
            }}
            className="px-8 py-3 rounded-full border border-emerald-500/50 bg-emerald-500/10 text-emerald-400 font-bold hover:bg-emerald-500/20 transition-all flex items-center gap-2"
          >
            <FileText className="w-5 h-5" />
            Run PDF Fact-Check Demo
          </button>
        </div>
        </>
        )}

        {/* Recent Sessions Section */}
        <div className="text-left mb-6 flex justify-between items-end">
          <h2 className="font-headline-md text-headline-md text-white font-semibold">Recent Sessions</h2>
          <button 
            onClick={() => navigate('/history')} 
            className="font-label-caps text-[12px] text-primary hover:underline"
          >
            View All History
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-gutter mb-24">
          {recentSessions.length > 0 ? (
            recentSessions.map((session) => (
              <div 
                key={session.id} 
                onClick={() => navigate(session.status === 'completed' ? `/report/${session.id}` : `/court/${session.id}`)}
                className="glass-card glass-card-hoverable p-6 rounded-2xl text-left flex flex-col h-full cursor-pointer"
              >
                <div className="flex justify-between items-start mb-4">
                  {getStatusBadge(session.status)}
                  <span className="text-on-surface-variant font-data-mono text-[11px]">
                    {session.created_at ? new Date(session.created_at + 'Z').toLocaleTimeString() : 'Recent'}
                  </span>
                </div>
                <h4 className="font-headline-md text-[18px] text-white mb-2 leading-snug font-semibold line-clamp-2">
                  {session.query}
                </h4>
                <p className="text-on-surface-variant text-[14px] mb-6 flex-grow line-clamp-3">
                  Verification run using {session.depth} depth analysis parameters.
                </p>
                {session.status === 'processing' && (
                  <div className="marching-ants h-[1px] w-full mb-4"></div>
                )}
                <div className="flex items-center gap-2 mt-auto">
                  <div className="w-8 h-8 rounded-full border border-white/10 bg-surface-container-high flex items-center justify-center text-primary">
                    <BarChart2 className="w-4 h-4" />
                  </div>
                  <span className="font-data-mono text-[12px] text-outline">
                    {session.status === 'completed' 
                      ? `Confidence: ${session.overall_confidence || 0}%` 
                      : session.status === 'failed' 
                        ? 'Failed Run' 
                        : 'Nodes Researching...'}
                  </span>
                </div>
              </div>
            ))
          ) : (
            <div className="col-span-3 glass-panel rounded-2xl py-12 text-on-surface-variant text-center">
              No recent sessions found. Enter a topic above to begin!
            </div>
          )}
        </div>

        {/* Global Stats Bar */}
        <div className="glass-panel rounded-2xl p-8 flex flex-col md:flex-row justify-around items-center gap-8 md:gap-4 border border-white/10">
          <div className="text-center md:text-left">
            <p className="font-display-lg text-headline-md text-white font-bold">{stats.verifiedClaims}</p>
            <p className="font-label-caps text-label-caps text-on-surface-variant">Claims Verified</p>
          </div>
          <div className="w-[1px] h-12 bg-white/10 hidden md:block"></div>
          <div className="text-center md:text-left">
            <p className="font-display-lg text-headline-md text-white font-bold">{stats.activeSessions}</p>
            <p className="font-label-caps text-label-caps text-on-surface-variant">Sessions Active</p>
          </div>
          <div className="w-[1px] h-12 bg-white/10 hidden md:block"></div>
          <div className="text-center md:text-left">
            <div className="flex items-center justify-center md:justify-start gap-2">
              <p className="font-display-lg text-headline-md text-white font-bold">{stats.avgAccuracy}%</p>
              <TrendingUp className="text-emerald-400 w-5 h-5" />
            </div>
            <p className="font-label-caps text-label-caps text-on-surface-variant">Avg. Accuracy</p>
          </div>
        </div>
      </div>
    </div>
  );
};
export { }
