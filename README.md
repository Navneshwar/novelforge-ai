<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/d223931f-8c57-44ac-90a2-0c2f48150b6a" /># 📖 NovelForge - AI Novel Writing Assistant with Persistent Memory

> **The Hangover Part AI: Where's My Context?** Hackathon Project
> June 29 – July 5, 2026

## 🎯 Project Overview

NovelForge is an AI-powered novel writing assistant that uses **Cognee's hybrid graph-vector memory layer** to maintain perfect consistency across characters, plot points, and world-building. The AI never forgets - it remembers every detail about your story across infinite sessions.

### Key Features

- 🧠 **Persistent Memory**: Every character, plot point, and story detail is stored in Cognee's memory
- ✍️ **AI Writing Assistant**: Generate content with context-aware AI that remembers your story
- 🔍 **Consistency Checker**: Automatically detects contradictions in your narrative
- 🕸️ **Memory Graph Visualizer**: Interactive 3D visualization of your story's knowledge graph
- 👥 **Character Management**: Track characters, relationships, and their evolution
- 📚 **Chapter Management**: Organize your novel with AI-assisted chapter writing

## 🏗️ Architecture

### Tech Stack

- **Backend**: Python 3.10+ with FastAPI
- **Memory Layer**: Cognee (self-hosted, hybrid graph-vector)
- **LLM**: Ollama (fully local, no cloud dependencies)
- **Database**: SQLite (local)
- **Frontend**: React + Vite + Three.js
- **Embeddings**: all-minilm (384 dims) or nomic-embed-text (768 dims)

### How It Works

1. **Write** content in the novel editor
2. **Remember**: Cognee stores all story elements in a knowledge graph
3. **Recall**: AI queries memory for context when generating new content
4. **Check**: Consistency scanner detects contradictions
5. **Visualize**: Interactive graph shows all connections

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- Ollama installed
- Git (optional)

### Installation

#### 1. Clone the Repository
```bash
git clone https://github.com/Navneshwar/novelforge-ai
cd novelforge
2. Set Up Ollama (Windows)
cmd
# Install Ollama from https://ollama.ai/download/windows

# Pull smaller models for low-resource systems
ollama pull llama3.2:3b
ollama pull all-minilm

# For better quality (if you have 16GB+ RAM)
ollama pull llama3.1:8b
ollama pull nomic-embed-text
3. Set Up Backend
cmd
cd backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
copy .env.example .env

# Edit .env to match your setup (especially model names)
# For low-resource: LLM_MODEL=llama3.2:3b, EMBEDDING_MODEL=all-minilm
# For better: LLM_MODEL=llama3.1:8b, EMBEDDING_MODEL=nomic-embed-text

# Run the backend
python main.py
4. Set Up Frontend
cmd
cd frontend

# Install dependencies
npm install

# Start the development server
npm run dev
5. Access the Application
Frontend: http://localhost:3000

Backend API: http://localhost:8000

API Docs: http://localhost:8000/docs

📁 Project Structure
text
novelforge/
├── backend/                 # FastAPI backend
│   ├── src/
│   │   ├── core/           # Configuration & database
│   │   ├── models/         # SQLAlchemy models
│   │   ├── services/       # Business logic
│   │   │   ├── memory_service.py   # Cognee wrapper
│   │   │   ├── llm_service.py      # Ollama client
│   │   │   ├── novel_service.py    # Novel management
│   │   │   └── consistency_service.py
│   │   ├── api/routes/     # API endpoints
│   │   └── utils/          # Helper functions
│   ├── data/               # SQLite & Cognee data
│   ├── logs/               # Application logs
│   └── main.py
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── pages/          # Page components
│   │   ├── services/       # API client
│   │   └── styles/         # CSS styles
│   └── package.json
├── docs/                   # Documentation
├── scripts/                # Utility scripts
└── README.md
🎮 Using NovelForge
Creating a Novel
Click "New Novel" on the dashboard

Enter a title and genre

Start writing in the editor

Writing with AI
Write some content

Click "AI Continue" to generate the next part

The AI uses Cognee memory to stay consistent

Managing Characters
Go to the "Characters" tab

Add characters with traits and descriptions

View relationships between characters

Checking Consistency
Click the "Consistency" tab

Click "Run Full Check"

Review and resolve any issues found

Visualizing Memory
Click the "Memory Graph" tab

Explore the interactive 3D graph

See connections between characters, locations, and plot points

🔧 Configuration
Environment Variables (.env)
env
# Ollama Configuration
LLM_MODEL=llama3.2:3b          # Or llama3.1:8b for better quality
EMBEDDING_MODEL=all-minilm     # Or nomic-embed-text for better quality
EMBEDDING_DIMENSIONS=384       # 768 for nomic-embed-text

# Cognee Configuration
COGNEE_DATABASE_PATH=./data/cognee.db
COGNEE_VECTOR_STORE_PATH=./data/vectors
COGNEE_GRAPH_STORE_PATH=./data/graph

# Application
DEBUG=True
SECRET_KEY=your-secret-key
📊 API Endpoints
Method	Endpoint	Description
GET	/api/novels	Get all novels
POST	/api/novels	Create a new novel
GET	/api/novels/{id}	Get a specific novel
PUT	/api/novels/{id}	Update a novel
POST	/api/novels/{id}/generate	Generate AI content
POST	/api/memory/remember/{id}	Store in memory
POST	/api/memory/recall/{id}	Recall from memory
POST	/api/consistency/check/{id}	Run consistency check
GET	/api/characters/{id}	Get characters
🧠 Cognee Memory Operations
NovelForge uses all four Cognee memory operations:

remember(): Store story elements (characters, plot points, chapters)

recall(): Query memory for context during writing

improve(): Run memify to derive new insights

forget(): Remove retconned or incorrect elements

🤝 Team Roles
Role	Responsibilities
Backend Lead	FastAPI, Cognee integration, memory services
Frontend Lead	UI, Graph visualization, Novel editor
LLM/Integration Lead	Ollama setup, prompt engineering, consistency
DevOps/QA Lead	Windows setup, testing, environment management
📅 Development Timeline
Day	Milestone
Day 1	Environment setup, Ollama+Cognee installation
Day 2	Core memory service, basic API routes
Day 3	Novel management, LLM integration
Day 4	Consistency checker, graph visualization
Day 5	Frontend polish, integration testing
Day 6	Documentation, demo preparation, submission
🛠️ Troubleshooting
Ollama Not Responding
cmd
# Check if Ollama is running
ollama list

# Restart Ollama
ollama serve
Cognee Import Errors
cmd
# Reinstall Cognee
pip uninstall cognee
pip install cognee==1.0.0
Frontend Build Issues
cmd
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
📝 License
MIT License - See LICENSE file for details

🙏 Acknowledgments
Cognee - Memory layer for AI agents

Ollama - Local LLM runtime

WeMakeDevs - Hackathon organizers

The Hangover Part AI - Hackathon theme

📞 Support
Discord: Join the WeMakeDevs Discord

Issues: GitHub Issues

Built with ❤️ for The Hangover Part AI Hackathon
