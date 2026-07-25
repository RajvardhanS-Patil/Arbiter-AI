import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useWebSocket } from '../../hooks/useWebSocket';
import { api } from '../../services/api';
import './DebateArena.css';

export const DebateArena = ({ sessionId, topic, onComplete }) => {
  const navigate = useNavigate();
  
  // Pipeline progress
  const [pipelinePercent, setPipelinePercent] = useState(5);
  const [agents, setAgents] = useState({
    orchestrator: { name: 'Orchestrator', status: 'WAITING' },
    investigator: { name: 'Investigator', status: 'WAITING' },
    verifier: { name: 'Verifier', status: 'WAITING' },
    devils_advocate: { name: "Devil's Advocate", status: 'WAITING' },
    judge: { name: 'Judge', status: 'WAITING' },
    synthesizer: { name: 'Synthesizer', status: 'WAITING' }
  });

  // Debate dialogue state
  const [dialogues, setDialogues] = useState([]); // {side, title, text, id}
  const [currentDialogue, setCurrentDialogue] = useState(null);
  const [isTyping, setIsTyping] = useState(false);
  const [verdictActive, setVerdictActive] = useState(false);
  const [reportReady, setReportReady] = useState(false);
  const [stats, setStats] = useState({ claims: 0, verified: 0, disputed: 0 });
  const [pipelineDone, setPipelineDone] = useState(false);

  // Queue system
  const queueRef = useRef([]);
  const isShowingRef = useRef(false);
  const dialogueIdRef = useRef(0);
  const introducedAgentsRef = useRef(new Set());

  // Draggable sidebar state
  const [sidebarPos, setSidebarPos] = useState({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState(false);
  const dragRef = useRef({ startX: 0, startY: 0, currentX: 0, currentY: 0 });

  const handleDragStart = (e) => {
    setIsDragging(true);
    dragRef.current.startX = e.clientX || (e.touches && e.touches[0].clientX);
    dragRef.current.startY = e.clientY || (e.touches && e.touches[0].clientY);
  };

  const handleDragMove = useCallback((e) => {
    if (!isDragging) return;
    const clientX = e.clientX || (e.touches && e.touches[0].clientX);
    const clientY = e.clientY || (e.touches && e.touches[0].clientY);
    
    const dx = clientX - dragRef.current.startX;
    const dy = clientY - dragRef.current.startY;
    
    setSidebarPos({ 
      x: dragRef.current.currentX + dx, 
      y: Math.max(0, dragRef.current.currentY + dy) 
    });
  }, [isDragging]);

  const handleDragEnd = useCallback(() => {
    if (!isDragging) return;
    setIsDragging(false);
    dragRef.current.currentX = sidebarPos.x;
    dragRef.current.currentY = sidebarPos.y;
  }, [isDragging, sidebarPos]);

  useEffect(() => {
    if (isDragging) {
      window.addEventListener('mousemove', handleDragMove);
      window.addEventListener('mouseup', handleDragEnd);
      window.addEventListener('touchmove', handleDragMove);
      window.addEventListener('touchend', handleDragEnd);
    } else {
      window.removeEventListener('mousemove', handleDragMove);
      window.removeEventListener('mouseup', handleDragEnd);
      window.removeEventListener('touchmove', handleDragMove);
      window.removeEventListener('touchend', handleDragEnd);
    }
    return () => {
      window.removeEventListener('mousemove', handleDragMove);
      window.removeEventListener('mouseup', handleDragEnd);
      window.removeEventListener('touchmove', handleDragMove);
      window.removeEventListener('touchend', handleDragEnd);
    };
  }, [isDragging, handleDragMove, handleDragEnd]);

  // Filler dialogues for when real AI events are slow
  const verifierFillers = [
    "Let me cross-reference this with official sources...",
    "Checking the publication date and data freshness...",
    "Verifying the statistical methodology used...",
    "Looking at peer-reviewed sources for confirmation...",
    "Assessing the credibility of this data point..."
  ];
  const advocateFillers = [
    "But have we considered the opposing evidence?",
    "The sample size in that study seems questionable...",
    "Correlation doesn't imply causation here...",
    "What about the selection bias in that source?",
    "I'd challenge the assumptions behind this claim..."
  ];

  // Show next dialogue from queue
  const showNext = useCallback(() => {
    if (queueRef.current.length === 0) {
      isShowingRef.current = false;
      setCurrentDialogue(null);
      return;
    }

    isShowingRef.current = true;
    const next = queueRef.current.shift();
    
    setIsTyping(true);
    setCurrentDialogue(next);

    // Show typing for 1s, then reveal text
    setTimeout(() => {
      setIsTyping(false);
    }, 1000);

    // Hold the dialogue for its duration, then show next
    const holdTime = next.duration || 4500;
    setTimeout(() => {
      showNext();
    }, holdTime + 1000);
  }, []);

  const enqueue = useCallback((side, title, text, duration = 4500) => {
    dialogueIdRef.current += 1;
    const item = { side, title, text, duration, id: dialogueIdRef.current };
    queueRef.current.push(item);
    setDialogues(prev => [...prev, item]);

    if (!isShowingRef.current) {
      showNext();
    }
  }, [showNext]);

  // Filler timer — keeps debate alive when backend is thinking
  useEffect(() => {
    const interval = setInterval(() => {
      if (!isShowingRef.current && queueRef.current.length === 0 && !pipelineDone && pipelinePercent > 10 && pipelinePercent < 95) {
        const useVerifier = Math.random() > 0.5;
        if (useVerifier) {
          const text = verifierFillers[Math.floor(Math.random() * verifierFillers.length)];
          enqueue('left', 'FACT VERIFIER', text, 3500);
        } else {
          const text = advocateFillers[Math.floor(Math.random() * advocateFillers.length)];
          enqueue('right', "DEVIL'S ADVOCATE", text, 3500);
        }
      }
    }, 7000);
    return () => clearInterval(interval);
  }, [pipelineDone, pipelinePercent, enqueue]);

  // Handle WebSocket events from the backend pipeline
  const handleWebSocketEvent = useCallback((event) => {
    const data = event.data || {};
    const metadata = data.metadata || {};
    const content = data.content || '';
    const fromAgent = data.from_agent || '';

    switch (event.event) {
      case 'pipeline_started':
        setPipelinePercent(10);
        updateAgentStatus('orchestrator', 'ACTIVE');
        enqueue('center', 'JUDGE', 'The fact-checking tribunal is now in session. Let the investigation begin.', 4000);
        break;

      case 'agent_started':
        updateAgentStatus(fromAgent, 'ACTIVE');
        adjustProgress(fromAgent, 'started');
        
        if (!introducedAgentsRef.current.has(fromAgent)) {
          introducedAgentsRef.current.add(fromAgent);
          if (fromAgent === 'investigator') {
            enqueue('center', 'JUDGE', 'Investigator, begin gathering evidence and extracting claims.', 3500);
          } else if (fromAgent === 'verifier') {
            enqueue('left', 'FACT VERIFIER', 'I will now systematically verify claims against credible sources.', 3500);
          } else if (fromAgent === 'devils_advocate') {
            enqueue('right', "DEVIL'S ADVOCATE", "My turn. I'll challenge these claims and find weaknesses.", 3500);
          } else if (fromAgent === 'judge') {
            enqueue('center', 'JUDGE', 'I will now weigh all evidence and issue verdicts.', 3500);
          } else if (fromAgent === 'synthesizer') {
            enqueue('center', 'JUDGE', 'The synthesizer is compiling the final report...', 3000);
          }
        }
        break;

      case 'agent_completed':
        updateAgentStatus(fromAgent, 'COMPLETED');
        adjustProgress(fromAgent, 'completed');
        
        if (fromAgent === 'investigator') {
          enqueue('center', 'JUDGE', `Investigation complete. ${content.includes('claims') ? content.split(':').pop().trim() : 'Claims extracted.'}`, 3000);
        } else if (fromAgent === 'synthesizer') {
          enqueue('center', 'JUDGE', 'Report compilation complete.', 3000);
        }
        // Do not enqueue for verifier/advocate/judge since they run in a loop per claim.
        break;

      case 'claim_created':
        setStats(prev => ({ ...prev, claims: prev.claims + 1 }));
        // Don't enqueue speech bubble here to avoid spam before the debate starts.
        break;

      case 'claim_verified':
        if (metadata.status === 'verified') {
          setStats(prev => ({ ...prev, verified: prev.verified + 1 }));
          const verifiedText = content.substring(content.indexOf(':') + 1).trim();
          enqueue('left', 'FACT VERIFIER', `This checks out: ${verifiedText}`, 4000);
        } else {
          enqueue('left', 'FACT VERIFIER', 'Verification failed or disputed. Evidence is insufficient.', 3500);
        }
        break;

      case 'claim_challenged':
        setStats(prev => ({ ...prev, disputed: prev.disputed + 1 }));
        const challengeText = content.substring(content.indexOf(':') + 1).trim();
        enqueue('right', "DEVIL'S ADVOCATE", `I challenge this! ${challengeText}`, 4500);
        break;

      case 'claim_judged':
        const verdictText = content.substring(content.indexOf('—') + 1).trim();
        enqueue('center', 'JUDGE', `Verdict: ${metadata.verdict.toUpperCase()}. ${verdictText}`, 4500);
        break;

      case 'agent_message':
        // General agent messages — show as dialogue from the appropriate side
        if (fromAgent === 'investigator' || fromAgent === 'verifier') {
          if (content && content.length > 5) {
            const shortContent = content.length > 300 ? content.substring(0, 300) + '...' : content;
            enqueue('left', 'FACT VERIFIER', shortContent, 4500);
          }
        } else if (fromAgent === 'devils_advocate') {
          if (content && content.length > 5) {
            const shortContent = content.length > 300 ? content.substring(0, 300) + '...' : content;
            enqueue('right', "DEVIL'S ADVOCATE", shortContent, 4500);
          }
        }
        break;

      case 'agent_progress':
        // Silently update progress, don't show dialogue for every progress tick
        break;

      case 'pipeline_completed':
      case 'report_ready':
        if (data.metadata && data.metadata.stats) {
          setStats(data.metadata.stats);
        }
        setPipelinePercent(100);
        setPipelineDone(true);
        updateAgentStatus('synthesizer', 'COMPLETED');
        
        // Clear remaining queue and show finale
        queueRef.current = [];
        isShowingRef.current = false;

        setTimeout(() => {
          setVerdictActive(true);
          enqueue('center', 'JUDGE', '⚖️ All evidence has been examined. I am ready to deliver the verdict.', 0);
          setTimeout(() => {
            setReportReady(true);
          }, 2500);
        }, 1500);
        break;

      case 'error':
        enqueue('center', 'SYSTEM', `⚠️ Error: ${content.substring(0, 100)}`, 5000);
        break;

      default:
        // Unknown event — ignore
        break;
    }
  }, [enqueue]);

  useWebSocket(sessionId === 'demo' ? null : sessionId, handleWebSocketEvent);

  // Demo mode
  useEffect(() => {
    if (sessionId !== 'demo') return;
    
    // Simulate pipeline start
    handleWebSocketEvent({ event: 'pipeline_started' });
    
    const sequence = [
      // Investigator finds claims
      { delay: 3000, e: { event: 'agent_started', data: { from_agent: 'investigator' } } },
      { delay: 6000, e: { event: 'agent_completed', data: { from_agent: 'investigator', content: 'Extracted 3 key claims from "India\'s Economy: Mixed Facts".' } } },
      
      // DEBATE 1
      { delay: 9000, e: { event: 'agent_started', data: { from_agent: 'verifier' } } },
      { delay: 11000, e: { event: 'agent_message', data: { from_agent: 'verifier', content: 'Claim 1: "India is the 5th largest economy in the world by nominal GDP."' } } },
      { delay: 15000, e: { event: 'agent_started', data: { from_agent: 'devils_advocate' } } },
      { delay: 16000, e: { event: 'agent_message', data: { from_agent: 'devils_advocate', content: 'Wait, I challenge this! Is it based on current data or outdated projections?' } } },
      { delay: 21000, e: { event: 'agent_message', data: { from_agent: 'verifier', content: 'I have cross-referenced this against the latest World Bank and IMF reports for 2023-2024. The data holds true.' } } },
      { delay: 27000, e: { event: 'agent_message', data: { from_agent: 'devils_advocate', content: 'I concede on this point. The nominal GDP figures align with international monetary tracking.' } } },
      
      { delay: 31000, e: { event: 'agent_started', data: { from_agent: 'judge' } } },
      { delay: 32000, e: { event: 'claim_judged', data: { metadata: { verdict: 'verified' }, content: 'The claim is factual and supported by credible institutions.' } } },
      
      // DEBATE 2
      { delay: 38000, e: { event: 'agent_message', data: { from_agent: 'verifier', content: 'Claim 2: "Agriculture contributes over 60% to India\'s GDP."' } } },
      { delay: 43000, e: { event: 'agent_message', data: { from_agent: 'devils_advocate', content: 'I strongly challenge this! That sounds like an employment statistic, not a GDP contribution.' } } },
      { delay: 49000, e: { event: 'agent_message', data: { from_agent: 'verifier', content: 'Let me double-check... The source text asserts this is the economic value output.' } } },
      { delay: 54000, e: { event: 'agent_message', data: { from_agent: 'devils_advocate', content: 'That is a hallucinated statistic. According to the Ministry of Statistics, agriculture contributes ~15-18% to the GDP. The 60% figure refers to the workforce dependent on it.' } } },
      
      { delay: 62000, e: { event: 'claim_judged', data: { metadata: { verdict: 'false' }, content: 'The document conflates employment data with GDP contribution. This is a severe factual error.' } } },

      // DEBATE 3
      { delay: 69000, e: { event: 'agent_message', data: { from_agent: 'verifier', content: 'Claim 3: "India has completely eliminated extreme poverty as of 2024."' } } },
      { delay: 75000, e: { event: 'agent_message', data: { from_agent: 'devils_advocate', content: 'Objection! Multidimensional poverty indexes still show millions living below the poverty line.' } } },
      { delay: 81000, e: { event: 'agent_message', data: { from_agent: 'verifier', content: 'The document cites a recent government report claiming a 0% rate in extreme poverty.' } } },
      { delay: 87000, e: { event: 'agent_message', data: { from_agent: 'devils_advocate', content: '"Extreme poverty" is a very specific World Bank metric ($1.90/day). While significantly reduced, saying it is "completely eliminated" is absolute and misleading.' } } },

      { delay: 95000, e: { event: 'claim_judged', data: { metadata: { verdict: 'false' }, content: 'The claim uses absolute terminology ("completely eliminated") which contradicts nuanced socioeconomic realities.' } } },

      // Conclusion
      { delay: 99000, e: { event: 'agent_completed', data: { from_agent: 'verifier' } } },
      { delay: 100000, e: { event: 'agent_completed', data: { from_agent: 'devils_advocate' } } },
      { delay: 101000, e: { event: 'agent_completed', data: { from_agent: 'judge' } } },
      { delay: 102000, e: { event: 'agent_started', data: { from_agent: 'synthesizer' } } },
      { delay: 105000, e: { event: 'report_ready', data: { metadata: { stats: { claims: 3, verified: 1, disputed: 2 } } } } }
    ];

    let timers = [];
    sequence.forEach((item) => {
      const timer = setTimeout(() => handleWebSocketEvent(item.e), item.delay);
      timers.push(timer);
    });

    return () => timers.forEach(clearTimeout);
  }, [sessionId, handleWebSocketEvent]);

  // Also poll session status periodically to update progress even if WS events are sparse
  useEffect(() => {
    if (!sessionId || pipelineDone || sessionId === 'demo') return;
    
    const pollInterval = setInterval(async () => {
      try {
        const status = await api.getSessionStatus(sessionId);
        if (status.status === 'completed') {
          setPipelinePercent(100);
          setPipelineDone(true);
          
          // If we didn't get the pipeline_completed WS event, trigger report ready
          if (!reportReady && !verdictActive) {
            queueRef.current = [];
            isShowingRef.current = false;
            setTimeout(() => {
              setVerdictActive(true);
              enqueue('center', 'JUDGE', '⚖️ The tribunal has concluded. The report is ready.', 0);
              setTimeout(() => setReportReady(true), 2500);
            }, 1000);
          }
        } else if (status.status === 'failed') {
          setPipelineDone(true);
          enqueue('center', 'SYSTEM', '❌ The pipeline encountered an error. Please try again.', 0);
        }
      } catch (err) {
        // Polling failed, that's OK
      }
    }, 8000);

    return () => clearInterval(pollInterval);
  }, [sessionId, pipelineDone, reportReady, verdictActive, enqueue]);

  const updateAgentStatus = (agentKey, status) => {
    setAgents(prev => ({
      ...prev,
      [agentKey]: { ...prev[agentKey], status }
    }));
  };

  const adjustProgress = (agent, stage) => {
    const map = {
      investigator: { started: 15, completed: 30 },
      verifier: { started: 35, completed: 55 },
      devils_advocate: { started: 58, completed: 75 },
      judge: { started: 78, completed: 90 },
      synthesizer: { started: 92, completed: 98 }
    };
    if (map[agent]?.[stage]) {
      setPipelinePercent(prev => Math.max(prev, map[agent][stage]));
    }
  };

  const getAgentBadge = (status) => {
    switch (status) {
      case 'ACTIVE': return <span className="badge active">ACTIVE</span>;
      case 'COMPLETED': return <span className="badge done">DONE</span>;
      default: return <span className="badge idle">WAITING</span>;
    }
  };

  return (
    <div className="w-full flex flex-col lg:flex-row gap-6 animate-fade-in relative">
      
      {/* Main Court Column */}
      <div className="flex-1 flex flex-col gap-6">
        <div className="text-left px-2 flex justify-between items-end">
          <div>
            <h3 className="font-headline-md text-on-surface mb-1 font-semibold text-2xl">
              Live Fact-Checking Arena
            </h3>
            <p className="text-on-surface-variant font-body-md truncate max-w-xl">
              Topic: "{topic || 'Uploaded Document'}"
            </p>
          </div>
          <div className="text-right">
            <span className="font-data-mono text-primary text-lg font-bold">{pipelinePercent}% COMPLETE</span>
          </div>
        </div>

        <div className="debate-arena relative shadow-2xl">
          <div className="debate-progress">
            <div className="debate-progress-fill" style={{ width: `${pipelinePercent}%` }}></div>
          </div>

          {/* Background */}
          <div className="court-pillars"></div>
          <div className="judge-bench"></div>
          <div className="bench"></div>

          {/* Characters */}
          <div className={`character verifier ${currentDialogue?.side === 'left' ? 'speaking' : ''}`}>
            <div className="char-label">Fact Verifier</div>
            <img src="/avatars/lawyer.avif" alt="Fact Verifier" className="avatar-img" />
          </div>

          <div className={`character advocate ${currentDialogue?.side === 'right' ? 'speaking' : ''}`}>
            <div className="char-label">Devil's Advocate</div>
            <img src="/avatars/bad.webp" alt="Devil's Advocate" className="avatar-img" />
          </div>

          <div className={`character judge ${verdictActive ? 'verdict-active' : ''}`}>
            <div className="char-label">The Arbiter</div>
            <img src="/avatars/judge.png" alt="Judge" className="avatar-img" />
            <div className="gavel-container">
              <div className="gavel-handle"></div>
              <div className="gavel-head"></div>
            </div>
          </div>

        {/* Speech Bubbles */}
        {currentDialogue && (
          <div className={`speech-bubble ${currentDialogue.side} show`}>
            <div className="bubble-title">{currentDialogue.title}</div>
            {isTyping ? (
              <div className="typing-indicator">
                <div className="typing-dot"></div>
                <div className="typing-dot"></div>
                <div className="typing-dot"></div>
              </div>
            ) : (
              <div className="speech-text leading-relaxed">{currentDialogue.text}</div>
            )}
          </div>
        )}

        {/* Verdict Overlay */}
        {reportReady && (
          <div className="absolute inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center animate-fade-in">
            <div className="bg-surface-container border border-white/20 rounded-2xl p-8 max-w-md w-full shadow-2xl text-center">
              <h2 className="text-3xl font-display-lg text-white mb-2">⚖️ Verdict Reached</h2>
              <p className="text-on-surface-variant mb-6">The fact-checking tribunal has concluded its analysis.</p>
              
              <div className="grid grid-cols-3 gap-4 mb-8">
                <div className="bg-surface-container-high rounded-xl p-4">
                  <div className="text-2xl font-bold text-blue-400">{stats.claims}</div>
                  <div className="text-[10px] text-on-surface-variant uppercase tracking-wider">Claims</div>
                </div>
                <div className="bg-surface-container-high rounded-xl p-4">
                  <div className="text-2xl font-bold text-emerald-400">{stats.verified}</div>
                  <div className="text-[10px] text-on-surface-variant uppercase tracking-wider">Verified</div>
                </div>
                <div className="bg-surface-container-high rounded-xl p-4">
                  <div className="text-2xl font-bold text-red-400">{stats.disputed}</div>
                  <div className="text-[10px] text-on-surface-variant uppercase tracking-wider">Disputed</div>
                </div>
              </div>

              <button 
                onClick={() => navigate(`/report/${sessionId}`)}
                className="w-full bg-primary text-on-primary py-4 rounded-xl font-bold text-lg hover:bg-primary-container hover:text-on-primary-container transition-colors"
              >
                View Full Fact-Check Report
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Dialogue History (scrollable transcript below the arena) */}
      {dialogues.length > 0 && (
        <div className="glass-panel rounded-xl p-4 max-h-48 overflow-y-auto">
          <h4 className="font-label-caps text-[10px] text-on-surface-variant mb-2">DEBATE TRANSCRIPT</h4>
          {dialogues.slice(-10).map((d) => (
            <div key={d.id} className={`text-[12px] mb-1 ${d.side === 'left' ? 'text-blue-300' : d.side === 'right' ? 'text-red-300' : 'text-yellow-300'}`}>
              <span className="font-bold">{d.title}:</span> {d.text}
            </div>
          ))}
        </div>
      )}
      </div>

      {/* Sidebar Column */}
      <div className="w-full lg:w-64 flex-shrink-0">
        <div 
          className="debate-sidebar shadow-2xl"
        >
          <div className="flex items-center justify-between mb-3 border-b border-white/10 pb-2">
            <h4 className="font-label-caps text-[10px] text-on-surface-variant">AGENT PIPELINE</h4>
            <div className="flex gap-1 opacity-50">
              <div className="w-1 h-1 bg-white rounded-full"></div>
              <div className="w-1 h-1 bg-white rounded-full"></div>
              <div className="w-1 h-1 bg-white rounded-full"></div>
            </div>
          </div>
          {Object.entries(agents).map(([key, agent]) => (
            <div key={key} className="agent-status-item">
              <span className="agent-name">{agent.name}</span>
              {getAgentBadge(agent.status)}
            </div>
          ))}
          <div className="mt-4 pt-3 border-t border-white/10">
            <div className="flex justify-between text-[11px] mb-1">
              <span className="text-on-surface-variant">Claims:</span>
              <span className="text-white font-data-mono">{stats.claims}</span>
            </div>
            <div className="flex justify-between text-[11px] mb-1">
              <span className="text-emerald-400">Verified:</span>
              <span className="text-white font-data-mono">{stats.verified}</span>
            </div>
            <div className="flex justify-between text-[11px]">
              <span className="text-red-400">Disputed:</span>
              <span className="text-white font-data-mono">{stats.disputed}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
