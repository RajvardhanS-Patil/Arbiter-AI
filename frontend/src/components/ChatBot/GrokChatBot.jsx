import React, { useState, useRef, useEffect, useCallback } from 'react';
import { api } from '../../services/api';
import './GrokChatBot.css';
import { MessageSquare, X, Send, Maximize2, Minimize2, Sparkles } from 'lucide-react';

export const GrokChatBot = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([
    { role: 'assistant', content: 'Hello! I am your AI assistant. How can I help you analyze a claim today?' }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  
  // Dragging state
  const [position, setPosition] = useState({ x: window.innerWidth - 380, y: window.innerHeight - 600 });
  const [isDragging, setIsDragging] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const dragRef = useRef({ startX: 0, startY: 0, currentX: window.innerWidth - 380, currentY: window.innerHeight - 600 });
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isOpen, isMinimized]);

  // Handle Dragging
  const handleDragStart = (e) => {
    // Only drag from header
    if (!e.target.closest('.grok-chat-header')) return;
    
    setIsDragging(true);
    const clientX = e.clientX || (e.touches && e.touches[0].clientX);
    const clientY = e.clientY || (e.touches && e.touches[0].clientY);
    
    dragRef.current.startX = clientX;
    dragRef.current.startY = clientY;
  };

  const handleDragMove = useCallback((e) => {
    if (!isDragging) return;
    const clientX = e.clientX || (e.touches && e.touches[0].clientX);
    const clientY = e.clientY || (e.touches && e.touches[0].clientY);
    
    const dx = clientX - dragRef.current.startX;
    const dy = clientY - dragRef.current.startY;
    
    // Calculate new position bounded by window
    let newX = dragRef.current.currentX + dx;
    let newY = dragRef.current.currentY + dy;
    
    // Bounds checking
    const maxX = window.innerWidth - 350;
    const maxY = window.innerHeight - 100;
    
    newX = Math.max(0, Math.min(newX, maxX));
    newY = Math.max(0, Math.min(newY, maxY));

    setPosition({ x: newX, y: newY });
  }, [isDragging]);

  const handleDragEnd = useCallback(() => {
    if (!isDragging) return;
    setIsDragging(false);
    dragRef.current.currentX = position.x;
    dragRef.current.currentY = position.y;
  }, [isDragging, position]);

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
      window.removeEventListener('touchmove', handleDragEnd);
    }
    return () => {
      window.removeEventListener('mousemove', handleDragMove);
      window.removeEventListener('mouseup', handleDragEnd);
      window.removeEventListener('touchmove', handleDragMove);
      window.removeEventListener('touchend', handleDragEnd);
    };
  }, [isDragging, handleDragMove, handleDragEnd]);

  // Handle chat submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage = { role: 'user', content: input };
    const updatedMessages = [...messages, userMessage];
    setMessages(updatedMessages);
    setInput('');
    setIsLoading(true);

    try {
      // Exclude system message and any errors when sending to backend
      const historyToSync = updatedMessages.filter(m => m.role !== 'system' && m.role !== 'error');
      
      const response = await api.sendChatMessage(historyToSync);
      setMessages([...updatedMessages, { role: 'assistant', content: response.reply, model: response.model }]);
    } catch (err) {
      console.error("Chat error:", err);
      setMessages([...updatedMessages, { role: 'error', content: 'Failed to communicate with AI. Please try again.' }]);
    } finally {
      setIsLoading(false);
    }
  };

  if (!isOpen) {
    return (
      <button 
        className="grok-chat-fab" 
        onClick={() => setIsOpen(true)}
        aria-label="Open Chat"
      >
        <Sparkles className="w-6 h-6 text-on-primary" />
      </button>
    );
  }

  return (
    <div 
      className={`grok-chat-window ${isDragging ? 'dragging' : ''} ${isMinimized ? 'minimized' : ''}`}
      style={{ left: `${position.x}px`, top: `${position.y}px` }}
    >
      {/* Header (Draggable Area) */}
      <div 
        className="grok-chat-header"
        onMouseDown={handleDragStart}
        onTouchStart={handleDragStart}
      >
        <div className="flex items-center gap-2 pointer-events-none">
          <Sparkles className="w-5 h-5 text-primary" />
          <span className="font-bold text-on-surface">Verdictor AI</span>
        </div>
        <div className="flex items-center gap-1">
          <button 
            className="p-1 hover:bg-surface-variant rounded-md text-on-surface-variant transition-colors"
            onClick={(e) => { e.stopPropagation(); setIsMinimized(!isMinimized); }}
          >
            {isMinimized ? <Maximize2 className="w-4 h-4" /> : <Minimize2 className="w-4 h-4" />}
          </button>
          <button 
            className="p-1 hover:bg-error hover:text-on-error rounded-md text-on-surface-variant transition-colors"
            onClick={(e) => { e.stopPropagation(); setIsOpen(false); }}
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Chat Body (Hidden when minimized) */}
      {!isMinimized && (
        <>
          <div className="grok-chat-messages">
            {messages.map((msg, idx) => (
              <div key={idx} className={`chat-message ${msg.role}`}>
                <div className="chat-avatar">
                  {msg.role === 'user' ? 'U' : msg.role === 'error' ? '!' : <Sparkles className="w-4 h-4" />}
                </div>
                <div className="chat-bubble">
                  {msg.content}
                </div>
              </div>
            ))}
            {isLoading && (
              <div className="chat-message assistant">
                <div className="chat-avatar"><Sparkles className="w-4 h-4" /></div>
                <div className="chat-bubble typing-indicator">
                  <span></span><span></span><span></span>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          <form onSubmit={handleSubmit} className="grok-chat-input-area">
            <input 
              type="text" 
              placeholder="Ask a question..." 
              value={input}
              onChange={(e) => setInput(e.target.value)}
              disabled={isLoading}
            />
            <button type="submit" disabled={!input.trim() || isLoading}>
              <Send className="w-5 h-5" />
            </button>
          </form>
        </>
      )}
    </div>
  );
};
