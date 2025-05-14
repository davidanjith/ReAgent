// API endpoints
const API_BASE_URL = 'http://localhost:8000';

// API functions
async function searchPapers(query, maxResults = 5) {
    const response = await fetch(`${API_BASE_URL}/search/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, max_results: maxResults })
    });
    
    if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to fetch papers');
    }
    
    return response.json();
}

async function sendChatMessage(message, paperId, context) {
    const response = await fetch(`${API_BASE_URL}/chat/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            message,
            paper_id: paperId,
            context
        })
    });
    
    if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to send message');
    }
    
    return response.json();
}

async function getFullText(paperId) {
    const response = await fetch(`${API_BASE_URL}/paper/${paperId}/full-text`);
    
    if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to get full text');
    }
    
    return response.json();
}

async function getKnowledgeGraph() {
    const response = await fetch(`${API_BASE_URL}/knowledge-graph/`);
    
    if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to get knowledge graph');
    }
    
    return response.json();
} 