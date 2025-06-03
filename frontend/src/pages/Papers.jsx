import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';

function Papers() {
  const [papers, setPapers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    loadPapers();
  }, []);

  const loadPapers = async () => {
    try {
      setLoading(true);
      const response = await axios.get('/api/papers');
      setPapers(response.data);
    } catch (err) {
      setError('Failed to load papers: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!searchQuery.trim()) {
      loadPapers();
      return;
    }

    try {
      setLoading(true);
      const response = await axios.get(`/api/papers/search/${searchQuery}`);
      setPapers(response.data);
    } catch (err) {
      setError('Search failed: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-red-500">{error}</div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto px-4">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-4">Research Papers</h1>
        
        <form onSubmit={handleSearch} className="mb-6">
          <div className="flex gap-4">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search papers..."
              className="flex-1 px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button
              type="submit"
              className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              Search
            </button>
          </div>
        </form>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {papers.map((paper) => (
            <Link
              key={paper.id}
              to={`/paper/${paper.id}`}
              className="block bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow p-6"
            >
              <h2 className="text-xl font-semibold text-gray-900 mb-2">
                {paper.title}
              </h2>
              <p className="text-gray-600 mb-2">
                {paper.authors?.join(', ')}
              </p>
              {paper.metadata?.year && (
                <p className="text-gray-500 text-sm mb-2">
                  Published: {paper.metadata.year}
                </p>
              )}
              {paper.metadata?.abstract && (
                <p className="text-gray-700 line-clamp-3">
                  {paper.metadata.abstract}
                </p>
              )}
            </Link>
          ))}
        </div>

        {papers.length === 0 && (
          <div className="text-center text-gray-500 py-8">
            No papers found. Try a different search query or add some papers.
          </div>
        )}
      </div>
    </div>
  );
}

export default Papers; 