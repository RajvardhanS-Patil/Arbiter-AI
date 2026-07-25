import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Clock, CheckCircle, AlertTriangle, Trash2, ArrowLeft, BarChart2 } from 'lucide-react';
import { api } from '../services/api';

export const HistoryPage = () => {
  const navigate = useNavigate();
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchSessions();
  }, []);

  const fetchSessions = async () => {
    setLoading(true);
    try {
      const res = await api.getSessions();
      setSessions(res.sessions || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id, e) => {
    e.stopPropagation();
    if (!window.confirm('Are you sure you want to delete this session?')) return;
    try {
      await api.deleteSession(id);
      setSessions(prev => prev.filter(s => s.id !== id));
    } catch (err) {
      console.error(err);
      alert('Delete failed');
    }
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'completed':
        return (
          <span className="font-label-caps text-[10px] px-2 py-1 bg-secondary-container/20 text-secondary border border-secondary/30 rounded font-bold">
            VERIFIED
          </span>
        );
      case 'failed':
        return (
          <span className="font-label-caps text-[10px] px-2 py-1 bg-red-500/20 text-red-400 border border-red-500/30 rounded font-bold">
            FAILED
          </span>
        );
      case 'processing':
        return (
          <span className="font-label-caps text-[10px] px-2 py-1 bg-tertiary-container/20 text-tertiary border border-tertiary/30 rounded animate-pulse font-bold">
            PROCESSING
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
    <div className="max-w-4xl mx-auto select-none text-left">
      <button 
        onClick={() => navigate('/')}
        className="flex items-center gap-2 text-on-surface-variant hover:text-primary transition-colors font-label-caps text-xs mb-6"
      >
        <ArrowLeft className="w-4 h-4" /> Back to Search
      </button>

      <h1 className="font-display-lg text-3xl text-white font-bold leading-tight mb-8">
        Investigation Archives
      </h1>

      {loading ? (
        <div className="glass-panel rounded-2xl py-24 text-center text-on-surface-variant border border-white/10 flex flex-col items-center gap-3">
          <Clock className="w-8 h-8 animate-spin text-primary" />
          <span>Retrieving archived records...</span>
        </div>
      ) : sessions.length > 0 ? (
        <div className="space-y-4">
          {sessions.map(s => (
            <div
              key={s.id}
              onClick={() => navigate(s.status === 'completed' ? `/report/${s.id}` : `/observatory/${s.id}`)}
              className="glass-card p-6 rounded-xl border border-white/10 hover:border-primary/20 flex justify-between items-center cursor-pointer"
            >
              <div className="flex-1 pr-6">
                <div className="flex items-center gap-3 mb-2 flex-wrap">
                  {getStatusBadge(s.status)}
                  <span className="text-on-surface-variant font-data-mono text-xs">
                    ID: {s.id.slice(0, 8).toUpperCase()}
                  </span>
                  <span className="text-on-surface-variant font-data-mono text-xs">
                    | {s.created_at ? new Date(s.created_at + 'Z').toLocaleString() : 'Recent'}
                  </span>
                </div>
                <h3 className="text-white text-lg font-semibold line-clamp-1">{s.query}</h3>
                <p className="text-sm text-on-surface-variant mt-1">
                  Processed {s.total_claims || 0} claims using {s.verified_claims || 0} supporting citations.
                </p>
              </div>

              <div className="flex items-center gap-6">
                {s.status === 'completed' && (
                  <div className="text-right hidden sm:block">
                    <p className="font-display-lg text-lg text-white font-bold">{s.overall_confidence}%</p>
                    <p className="font-label-caps text-[10px] text-on-surface-variant">Confidence</p>
                  </div>
                )}
                <button
                  onClick={(e) => handleDelete(s.id, e)}
                  className="p-2.5 rounded-lg bg-surface-container hover:bg-red-500/10 text-on-surface-variant hover:text-red-400 border border-white/5 hover:border-red-500/20 transition-all"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="glass-panel rounded-2xl py-24 text-center text-on-surface-variant border border-white/10">
          No past investigation sessions found. Initiate a query on the home page!
        </div>
      )}
    </div>
  );
};
export { }
