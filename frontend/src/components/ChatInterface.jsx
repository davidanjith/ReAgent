import React, { useState, useEffect, useRef } from 'react';
import { getPaperChatHistory, askQuestion } from '../services/api';

const ChatInterface = ({ paperId }) => {
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const messagesEndRef = useRef(null);

    useEffect(() => {
        loadChatHistory();
    }, [paperId]);

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    const loadChatHistory = async () => {
        try {
            setLoading(true);
            const response = await getPaperChatHistory(paperId);
            setMessages(response.data);
            setError(null);
        } catch (err) {
            setError('Failed to load chat history. Please try again.');
            console.error('Error loading chat history:', err);
        } finally {
            setLoading(false);
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!input.trim()) return;

        const question = input.trim();
        setInput('');
        setLoading(true);

        try {
            // Add user question to messages immediately
            setMessages(prev => [...prev, { role: 'user', content: question }]);

            // Get response from API
            const response = await askQuestion(paperId, question);
            
            // Add assistant response to messages
            setMessages(prev => [...prev, {
                role: 'assistant',
                content: response.data.answer,
                context: response.data.context
            }]);

            setError(null);
        } catch (err) {
            setError('Failed to get response. Please try again.');
            console.error('Error getting response:', err);
        } finally {
            setLoading(false);
        }
    };

    if (error) {
        return (
            <div className="text-red-500 text-center p-4">
                {error}
            </div>
        );
    }

    return (
        <div className="flex flex-col h-[calc(100vh-300px)]">
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
                {messages.map((message, index) => (
                    <div
                        key={index}
                        className={`flex ${
                            message.role === 'user' ? 'justify-end' : 'justify-start'
                        }`}
                    >
                        <div
                            className={`max-w-[70%] rounded-lg p-4 ${
                                message.role === 'user'
                                    ? 'bg-blue-500 text-white'
                                    : 'bg-gray-100 text-gray-800'
                            }`}
                        >
                            <p className="whitespace-pre-wrap">{message.content}</p>
                            {message.context && (
                                <div className="mt-2 text-sm opacity-75">
                                    <p className="font-medium">Context:</p>
                                    <p className="whitespace-pre-wrap">{message.context}</p>
                                </div>
                            )}
                        </div>
                    </div>
                ))}
                <div ref={messagesEndRef} />
            </div>

            <form onSubmit={handleSubmit} className="p-4 border-t">
                <div className="flex gap-4">
                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        placeholder="Ask a question about the paper..."
                        className="flex-1 p-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                        disabled={loading}
                    />
                    <button
                        type="submit"
                        className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
                        disabled={loading}
                    >
                        {loading ? 'Sending...' : 'Send'}
                    </button>
                </div>
            </form>
        </div>
    );
};

export default ChatInterface; 