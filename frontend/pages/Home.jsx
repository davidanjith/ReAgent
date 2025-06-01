import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

function Home() {
  const [arxivId, setArxivId] = useState('');
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setArxivId('');
  };

  const handleArxivIdChange = (e) => {
    setArxivId(e.target.value);
    setFile(null);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      let response;
      if (file) {
        const formData = new FormData();
        formData.append('file', file);
        response = await fetch('http://localhost:8000/api/papers/upload', {
          method: 'POST',
          body: formData,
        });
      } else if (arxivId) {
        response = await fetch(`http://localhost:8000/api/papers/arxiv/${arxivId}`);
      } else {
        throw new Error('Please provide either a file or arXiv ID');
      }

      if (!response.ok) {
        throw new Error('Failed to process paper');
      }

      const data = await response.json();
      navigate(`/paper/${data.source}`);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto">
      <h1 className="text-3xl font-bold text-center mb-8">
        Research Paper Companion
      </h1>

      <div className="bg-white rounded-lg shadow-md p-6">
        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Upload PDF
            </label>
            <input
              type="file"
              accept=".pdf"
              onChange={handleFileChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md"
            />
          </div>

          <div className="relative">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-gray-300"></div>
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-2 bg-white text-gray-500">OR</span>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              arXiv ID
            </label>
            <input
              type="text"
              value={arxivId}
              onChange={handleArxivIdChange}
              placeholder="e.g., 1706.03762"
              className="w-full px-3 py-2 border border-gray-300 rounded-md"
            />
          </div>

          {error && (
            <div className="text-red-600 text-sm">{error}</div>
          )}

          <button
            type="submit"
            disabled={loading || (!file && !arxivId)}
            className={`w-full py-2 px-4 rounded-md text-white font-medium
              ${loading || (!file && !arxivId)
                ? 'bg-gray-400 cursor-not-allowed'
                : 'bg-blue-600 hover:bg-blue-700'
              }`}
          >
            {loading ? 'Processing...' : 'Continue'}
          </button>
        </form>
      </div>
    </div>
  );
}

export default Home; 