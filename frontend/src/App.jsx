import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Layout } from './components/Layout/Layout';
import { HomePage } from './pages/HomePage';
import { ObservatoryPage } from './pages/ObservatoryPage';
import { ReportPage } from './pages/ReportPage';
import { CourtPage } from './pages/CourtPage';
import { HistoryPage } from './pages/HistoryPage';

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/court/:sessionId" element={<CourtPage />} />
          <Route path="/observatory/:sessionId" element={<ObservatoryPage />} />
          <Route path="/report/:sessionId" element={<ReportPage />} />
          <Route path="/history" element={<HistoryPage />} />
        </Routes>
      </Layout>
    </Router>
  );
}

export default App;
