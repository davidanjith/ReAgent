import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { getPaper, processPaper } from '../services/api';
import ChatInterface from '../components/ChatInterface';
import ClusterVisualization from '../components/ClusterVisualization';

const PaperView = () => {
    const { paperId } = useParams();
    const [paper, setPaper] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [activeTab, setActiveTab] = useState('chat');

    useEffect(() => {
        loadPaper();
    }, [paperId]);

    const loadPaper = async () => {
        try {
            setLoading(true);
            const response = await getPaper(paperId);
            setPaper(response.data);
            
            // Process the paper for embeddings
            await processPaper(paperId);
            
            setError(null);
        } catch (err) {
            setError('Failed to load paper. Please try again later.');
            console.error('Error loading paper:', err);
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="flex justify-center items-center h-64">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="text-red-500 text-center p-4">
                {error}
            </div>
        );
    }

    if (!paper) {
        return (
            <div className="text-center text-gray-500 p-4">
                Paper not found.
            </div>
        );
    }

    return (
        <div className="container mx-auto px-4 py-8">
            <div className="mb-8">
                <h1 className="text-3xl font-bold mb-2">{paper.title}</h1>
                <p className="text-gray-600 mb-4">
                    {paper.authors.join(', ')}
                </p>
                {paper.metadata?.year && (
                    <p className="text-sm text-gray-500">
                        Published: {paper.metadata.year}
                    </p>
                )}
            </div>

            <div className="mb-6">
                <nav className="flex space-x-4 border-b border-gray-200">
                    <button
                        className={`px-4 py-2 font-medium ${
                            activeTab === 'chat'
                                ? 'text-blue-600 border-b-2 border-blue-600'
                                : 'text-gray-500 hover:text-gray-700'
                        }`}
                        onClick={() => setActiveTab('chat')}
                    >
                        Chat
                    </button>
                    <button
                        className={`px-4 py-2 font-medium ${
                            activeTab === 'clusters'
                                ? 'text-blue-600 border-b-2 border-blue-600'
                                : 'text-gray-500 hover:text-gray-700'
                        }`}
                        onClick={() => setActiveTab('clusters')}
                    >
                        Clusters
                    </button>
                </nav>
            </div>

            <div className="mt-6">
                {activeTab === 'chat' ? (
                    <ChatInterface paperId={paperId} />
                ) : (
                    <ClusterVisualization paperId={paperId} />
                )}
            </div>
        </div>
    );
};

export default PaperView; 