import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Search, Shield, HelpCircle, FileText, CheckCircle, RefreshCw, Send, Settings, BarChart2 } from 'lucide-react';
import { api } from '../services/api';
import { useWebSocket } from '../hooks/useWebSocket';

export const ObservatoryPage = () => {
  const { sessionId } = useParams();
  const navigate = useNavigate();
  const [session, setSession] = useState(null);
  const [messages, setMessages] = useState([]);
  const [interrogationInput, setInterrogationInput] = useState('');
  const [claimsCount, setClaimsCount] = useState(0);
  const [verifiedCount, setVerifiedCount] = useState(0);
  const [sourcesCount, setSourcesCount] = useState(0);
  const [pipelinePercent, setPipelinePercent] = useState(10);
  const messagesEndRef = useRef(null);

  // Define agents based on DESIGN.md & Stitch screen
  const [agents, setAgents] = useState({
    orchestrator: { name: 'Orchestrator', status: 'IDLE', desc: 'Managing node flow and task distribution.', avatar: 'https://lh3.googleusercontent.com/aida-public/AB6AXuB5VjRy0HTQrlD9z9EOFKUOIyn8VU9t8KC3IL5f8hXE68ml3srrkczfD0XuMDTE_vuAebAyL51HvErWmiN93L_k8sORVPmHRzQ8Wlk7XhwxjXpYA66ERmkbyoK7x3P0uX080YvVV5nLG1PB_pwsh3FM4aw62zJxR2Lh0uoFTCwo2L9kiRK9-I_dYca53T611LXvPtfpGS2Y6Zsdx-MQofSkU5_WfFM56Us5_31DYra_Fs6VA-0x7KQwsZrCYvmiwU8tPZn4--DbSGw', progress: 0 },
    investigator: { name: 'Investigator', status: 'WAITING', desc: 'Extracting source entities from raw text.', avatar: 'https://lh3.googleusercontent.com/aida-public/AB6AXuAzcX6GnrJIa3samzBt1QEr0xl7lYK8f6TWI6n_4nYSm7X-l4Z7yNrg2rDNaqBFtbU3jLtQ_Q39ccwjfXXK2_lWpYYs7CSgoS9FcGauDcMovyTf-GoEgxMOYLxmhVjPtnEywNMKa7q2RfCKitjw5_fyRyFp1s6Wbx8Uj5yhCcpm-geV2MHTA_5obY4gJ5D11dreaiSmWrIIU0N2lVvxoM1rEANC401qXV7N1jzqmj4gTC0MWnAoqaO-Laob_AJlpphgml3zYP3QKeM', progress: 0 },
    verifier: { name: 'Verifier', status: 'WAITING', desc: 'Cross-referencing claims against established data.', avatar: 'https://lh3.googleusercontent.com/aida-public/AB6AXuB5_sQtmepe6AKzlhXlxGt1WFrr_L7w6CMcpTDx-0bNOw_o1vrxD1H7epkut0Fomo2x6UeBebRxVuKlGfCid9qJvR3iJvjPLqNWv29GDSoHKE5U5CAjqqsHGipkbdrfZ0HhoZjXxOaTloiaEH_mQcgghzDfxdA6mXUPOTGjcgJZ24p22616tckV0BwVsWRRRQnYCwu35z_2kjpTeKfOEzkgCyIbr_fXt31-6Ola99X6Wltjw6gg8scmPl0hUxymE6jX5_sJPkskovo', progress: 0 },
    devils_advocate: { name: "Devil's Advocate", status: 'WAITING', desc: 'Stress-testing arguments for logical fallacies.', avatar: 'https://lh3.googleusercontent.com/aida-public/AB6AXuD5ek_rkmFqPWAUm8K5UtppVTKpMedlyeiuCz6HMPJG3k7-JxIJk_QTihMZ4jtjQ6W2Y9uq-Mi2b8nnWaouc6wcxw5NP0E1gNCTA0mux0I2l5CzEmRGJ5Gm_hyBU3XiyyTcBUEPswRKpN9B62aR15DCGU3QqSzzn2EjJbm8AXha1iO6WPbttoQGckIoc3ftblS3niuO8YBuNXupZWBLYf5wDjFGGtDHOskj42WTsegXlmNbw7QzlQsykybVPCD2M9XjsgVvtOOt1Y8', progress: 0 },
    judge: { name: 'Judge', status: 'WAITING', desc: 'Weighting evidence to form final verdict.', avatar: 'https://lh3.googleusercontent.com/aida-public/AB6AXuBf4_TbNBMAX50l7fs7vj0L-GjKeJxh3Quz1Og76PIYLaVAOrPRMFgsMa7a66b6SEN6jSVEGd27eNKpUh2e0_r-igAKyEE4w_q3zu8T2IxRVy5EuKvajvFHa_NgIYHiZGdYgv0WjEyeo7SuljYCL1ii0T-zm-GkjdC_zk72QRx0ATW5N11TjdtR2wYkbqCHnKOCj3GOvk0soelnAsEBaevmnWOzRzeDRYXlhVzlvva_MG0occI1TgjpuEalrZZ0GwLBhiNLtjdeTK0', progress: 0 },
    synthesizer: { name: 'Synthesizer', status: 'WAITING', desc: 'Generating human-readable intelligence report.', avatar: 'https://lh3.googleusercontent.com/aida-public/AB6AXuAV579oXx-MMNcuxYA0GftMLW7bj1Bay5gikd0prfROcpN8HLnEvIlYXz5reyenRIVI3QeqO6Fw1TUvmq-XDYSmkcBSGazHyndC_KGLz9O_ra8k6yjoSerHUb7ufPa8G_vlQAJIX8tcoPtlGZGQTmOa5cnY19GGfcrmLguOvm7ZJF4-JTsVjNv1Gfz3xiKQ95MnkVrVOCPrpZis0W1KfIBavOd6EU7o5_DpuNwHPRoA_7v40IBRIHwIM0u0y3AocIZ0nltN7l1u7As', progress: 0 }
  });

  // Pull initial DB history
  useEffect(() => {
    if (!sessionId) return;
    api.getSessionStatus(sessionId)
      .then(res => {
        setSession(res);
        setClaimsCount(res.claims_found || 0);
        setVerifiedCount(res.claims_verified || 0);
        updateAgentStatuses(res);
      })
      .catch(console.error);

    // Get sources
    api.getSessionSources(sessionId)
      .then(res => setSourcesCount(res.length || 0))
      .catch(() => {});
  }, [sessionId]);

  // Scroll to bottom of message logs
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // WebSocket event processing
  const handleWebSocketEvent = (event) => {
    console.log('WS Event:', event);

    // Add to message logs
    const timestampStr = new Date().toLocaleTimeString();
    setMessages(prev => [
      ...prev,
      {
        id: event.data.id || Math.random().toString(),
        from: event.data.from_agent?.toUpperCase() || 'SYSTEM',
        time: timestampStr,
        content: event.data.content,
        type: event.data.message_type
      }
    ]);

    // Handle updates based on event type
    const data = event.data;
    const metadata = data.metadata || {};

    if (event.event === 'pipeline_started') {
      setPipelinePercent(10);
      updateAgentStatus('orchestrator', 'ACTIVE');
    } else if (event.event === 'agent_started') {
      const agent = data.from_agent;
      updateAgentStatus(agent, 'ACTIVE');
      setAgentProgress(agent, 10);
      adjustPipelineProgress(agent, 'started');
    } else if (event.event === 'agent_progress') {
      const agent = data.from_agent;
      const progress = metadata.progress || 0;
      setAgentProgress(agent, progress);
    } else if (event.event === 'agent_completed') {
      const agent = data.from_agent;
      updateAgentStatus(agent, 'COMPLETED');
      setAgentProgress(agent, 100);
      adjustPipelineProgress(agent, 'completed');
    } else if (event.event === 'claim_created') {
      setClaimsCount(prev => prev + 1);
    } else if (event.event === 'claim_verified') {
      if (metadata.status === 'verified') {
        setVerifiedCount(prev => prev + 1);
      }
    } else if (event.event === 'report_ready' || event.event === 'pipeline_completed') {
      setPipelinePercent(100);
      // Auto navigation to Report page after 1.5 seconds
      setTimeout(() => {
        navigate(`/report/${sessionId}`);
      }, 1500);
    }
  };

  const { send } = useWebSocket(sessionId, handleWebSocketEvent);

  const updateAgentStatus = (agentKey, status) => {
    setAgents(prev => ({
      ...prev,
      [agentKey]: {
        ...prev[agentKey],
        status
      }
    }));
  };

  const setAgentProgress = (agentKey, progress) => {
    setAgents(prev => ({
      ...prev,
      [agentKey]: {
        ...prev[agentKey],
        progress
      }
    }));
  };

  const updateAgentStatuses = (statusRes) => {
    const progress = statusRes.progress || {};
    const current = statusRes.current_agent;
    
    setAgents(prev => {
      const newAgents = { ...prev };
      Object.keys(newAgents).forEach(k => {
        const state = progress[k] || 'pending';
        if (state === 'completed') {
          newAgents[k].status = 'COMPLETED';
          newAgents[k].progress = 100;
        } else if (state === 'processing' || k === current) {
          newAgents[k].status = 'ACTIVE';
          newAgents[k].progress = 40;
        } else {
          newAgents[k].status = 'WAITING';
          newAgents[k].progress = 0;
        }
      });
      return newAgents;
    });

    // Approximate overall progress percent
    if (statusRes.status === 'completed') {
      setPipelinePercent(100);
    } else if (current === 'investigator') {
      setPipelinePercent(20);
    } else if (current === 'verifier') {
      setPipelinePercent(40);
    } else if (current === 'devils_advocate') {
      setPipelinePercent(60);
    } else if (current === 'judge') {
      setPipelinePercent(80);
    } else if (current === 'synthesizer') {
      setPipelinePercent(95);
    }
  };

  const adjustPipelineProgress = (agent, stage) => {
    const percents = {
      investigator: { started: 15, completed: 30 },
      verifier: { started: 35, completed: 55 },
      devils_advocate: { started: 60, completed: 75 },
      judge: { started: 80, completed: 90 },
      synthesizer: { started: 92, completed: 98 }
    };
    if (percents[agent]) {
      setPipelinePercent(percents[agent][stage]);
    }
  };

  const handleInterrogate = () => {
    if (!interrogationInput.trim()) return;
    // Broadcast user prompt over websocket
    send({
      type: 'interrogation',
      content: interrogationInput,
      timestamp: new Date().toISOString()
    });
    
    // Add locally to list
    setMessages(prev => [
      ...prev,
      {
        id: Math.random().toString(),
        from: 'USER',
        time: new Date().toLocaleTimeString(),
        content: interrogationInput,
        type: 'user'
      }
    ]);
    setInterrogationInput('');
  };

  const getAgentBadge = (status) => {
    switch (status) {
      case 'ACTIVE':
        return (
          <span className="font-label-caps text-[10px] px-2 py-1 bg-primary-container/30 rounded text-primary border border-primary/20">
            ACTIVE
          </span>
        );
      case 'COMPLETED':
        return (
          <span className="font-label-caps text-[10px] px-2 py-1 bg-emerald-500/20 text-emerald-400 border border-emerald-500/10 rounded">
            DONE
          </span>
        );
      case 'WAITING':
      default:
        return (
          <span className="font-label-caps text-[10px] px-2 py-1 bg-surface-container-high rounded text-on-surface-variant">
            WAITING
          </span>
        );
    }
  };

  return (
    <div className="select-none">
      {/* Pipeline Header */}
      <section className="mb-8">
        <div className="flex justify-between items-end mb-4">
          <div>
            <h3 className="font-headline-md text-on-surface mb-1 font-semibold text-2xl">
              Live Interrogation Pipeline
            </h3>
            <p className="text-on-surface-variant font-body-md">
              Interpreting research facts and analyzing contradictions: "{session?.query}"
            </p>
          </div>
          <div className="text-right">
            <span className="font-data-mono text-secondary text-lg font-bold">{pipelinePercent}% COMPLETE</span>
          </div>
        </div>
        <div className="w-full h-2 bg-surface-container-highest rounded-full overflow-hidden relative">
          <div 
            className="absolute top-0 left-0 h-full bg-primary-container transition-all duration-1000" 
            style={{ width: `${pipelinePercent}%` }}
          ></div>
          <div className="marching-ants absolute top-0 left-0 h-full opacity-30 w-full"></div>
        </div>
        
        <div className="flex items-center mt-6 gap-4 font-label-caps text-label-caps text-[12px]">
          <div className={`flex items-center gap-2 ${pipelinePercent >= 30 ? 'text-emerald-400' : 'text-primary'}`}>
            <Search className="w-4 h-4" /> Investigating
          </div>
          <div className="w-12 h-[1px] bg-outline-variant"></div>
          <div className={`flex items-center gap-2 ${pipelinePercent >= 80 ? 'text-emerald-400' : pipelinePercent >= 30 ? 'text-primary' : 'text-on-surface-variant opacity-30'}`}>
            <Shield className="w-4 h-4" /> Verifying & Debating
          </div>
          <div className="w-12 h-[1px] bg-outline-variant"></div>
          <div className={`flex items-center gap-2 ${pipelinePercent >= 98 ? 'text-emerald-400' : 'text-on-surface-variant opacity-30'}`}>
            <CheckCircle className="w-4 h-4" /> Finalizing
          </div>
        </div>
      </section>

      {/* Main Workspace Split */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-gutter items-start">
        {/* Left: Agent Grid (2x3) */}
        <div className="lg:col-span-7 grid grid-cols-1 sm:grid-cols-2 gap-4">
          {Object.entries(agents).map(([key, agent]) => {
            const isActive = agent.status === 'ACTIVE';
            return (
              <div 
                key={key}
                className={`glass-card rounded-xl p-6 transition-all ${
                  isActive 
                    ? 'border-primary-container/40 bg-primary-container/5 active-glow ring-1 ring-primary-container/30' 
                    : 'hover:translate-y-[-4px]'
                }`}
              >
                <div className="flex justify-between items-start mb-4">
                  <div className={`w-12 h-12 rounded-full border-2 p-0.5 ${isActive ? 'border-primary' : 'border-primary/20'}`}>
                    <img 
                      className="w-full h-full rounded-full object-cover" 
                      src={agent.avatar}
                      alt={agent.name}
                    />
                  </div>
                  {getAgentBadge(agent.status)}
                </div>
                <h4 className={`font-body-lg font-semibold ${isActive ? 'text-primary' : 'text-on-surface'}`}>{agent.name}</h4>
                <p className="text-on-surface-variant text-sm mt-1">{agent.desc}</p>
                
                {agent.progress > 0 && agent.progress < 100 && (
                  <div className="mt-4 flex items-center gap-2">
                    <div className="flex-1 h-1 bg-surface-container-highest rounded-full overflow-hidden">
                      <div className="h-full bg-primary transition-all duration-300" style={{ width: `${agent.progress}%` }}></div>
                    </div>
                    <span className="font-data-mono text-[10px] text-primary">{agent.progress}%</span>
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {/* Right: Live Message Stream */}
        <div className="lg:col-span-5 h-[620px] flex flex-col glass-card rounded-2xl overflow-hidden border border-white/10">
          <div className="px-6 py-4 border-b border-white/10 flex justify-between items-center bg-surface-container-low/50">
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 bg-secondary rounded-full animate-pulse"></div>
              <h5 className="font-label-caps text-label-caps">Live Message Stream</h5>
            </div>
            <Settings className="w-4 h-4 text-on-surface-variant cursor-pointer hover:text-primary transition-colors" />
          </div>

          <div className="flex-1 p-6 overflow-y-auto space-y-6">
            {messages.map((msg) => (
              <div key={msg.id} className="flex gap-4 items-start animate-fade-in">
                <div className="w-8 h-8 rounded-full bg-surface-container-high border border-white/10 flex items-center justify-center text-primary font-bold text-xs">
                  {msg.from[0]}
                </div>
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <span className={`font-label-caps text-[11px] ${msg.from === 'USER' ? 'text-secondary' : 'text-primary'}`}>{msg.from}</span>
                    <span className="text-[10px] text-on-surface-variant opacity-50">{msg.time}</span>
                  </div>
                  <div className={`p-3 rounded-tr-xl rounded-b-xl border ${msg.from === 'USER' ? 'bg-secondary-container/10 border-secondary/20' : 'bg-surface-container-high/40 border-white/5'}`}>
                    <p className="text-sm font-body-md leading-relaxed">{msg.content}</p>
                  </div>
                </div>
              </div>
            ))}
            {agents.verifier.status === 'ACTIVE' && (
              <div className="flex gap-4 items-start">
                <div className="w-8 h-8 rounded-full bg-surface-container-high border border-white/10 flex items-center justify-center text-primary font-bold text-xs animate-pulse">
                  V
                </div>
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="font-label-caps text-[11px] text-primary">VERIFIER</span>
                    <span className="text-[10px] text-on-surface-variant opacity-50">Active</span>
                  </div>
                  <div className="bg-primary-container/10 p-3 rounded-tr-xl rounded-b-xl border border-primary/20">
                    <p className="text-sm font-body-md leading-relaxed">Processing queries in parallel...</p>
                    <div className="mt-2 flex gap-1">
                      <div className="w-1 h-1 bg-primary rounded-full animate-bounce"></div>
                      <div className="w-1 h-1 bg-primary rounded-full animate-bounce [animation-delay:0.2s]"></div>
                      <div className="w-1 h-1 bg-primary rounded-full animate-bounce [animation-delay:0.4s]"></div>
                    </div>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          <div className="p-4 bg-surface-container-lowest/80 border-t border-white/10">
            <div className="relative">
              <input 
                className="w-full bg-surface-container-high border-none rounded-xl py-3 pl-4 pr-12 text-sm focus:ring-1 focus:ring-primary-container focus:outline-none transition-all text-white placeholder-on-surface-variant/40" 
                placeholder="Interrogate the pipeline..." 
                type="text"
                value={interrogationInput}
                onChange={(e) => setInterrogationInput(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleInterrogate()}
              />
              <button 
                onClick={handleInterrogate}
                className="absolute right-2 top-1/2 -translate-y-1/2 p-1.5 text-primary hover:bg-primary-container/20 rounded-lg transition-colors"
              >
                <Send className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Live Stats Bottom Right */}
      <div className="fixed bottom-24 md:bottom-8 right-margin-mobile md:right-margin-desktop z-30">
        <div className="glass-card rounded-2xl p-4 flex gap-6 border-secondary/20 bloom-purple">
          <div className="flex flex-col">
            <span className="font-label-caps text-[10px] text-on-surface-variant">CLAIMS</span>
            <span className="font-data-mono text-xl text-primary font-bold">{claimsCount}</span>
          </div>
          <div className="w-[1px] h-full bg-white/10 self-stretch"></div>
          <div className="flex flex-col">
            <span className="font-label-caps text-[10px] text-on-surface-variant">VERIFIED</span>
            <span className="font-data-mono text-xl text-secondary font-bold">{verifiedCount}</span>
          </div>
          <div className="w-[1px] h-full bg-white/10 self-stretch"></div>
          <div className="flex flex-col">
            <span className="font-label-caps text-[10px] text-on-surface-variant">SOURCES</span>
            <span className="font-data-mono text-xl text-tertiary font-bold">{sourcesCount}</span>
          </div>
        </div>
      </div>
    </div>
  );
};
export { }
