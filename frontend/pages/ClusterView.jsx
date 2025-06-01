import React, { useState, useEffect } from 'react';
import CirclePacking from '../graph/CirclePacking';

function ClusterView() {
  const [clusters, setClusters] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchClusters = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/papers/clusters');
        if (!response.ok) throw new Error('Failed to fetch clusters');
        const data = await response.json();
        setClusters(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchClusters();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-xl text-gray-600">Loading clusters...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-xl text-red-600">{error}</div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div className="text-center">
        <h1 className="text-3xl font-bold mb-4">Question Clusters</h1>
        <p className="text-gray-600">
          Explore your research questions organized by semantic similarity
        </p>
      </div>

      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="h-[600px]">
          <CirclePacking data={clusters} />
        </div>
      </div>

      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-xl font-bold mb-4">How to Use</h2>
        <ul className="list-disc list-inside space-y-2 text-gray-700">
          <li>Zoom in/out using the mouse wheel or pinch gestures</li>
          <li>Click and drag to pan around the visualization</li>
          <li>Hover over circles to see the full question and answer</li>
          <li>Related questions are grouped together in clusters</li>
        </ul>
      </div>
    </div>
  );
}

export default ClusterView; 