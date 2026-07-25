/**
 * Arbiter AI — API Client Service
 * Handles making requests to the FastAPI backend.
 */

const BASE_URL = '/api/v1';

export const api = {
  /**
   * Start a new research session.
   */
  startResearch: async (query, depth = 'standard', maxClaims = 15, enableDebate = true, enableMultiModel = true) => {
    const response = await fetch(`${BASE_URL}/research`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query, depth, max_claims: maxClaims, enable_debate: enableDebate, enable_multi_model: enableMultiModel })
    });
    if (!response.ok) throw new Error('Failed to start research');
    return response.json();
  },

  /**
   * Upload a document for verification.
   */
  uploadDocument: async (file, query = '', depth = 'standard') => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('depth', depth);
    if (query && query.trim() !== '') {
      formData.append('query', query.trim());
    }
    
    const response = await fetch(`${BASE_URL}/upload/verify`, {
      method: 'POST',
      body: formData
    });
    if (!response.ok) throw new Error('Failed to upload document');
    return response.json();
  },

  /**
   * Get progress/status of a session.
   */
  getSessionStatus: async (sessionId) => {
    const response = await fetch(`${BASE_URL}/research/${sessionId}`);
    if (!response.ok) throw new Error('Failed to get session status');
    return response.json();
  },

  /**
   * Retrieve all claims with metadata for a session.
   */
  getSessionClaims: async (sessionId) => {
    const response = await fetch(`${BASE_URL}/research/${sessionId}/claims`);
    if (!response.ok) throw new Error('Failed to get claims');
    return response.json();
  },

  /**
   * Retrieve contradictions (matrix + topics) for a session.
   */
  getSessionContradictions: async (sessionId) => {
    const response = await fetch(`${BASE_URL}/research/${sessionId}/contradictions`);
    if (!response.ok) throw new Error('Failed to get contradictions');
    return response.json();
  },

  /**
   * Retrieve all sources collected during the session.
   */
  getSessionSources: async (sessionId) => {
    const response = await fetch(`${BASE_URL}/research/${sessionId}/sources`);
    if (!response.ok) throw new Error('Failed to get sources');
    return response.json();
  },

  /**
   * Retrieve adversarial debate logs for the claims.
   */
  getSessionDebates: async (sessionId) => {
    const response = await fetch(`${BASE_URL}/research/${sessionId}/debate`);
    if (!response.ok) throw new Error('Failed to get debates');
    return response.json();
  },

  /**
   * Retrieve the final compiled report metadata and summary.
   */
  getReport: async (sessionId) => {
    const response = await fetch(`${BASE_URL}/reports/${sessionId}`);
    if (!response.ok) throw new Error('Failed to get report');
    return response.json();
  },

  /**
   * Export the report in JSON or Markdown.
   */
  exportReport: async (sessionId, format = 'markdown') => {
    const response = await fetch(`${BASE_URL}/reports/${sessionId}/export?format=${format}`);
    if (!response.ok) throw new Error('Failed to export report');
    return response.json();
  },

  /**
   * Get all past sessions.
   */
  getSessions: async (limit = 20, offset = 0) => {
    const response = await fetch(`${BASE_URL}/sessions?limit=${limit}&offset=${offset}`);
    if (!response.ok) throw new Error('Failed to list sessions');
    return response.json();
  },

  /**
   * Delete a session.
   */
  deleteSession: async (sessionId) => {
    const response = await fetch(`${BASE_URL}/sessions/${sessionId}`, {
      method: 'DELETE'
    });
    if (!response.ok) throw new Error('Failed to delete session');
    return response.json();
  }
};
