import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { DebateArena } from '../components/DebateArena/DebateArena';
import { api } from '../services/api';

export const CourtPage = () => {
  const { sessionId } = useParams();
  const navigate = useNavigate();
  const [topic, setTopic] = useState('Loading session...');

  useEffect(() => {
    // Fetch session details to get the topic/query
    api.getSessionStatus(sessionId)
      .then(res => {
        setTopic(res.query || res.file_name || 'Active Fact-Check Session');
      })
      .catch(err => {
        console.error('Failed to load session details', err);
        setTopic('Unknown Topic');
      });
  }, [sessionId]);

  return (
    <div className="max-w-6xl mx-auto mb-16 select-none">
      <DebateArena sessionId={sessionId} topic={topic} />
    </div>
  );
};
