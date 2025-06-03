import React, { useState, useEffect } from 'react';
import { CirclePacking, KnowledgeGraph } from '../graph';

function ClusterView() {
  const [clusters, setClusters] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeView, setActiveView] = useState('circle'); // 'circle' or 'graph'

  useEffect(() => {
    const fetchClusters = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/clusters');
        const data = await response.json();
        setClusters(data);
      } catch (error) {
        console.error('Error fetching clusters:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchClusters();
  }, []);

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-gray-600">Loading...</div>
      </div>
    );
  }

  // Use clusters data if available, otherwise use sample data
  const visualizationData = clusters.length > 0 ? clusters : [
    {
      question: "What is the main contribution?",
      answer: "The paper introduces a new method for...",
      timestamp: "2024-01-01T10:00:00Z",
      value: 1
    },
    {
      question: "How does it compare to previous work?",
      answer: "The method improves upon previous approaches by...",
      timestamp: "2024-01-01T11:00:00Z",
      value: 2
    }
  ];

  return (
    <div className="max-w-6xl mx-auto">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold text-gray-900">
          Knowledge Clusters
        </h1>
        <div className="flex space-x-4">
          <button
            onClick={() => setActiveView('circle')}
            className={`px-4 py-2 rounded-md ${
              activeView === 'circle'
                ? 'bg-blue-500 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            Circle View
          </button>
          <button
            onClick={() => setActiveView('graph')}
            className={`px-4 py-2 rounded-md ${
              activeView === 'graph'
                ? 'bg-blue-500 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            Graph View
          </button>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="h-[600px]">
          {activeView === 'circle' ? (
            <CirclePacking data={visualizationData} />
          ) : (
            <KnowledgeGraph data={visualizationData} />
          )}
        </div>
      </div>
    </div>
  );
}

export default ClusterView; 