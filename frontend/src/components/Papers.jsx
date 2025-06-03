import React, { useState, useEffect } from 'react';
import { searchPapers } from '../services/api';
import { Link, useLocation } from 'react-router-dom';

const Papers = () => {
    const [papers, setPapers] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [searchQuery, setSearchQuery] = useState('');
    const [isSearching, setIsSearching] = useState(false);
    const location = useLocation();

    useEffect(() => {
        if (location.state && location.state.papers) {
            setPapers(location.state.papers);
        } else {
            // Optionally, could try fetching all papers here if direct navigation is expected
            // For now, we rely on search from Home or on this page.
            // You could add loadPapers() back here if needed, but handle the 404 gracefully.
        }
    }, [location.state]);

    const handleSearch = async (e) => {
        e.preventDefault();
        if (!searchQuery.trim()) return;

        try {
            setIsSearching(true);
            setError(null);
            const response = await searchPapers(searchQuery);
            setPapers(response.data.papers);
        } catch (err) {
            setError('Failed to search papers. Please try again.');
            console.error('Error searching papers:', err);
            setPapers([]);
        } finally {
            setIsSearching(false);
        }
    };

    return (
        <div className="container mx-auto px-4 py-8">
            <div className="mb-8">
                <h1 className="text-3xl font-bold mb-4">Research Papers</h1>
                <form onSubmit={handleSearch} className="flex gap-4">
                    <input
                        type="text"
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        placeholder="Search for papers on arXiv..."
                        className="flex-1 p-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                        disabled={isSearching}
                    />
                    <button
                        type="submit"
                        disabled={isSearching}
                        className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
                    >
                        {isSearching ? 'Searching...' : 'Search'}
                    </button>
                </form>
            </div>

            {error && (
                <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
                    {error}
                </div>
            )}

            {isSearching ? (
                <div className="flex justify-center items-center h-64">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
                </div>
            ) : (
                <>
                    {papers.length > 0 ? (
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                            {papers.map((paper) => (
                                <Link
                                    key={paper.id}
                                    to={`/papers/${paper.id}`}
                                    className="block p-6 bg-white rounded-lg shadow-lg hover:shadow-xl transition-shadow duration-200"
                                >
                                    <h2 className="text-xl font-semibold mb-2 line-clamp-2">{paper.title}</h2>
                                    <p className="text-gray-600 mb-2">
                                        {paper.authors.join(', ')}
                                    </p>
                                    <p className="text-gray-500 text-sm mb-4">
                                        {paper.metadata?.year} • {paper.metadata?.citations} citations
                                    </p>
                                    <p className="text-gray-700 line-clamp-3">
                                        {paper.metadata?.abstract}
                                    </p>
                                    <div className="mt-4 flex flex-wrap gap-2">
                                        {paper.metadata?.keywords?.map((keyword, index) => (
                                            <span
                                                key={index}
                                                className="px-2 py-1 bg-gray-100 text-gray-600 text-sm rounded"
                                            >
                                                {keyword}
                                            </span>
                                        ))}
                                    </div>
                                </Link>
                            ))}
                        </div>
                    ) : (
                        <div className="text-center text-gray-500 mt-8">
                            {error ? 'Error loading papers.' : 'No papers found. Try searching for a topic above.'}
                        </div>
                    )}
                </>
            )}
        </div>
    );
};

export default Papers; 