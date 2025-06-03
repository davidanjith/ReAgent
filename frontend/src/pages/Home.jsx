import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { searchPapers } from '../services/api';

function Home() {
    const [searchQuery, setSearchQuery] = useState('');
    const [isSearching, setIsSearching] = useState(false);
    const [error, setError] = useState(null);
    const navigate = useNavigate();

    const handleSearch = async (e) => {
        e.preventDefault();
        if (!searchQuery.trim()) return;

        try {
            setIsSearching(true);
            setError(null);
            // Call the backend search endpoint
            const response = await searchPapers(searchQuery);
            
            // Navigate to the papers page after successful search, passing papers data
            navigate('/papers', { state: { papers: response.data.papers } });

        } catch (err) {
            setError('Failed to search papers. Please try again.');
            console.error('Error searching papers:', err);
        } finally {
            setIsSearching(false);
        }
    };

    return (
        <div className="flex flex-col items-center justify-center h-[calc(100vh-150px)]">
            <h1 className="text-4xl font-bold text-gray-900 mb-6">Research Companion</h1>
            <p className="text-xl text-gray-600 mb-8 text-center max-w-2xl">
                Explore and analyze research papers with AI-powered insights.
            </p>

            <form onSubmit={handleSearch} className="w-full max-w-md flex gap-4">
                <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    placeholder="Enter your research topic (e.g., quantum physics)"
                    className="flex-1 p-3 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                    disabled={isSearching}
                />
                <button
                    type="submit"
                    disabled={isSearching}
                    className="px-6 py-3 bg-blue-600 text-white rounded-lg shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
                >
                    {isSearching ? 'Searching...' : 'Search Papers'}
                </button>
            </form>

            {error && (
                <div className="mt-6 bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
                    {error}
                </div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-8">
                <Link
                    to="/papers"
                    className="p-6 bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow"
                >
                    <h2 className="text-2xl font-semibold text-gray-800 mb-2">
                        Papers
                    </h2>
                    <p className="text-gray-600">
                        Browse and analyze research papers with AI-powered insights.
                    </p>
                </Link>

                <Link
                    to="/clusters"
                    className="p-6 bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow"
                >
                    <h2 className="text-2xl font-semibold text-gray-800 mb-2">
                        Clusters
                    </h2>
                    <p className="text-gray-600">
                        Explore knowledge clusters and connections between papers.
                    </p>
                </Link>
            </div>
        </div>
    );
}

export default Home; 