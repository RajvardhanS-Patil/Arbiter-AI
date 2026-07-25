import React, { useState, useEffect } from 'react';
import { Search, Shield, AlertTriangle, FileCheck, CheckCircle2, Loader2, FileText } from 'lucide-react';

const AGENTS = [
  {
    id: 'researcher',
    name: 'Researcher Agent',
    icon: Search,
    color: 'text-blue-400',
    bg: 'bg-blue-500/10',
    border: 'border-blue-500/30',
    progressColor: 'bg-blue-500',
    statusText: 'Extracting claims from document...'
  },
  {
    id: 'verifier',
    name: 'Fact Verifier',
    icon: Shield,
    color: 'text-emerald-400',
    bg: 'bg-emerald-500/10',
    border: 'border-emerald-500/30',
    progressColor: 'bg-emerald-500',
    statusText: 'Cross-referencing against trusted sources...'
  },
  {
    id: 'detector',
    name: 'Hallucination Detector',
    icon: AlertTriangle,
    color: 'text-amber-400',
    bg: 'bg-amber-500/10',
    border: 'border-amber-500/30',
    progressColor: 'bg-amber-500',
    statusText: 'Detecting logical contradictions...'
  },
  {
    id: 'compiler',
    name: 'Report Compiler',
    icon: FileCheck,
    color: 'text-purple-400',
    bg: 'bg-purple-500/10',
    border: 'border-purple-500/30',
    progressColor: 'bg-purple-500',
    statusText: 'Synthesizing final confidence scores...'
  }
];

export const MultiAgentProgress = ({ onComplete }) => {
  const [progress, setProgress] = useState({
    researcher: 0,
    verifier: 0,
    detector: 0,
    compiler: 0
  });

  useEffect(() => {
    // Start the fake progress sequence
    let currentProgress = { researcher: 0, verifier: 0, detector: 0, compiler: 0 };
    
    const interval = setInterval(() => {
      // Researcher goes fast
      if (currentProgress.researcher < 100) {
        currentProgress.researcher += Math.floor(Math.random() * 15) + 5;
      } else if (currentProgress.verifier < 100) {
        // Verifier starts when researcher is done
        currentProgress.verifier += Math.floor(Math.random() * 10) + 5;
      } else if (currentProgress.detector < 100) {
        // Detector starts when verifier is done
        currentProgress.detector += Math.floor(Math.random() * 12) + 5;
      } else if (currentProgress.compiler < 100) {
        // Compiler finishes up
        currentProgress.compiler += Math.floor(Math.random() * 20) + 5;
      }

      // Cap at 100
      Object.keys(currentProgress).forEach(key => {
        if (currentProgress[key] > 100) currentProgress[key] = 100;
      });

      setProgress({ ...currentProgress });

      // Check if all done
      if (currentProgress.compiler >= 100) {
        clearInterval(interval);
        setTimeout(() => {
          onComplete();
        }, 800); // Wait a tiny bit after hitting 100% before transitioning
      }
    }, 200);

    return () => clearInterval(interval);
  }, [onComplete]);

  return (
    <div className="glass-panel p-8 rounded-2xl border border-white/10 max-w-2xl mx-auto w-full animate-fade-in">
      <div className="flex flex-col items-center mb-8">
        <div className="w-16 h-16 rounded-full bg-primary/20 flex items-center justify-center mb-4 border border-primary/30 relative">
          <FileText className="w-8 h-8 text-primary" />
          <span className="absolute -bottom-1 -right-1 flex h-4 w-4">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-primary opacity-75"></span>
            <span className="relative inline-flex rounded-full h-4 w-4 bg-primary border-2 border-[#121212]"></span>
          </span>
        </div>
        <h2 className="font-display-lg text-2xl text-white font-bold mb-2">Analyzing Document</h2>
        <p className="text-on-surface-variant font-body-md text-center max-w-md">
          Our Multi-Agent system has been deployed. Different specialist models are working together to verify the claims.
        </p>
      </div>

      <div className="space-y-6">
        {AGENTS.map((agent) => {
          const val = progress[agent.id];
          const isActive = val > 0 && val < 100;
          const isDone = val === 100;
          const isWaiting = val === 0;

          return (
            <div 
              key={agent.id} 
              className={`p-4 rounded-xl border transition-all duration-300 ${isWaiting ? 'opacity-40 border-white/5 bg-white/5' : isActive ? 'border-white/20 bg-surface-container-high' : 'border-white/10 bg-surface-container shadow-inner'}`}
            >
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-3">
                  <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${agent.bg} ${agent.border} border`}>
                    <agent.icon className={`w-5 h-5 ${agent.color}`} />
                  </div>
                  <div>
                    <h3 className="text-white font-bold font-headline-md text-sm">{agent.name}</h3>
                    <p className="text-on-surface-variant text-xs font-data-mono">
                      {isWaiting ? 'Waiting...' : isDone ? 'Complete' : agent.statusText}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  {isDone ? (
                    <CheckCircle2 className="w-5 h-5 text-emerald-400" />
                  ) : isActive ? (
                    <Loader2 className={`w-5 h-5 ${agent.color} animate-spin`} />
                  ) : null}
                  <span className={`font-data-mono text-sm font-bold ${isDone ? 'text-emerald-400' : isActive ? agent.color : 'text-on-surface-variant'}`}>
                    {val}%
                  </span>
                </div>
              </div>
              
              {/* Progress Bar */}
              <div className="h-1.5 w-full bg-black/50 rounded-full overflow-hidden">
                <div 
                  className={`h-full ${agent.progressColor} transition-all duration-300 ease-out`}
                  style={{ width: `${val}%` }}
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
