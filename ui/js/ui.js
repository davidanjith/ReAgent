// UI state
let currentPapers = [];
let currentPaperIndex = 0;
let currentHighlightedText = '';

// Global variable to store the current concept hierarchy
let currentConceptHierarchy = null;

// UI functions
function showLoading(show) {
    const responseBox = document.getElementById('responseBox');
    responseBox.innerHTML = show ? '<div class="loading">Loading...</div>' : '';
}

function showError(message) {
    const responseBox = document.getElementById('responseBox');
    responseBox.innerHTML = `<div class="error">❌ ${message}</div>`;
}

function renderPapers(papers) {
    currentPapers = papers;
    const container = document.getElementById('papersContainer');
    container.innerHTML = '';
    
    const paperContainer = document.createElement('div');
    paperContainer.className = 'paper-container';
    
    // Create tabs
    const paperTabs = document.createElement('div');
    paperTabs.className = 'paper-tabs';
    
    papers.forEach((paper, index) => {
        const tab = document.createElement('div');
        tab.className = `paper-tab ${index === currentPaperIndex ? 'active' : ''}`;
        tab.textContent = `Paper ${index + 1}`;
        tab.onclick = () => displayPaper(index);
        paperTabs.appendChild(tab);
    });
    
    // Create content
    const paperContent = document.createElement('div');
    paperContent.className = 'paper-content';
    
    // Display paper details
    const paperDetails = document.createElement('div');
    paperDetails.className = 'paper-details';
    const currentPaper = papers[currentPaperIndex];
    paperDetails.innerHTML = `
        <h2>${currentPaper.title}</h2>
        <p><strong>Authors:</strong> ${currentPaper.authors.join(', ')}</p>
        <p><strong>Published:</strong> ${currentPaper.published}</p>
        <p><strong>Categories:</strong> ${currentPaper.categories.join(', ')}</p>
        <p><strong>Abstract:</strong> <span class="highlightable">${currentPaper.abstract}</span></p>
        <div class="chat-input">
            <input type="text" id="chatInput" placeholder="Ask about this paper...">
            <button onclick="sendChatMessage()">Send</button>
        </div>
        <div class="paper-actions">
            <button onclick="openPDF('${currentPaper.pdf_url}')" class="pdf-button">View PDF</button>
            <button onclick="loadFullText('${currentPaper.entry_id}')" class="full-text-button">Load Full Text</button>
        </div>
    `;
    paperContent.appendChild(paperDetails);
    
    // Add text selection event listeners
    const highlightableElements = paperContent.querySelectorAll('.highlightable');
    highlightableElements.forEach(element => {
        element.addEventListener('mouseup', handleTextSelection);
    });
    
    paperContainer.appendChild(paperTabs);
    paperContainer.appendChild(paperContent);
    container.appendChild(paperContainer);
}

function displayPaper(index) {
    currentPaperIndex = index;
    renderPapers(currentPapers);
}

function handleTextSelection() {
    const selection = window.getSelection();
    const selectedText = selection.toString().trim();
    
    if (selectedText) {
        const range = selection.getRangeAt(0);
        const rect = range.getBoundingClientRect();
        
        const highlightMenu = document.createElement('div');
        highlightMenu.className = 'highlight-menu';
        highlightMenu.style.position = 'fixed';
        highlightMenu.style.left = `${rect.left + window.scrollX}px`;
        highlightMenu.style.top = `${rect.bottom + window.scrollY + 5}px`;
        
        highlightMenu.innerHTML = `
            <button onclick="explainHighlight('${selectedText.replace(/'/g, "\\'")}')">Explain</button>
            <button onclick="askQuestion('${selectedText.replace(/'/g, "\\'")}')">Ask Question</button>
        `;
        
        document.body.appendChild(highlightMenu);
        
        // Remove menu when clicking outside
        document.addEventListener('click', function removeMenu(e) {
            if (!highlightMenu.contains(e.target)) {
                highlightMenu.remove();
                document.removeEventListener('click', removeMenu);
            }
        });
    }
}

async function explainHighlight(text) {
    try {
        showLoading(true);
        const response = await sendMessage(`Please explain this highlighted text: "${text}"`);
        showResponse(response);
    } catch (error) {
        showError(error.message);
    } finally {
        showLoading(false);
    }
}

async function askQuestion(text) {
    try {
        showLoading(true);
        const response = await sendMessage(`I have a question about this text: "${text}"`);
        showResponse(response);
    } catch (error) {
        showError(error.message);
    } finally {
        showLoading(false);
    }
}

async function handleSend() {
    const input = document.getElementById('userInput');
    const message = input.value.trim();
    
    if (!message) return;
    
    try {
        showLoading(true);
        const response = await sendMessage(message);
        showResponse(response);
        input.value = '';
    } catch (error) {
        showError(error.message);
    } finally {
        showLoading(false);
    }
}

function openPDF(url) {
    window.open(url, '_blank');
}

async function loadFullText(paperId) {
    try {
        showLoading(true);
        // Extract the arXiv ID from the full URL if present
        if (paperId.includes('arxiv.org')) {
            paperId = paperId.split('/').pop();
        }
        // Remove version suffix if present
        if (paperId.includes('v')) {
            paperId = paperId.split('v')[0];
        }
        
        const data = await getFullText(paperId);
        
        const paperContent = document.querySelector('.paper-content');
        const fullTextSection = document.createElement('div');
        fullTextSection.className = 'full-text-section';
        
        // Display the summary instead of the full text
        let summary = data.summary;
        if (typeof summary !== 'string') {
            summary = JSON.stringify(summary, null, 2);
        }
        let text = data.text;
        if (typeof text !== 'string') {
            text = JSON.stringify(text, null, 2);
        }
        fullTextSection.innerHTML = `
            <h3>Paper Summary</h3>
            <div class="summary-content">${summary || text || 'No summary available'}</div>
            <div class="paper-actions">
                <button onclick="toggleFullText('${paperId}')" class="toggle-text-button">Show Full Text</button>
            </div>
        `;
        
        // Store the full text data for later use
        fullTextSection._fullData = data;
        
        paperContent.appendChild(fullTextSection);

        // Store full text in currentPaper for chat context
        if (currentPapers && currentPapers[currentPaperIndex]) {
            currentPapers[currentPaperIndex].full_text = data.text || '';
            currentPapers[currentPaperIndex].summary = data.summary || '';
        }

        // Update the concept hierarchy visualization for this paper only
        if (data.hierarchy) {
            // Find the paper node in the current concept hierarchy and update its children
            if (currentConceptHierarchy) {
                const paperTitle = currentPapers[currentPaperIndex].title;
                const paperNode = currentConceptHierarchy.children.find(child => child.name === paperTitle);
                if (paperNode) {
                    // Replace children with the new hierarchy's children
                    paperNode.children = data.hierarchy.children;
                }
                updateConceptHierarchy(currentConceptHierarchy);
            } else {
                // If not set, just show this hierarchy
                updateConceptHierarchy(data.hierarchy);
            }
        }
    } catch (error) {
        showError(error.message);
    } finally {
        showLoading(false);
    }
}

// Add function to toggle between summary and full text
function toggleFullText(paperId) {
    const fullTextSection = document.querySelector('.full-text-section');
    const summaryContent = fullTextSection.querySelector('.summary-content');
    const toggleButton = fullTextSection.querySelector('.toggle-text-button');
    const fullData = fullTextSection._fullData;
    
    if (toggleButton.textContent === 'Show Full Text') {
        summaryContent.innerHTML = fullData.text || 'No full text available';
        summaryContent.className = 'full-text-content highlightable';
        toggleButton.textContent = 'Show Summary';
        
        // Add text selection event listener for full text
        summaryContent.addEventListener('mouseup', handleTextSelection);
    } else {
        summaryContent.innerHTML = fullData.summary || 'No summary available';
        summaryContent.className = 'summary-content';
        toggleButton.textContent = 'Show Full Text';
    }
} 