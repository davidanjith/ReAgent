# Research Companion

A full-stack research assistant tool that helps users explore and understand research papers using AI, clustering, and rich visualization.

## Features

- 🔍 Smart paper search and recommendation
- 💬 Context-aware Q&A using Ollama
- 📊 Interactive visualization of concepts and relationships
- 🧠 Persistent memory using ChromaDB
- 📈 Semantic clustering of questions and answers

## Tech Stack

- **Backend:**
  - FastAPI
  - Ollama (for LLM and embeddings)
  - ChromaDB (for vector storage)
  - UMAP + HDBSCAN (for clustering)

- **Frontend:**
  - React
  - Tailwind CSS
  - D3.js (for visualizations)

## Prerequisites

- Python 3.8+
- Node.js 16+
- Ollama (with llama2 model)
- ChromaDB

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd research-companion
```

2. Set up the Python virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

3. Install frontend dependencies:
```bash
cd frontend
npm install
```

4. Create necessary directories:
```bash
mkdir -p backend/data/chroma
```

## Running the Application

1. Start the backend server:
```bash
cd backend
uvicorn main:app --reload
```

2. Start the frontend development server:
```bash
cd frontend
npm start
```

3. Access the application at `http://localhost:3000`

## Usage

1. Enter your research question (e.g., "Help me understand quantum theory")
2. The system will find relevant papers and display them
3. Ask follow-up questions about specific papers
4. View the semantic clusters of your questions and answers
5. Explore the interactive visualization of concepts

## Development

### Project Structure

```
.
├── backend/
│   ├── data/
│   │   └── chroma/        # ChromaDB storage
│   │   └── test_data/
│   │   │   └── papers/        # Sample papers
│   │   └── utils/             # Backend services
│   └── main.py           # FastAPI application
├── frontend/
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── pages/        # Page components
│   │   └── services/     # API services
│   └── package.json
└── README.md
```

### Adding New Papers

1. Add paper metadata to `backend/test_data/papers/metadata.json`
2. Add paper content to `backend/test_data/papers/<paper_id>.txt`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License 