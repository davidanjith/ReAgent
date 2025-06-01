import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import CirclePacking from '../graph/CirclePacking';

function PaperView() {
  const { paperId } = useParams();
  const [paper, setPaper] = useState(null);
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [qaHistory, setQaHistory] = useState([]);

  useEffect(() => {
    // Load paper data
    const loadPaper = async () => {
      try {
        const response = await fetch(`http://localhost:8000/api/papers/${paperId}`);
        if (!response.ok) throw new Error('Failed to load paper');
        const data = await response.json();
        setPaper(data);
      } catch (err) {
        setError(err.message);
      }
    };
    loadPaper();
  }, [paperId]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!question.trim()) return;

    setLoading(true);
    setError(null);

    try {
      const response = await fetch('http://localhost:8000/api/papers/ask', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          question,
          paper_id: paperId,
        }),
      });

      if (!response.ok) throw new Error('Failed to get answer');

      const data = await response.json();
      if (data.success) {
        setAnswer(data.answer);
        setQaHistory(prev => [...prev, { question, answer: data.answer }]);
        setQuestion('');
      } else {
        throw new Error(data.error || 'Failed to get answer');
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (!paper) {
    return <div className="text-center">Loading...</div>;
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
      {/* Paper Content */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-2xl font-bold mb-4">{paper.metadata.title}</h2>
        <div className="prose max-w-none">
          {Object.entries(paper.content).map(([page, text]) => (
            <div key={page} className="mb-4">
              <h3 className="text-lg font-semibold mb-2">{page}</h3>
              <p className="text-gray-700">{text}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Q&A Section */}
      <div className="space-y-6">
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-xl font-bold mb-4">Ask Questions</h3>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <textarea
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                placeholder="Ask a question about the paper..."
                className="w-full px-3 py-2 border border-gray-300 rounded-md"
                rows={3}
              />
            </div>
            {error && (
              <div className="text-red-600 text-sm">{error}</div>
            )}
            <button
              type="submit"
              disabled={loading || !question.trim()}
              className={`w-full py-2 px-4 rounded-md text-white font-medium
                ${loading || !question.trim()
                  ? 'bg-gray-400 cursor-not-allowed'
                  : 'bg-blue-600 hover:bg-blue-700'
                }`}
            >
              {loading ? 'Thinking...' : 'Ask'}
            </button>
          </form>
        </div>

        {/* Q&A History */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-xl font-bold mb-4">Q&A History</h3>
          <div className="space-y-4">
            {qaHistory.map((qa, index) => (
              <div key={index} className="border-b pb-4 last:border-b-0">
                <p className="font-medium text-gray-900">Q: {qa.question}</p>
                <p className="mt-2 text-gray-700">A: {qa.answer}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Cluster Visualization */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-xl font-bold mb-4">Question Clusters</h3>
          <div className="h-96">
            <CirclePacking data={qaHistory} />
          </div>
        </div>
      </div>
    </div>
  );
}

export default PaperView; 