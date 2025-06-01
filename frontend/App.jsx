import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Home from './pages/Home';
import PaperView from './pages/PaperView';
import ClusterView from './pages/ClusterView';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-100">
        <Navbar />
        <main className="container mx-auto px-4 py-8">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/paper/:paperId" element={<PaperView />} />
            <Route path="/clusters" element={<ClusterView />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App; 