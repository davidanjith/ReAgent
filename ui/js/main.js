// Main application logic
async function handleSearch() {
    const query = document.getElementById('searchInput').value.trim();
    if (!query) return;

    try {
        showLoading(true);
        const data = await searchPapers(query);
        
        if (!data.papers || data.papers.length === 0) {
            showError("No papers found for your query");
            return;
        }

        // Update the response box
        const responseBox = document.getElementById('responseBox');
        responseBox.innerHTML = `Found ${data.papers.length} papers matching your query.`;

        // Render the papers
        renderPapers(data.papers);
        
        // Generate concept hierarchy for all papers
        const hierarchy = {
            name: "Search Results",
            children: data.papers.map(paper => ({
                name: paper.title,
                value: 5, // Make each paper a big circle
                children: [
                    {
                        name: "Abstract",
                        value: 1
                    }
                ]
            }))
        };
        
        updateConceptHierarchy(hierarchy);
        
    } catch (error) {
        showError(error.message);
    } finally {
        showLoading(false);
    }
}

async function sendChatMessage() {
    const chatInput = document.getElementById('chatInput');
    const message = chatInput.value.trim();
    
    if (!message) return;

    try {
        const currentPaper = currentPapers[currentPaperIndex];
        if (!currentPaper || !currentPaper.entry_id) {
            throw new Error('Invalid paper data');
        }

        showLoading(true);

        // Extract the arXiv ID from the full URL if present
        let paperId = currentPaper.entry_id;
        if (paperId.includes('arxiv.org')) {
            paperId = paperId.split('/').pop();
        }
        // Remove version suffix if present
        if (paperId.includes('v')) {
            paperId = paperId.split('v')[0];
        }

        const data = await sendChatMessage(message, paperId, currentPaper.abstract);
        
        const responseBox = document.getElementById('responseBox');
        responseBox.innerHTML = `
            <div class="chat-message user">
                <div class="message-content">${message}</div>
            </div>
            <div class="chat-message assistant">
                <div class="message-content">${data.response}</div>
            </div>
        `;
        
        // Update knowledge graph
        if (data.knowledge_graph) {
            updateKnowledgeGraph(data.knowledge_graph);
        }
    } catch (error) {
        showError(error.message);
    } finally {
        showLoading(false);
    }

    chatInput.value = '';
}

async function explainSelection() {
    if (!currentHighlightedText) return;

    try {
        const currentPaper = currentPapers[currentPaperIndex];
        if (!currentPaper || !currentPaper.entry_id) {
            throw new Error('Invalid paper data');
        }

        showLoading(true);

        // Extract the arXiv ID from the full URL if present
        let paperId = currentPaper.entry_id;
        if (paperId.includes('arxiv.org')) {
            paperId = paperId.split('/').pop();
        }
        // Remove version suffix if present
        if (paperId.includes('v')) {
            paperId = paperId.split('v')[0];
        }

        const data = await sendChatMessage(
            `Please provide a detailed explanation of this text: "${currentHighlightedText}"`,
            paperId,
            currentPaper.abstract
        );
        
        const responseBox = document.getElementById('responseBox');
        responseBox.innerHTML = `
            <div class="analysis-result">
                <h3>Detailed Explanation</h3>
                <div class="highlighted-context">${currentHighlightedText}</div>
                <div class="analysis-content">${data.response}</div>
            </div>
        `;
        
        // Update knowledge graph
        if (data.knowledge_graph) {
            updateKnowledgeGraph(data.knowledge_graph);
        }
    } catch (error) {
        showError(error.message);
    } finally {
        showLoading(false);
    }
}

// Initialize the application
document.addEventListener('DOMContentLoaded', () => {
    // Add event listeners
    document.getElementById('searchInput').addEventListener('keypress', (event) => {
        if (event.key === 'Enter') {
            handleSearch();
        }
    });

    document.getElementById('chatInput').addEventListener('keypress', (event) => {
        if (event.key === 'Enter') {
            sendChatMessage();
        }
    });
});

// --- ChatGPT-like Chat UI Logic ---
let chatHistory = [];

function renderChatHistory() {
    const chatHistoryDiv = document.getElementById('chatHistory');
    chatHistoryDiv.innerHTML = '';
    chatHistory.forEach(msg => {
        const div = document.createElement('div');
        div.className = 'chat-message ' + msg.role + (msg.type === 'highlight' ? ' highlight' : '');
        if (msg.type === 'highlight') {
            div.innerHTML = `<em>Highlighted:</em> <span class="mathjax-label">${msg.text}</span>`;
        } else {
            div.innerHTML = `<span class="mathjax-label">${msg.text}</span>`;
        }
        chatHistoryDiv.appendChild(div);
    });
    // Scroll to bottom
    chatHistoryDiv.scrollTop = chatHistoryDiv.scrollHeight;
    // Render MathJax
    setTimeout(() => {
        if (window.MathJax && window.MathJax.typesetPromise) {
            window.MathJax.typesetPromise([chatHistoryDiv]);
        }
    }, 50);
}

function addChatMessage(role, text, type = 'normal') {
    chatHistory.push({ role, text, type });
    renderChatHistory();
}

// Multi-line input: Enter to send, Shift+Enter for new line
const chatInput = document.getElementById('chatInput');
const sendChatBtn = document.getElementById('sendChatBtn');
chatInput.addEventListener('keydown', function(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendChat();
    }
});
sendChatBtn.addEventListener('click', sendChat);

function sendChat() {
    const message = chatInput.value.trim();
    if (!message) return;
    chatInput.value = '';
    addChatMessage('user', message);
    // Get current paper context
    const currentPaper = currentPapers[currentPaperIndex];
    let paperId = currentPaper && currentPaper.entry_id ? currentPaper.entry_id : null;
    let context = '';
    if (currentPaper) {
        context = `Title: ${currentPaper.title}\nAuthors: ${currentPaper.authors ? currentPaper.authors.join(', ') : ''}\nAbstract: ${currentPaper.abstract || ''}`;
        if (currentPaper.full_text) {
            context += `\nFull Text: ${currentPaper.full_text}`;
        }
    }
    // Send to backend (reuse sendChatMessage logic, but update to use chat UI)
    showLoading(true);
    fetch(`/paper/${paperId}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message, context })
    })
    .then(res => res.json())
    .then(data => {
        addChatMessage('assistant', data.response);
    })
    .catch(err => {
        addChatMessage('assistant', 'Error: ' + err.message);
    })
    .finally(() => {
        showLoading(false);
    });
}

// Highlight tracking: when a highlight is explained, add to chat
window.explainHighlight = function(selectedText) {
    addChatMessage('highlight', selectedText, 'highlight');
    // Optionally, send to backend for explanation and add response
    // ...
};

// On page load, render empty chat
renderChatHistory(); 