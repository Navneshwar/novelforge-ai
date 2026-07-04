<<<<<<< HEAD
=======
# 📖 NovelForge — AI Novel Writing Assistant with Persistent Memory
>>>>>>> 0c86f7d (Backend and ui changes done)

> **The Hangover Part AI: Where's My Context?** — WeMakeDevs Hackathon
> June 29 – July 5, 2026

**Team: Hopeless**

| Name | Role |
|---|---|
| Navneshwar B | Team Lead / Backend & Cognee Integration |
| Vishwak S | Frontend & Graph Visualization |
| Abimanyu R | LLM Integration & Prompt Engineering |
| Girusudhan K | DevOps, QA & Environment Setup |

---

## 🎯 Problem We're Solving

Every AI writing tool wakes up with amnesia. Ask it to continue a novel and it forgets which character died two chapters ago, contradicts a world-building rule it invented itself, or can't remember a name it just introduced. Writers end up re-explaining their own story to the AI over and over.

**NovelForge** fixes this by giving the AI a real memory. Every character, plot point, and story detail is written into **Cognee's self-hosted, hybrid graph-vector memory layer**, so the assistant can recall exactly what happened — and why it matters — no matter how many sessions have passed.

## ✨ Key Features

- 🧠 **Persistent Memory** — every character, plot point, and story detail is stored via Cognee's `remember()` and retrieved via `recall()`
- ✍️ **AI Writing Assistant** — generates new chapters/scenes using memory-grounded context, not just the last few paragraphs
- 🔍 **Consistency Checker** — flags contradictions between new writing and established story memory using an LLM-backed analysis pass
- 🕸️ **Memory Graph Visualizer** — interactive 3D view of Cognee's extracted knowledge graph (characters, locations, events, and how they connect), layered with the novel's structural data
- 👥 **Character Management** — track traits, relationships, and evolution over time
- 📚 **Chapter Management** — organize a novel with AI-assisted drafting and rich-text editing
- 🌍 **World Building & Timeline** — dedicated views for lore, settings, and chronological plot ordering

## 🏗️ Architecture

### Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.10+, FastAPI |
| Memory Layer | **Cognee** (self-hosted, hybrid graph + vector) |
| LLM | Ollama (fully local, no cloud dependency) |
| Relational DB | SQLite |
| Frontend | React + Vite + Three.js |
| Embeddings | `all-minilm` (384-dim) or `nomic-embed-text` (768-dim) |

### How It Works

1. **Write** — content is drafted in the novel editor
2. **Remember** — `cognee.remember()` ingests the text and Cognee builds/updates the knowledge graph in the background
3. **Recall** — before generating new content, the app calls `cognee.recall()` to pull relevant characters, events, and facts into the prompt
4. **Check** — the consistency service recalls related memory for the newest chapter and asks the LLM to flag contradictions
5. **Visualize** — the Memory Graph Visualizer renders Cognee's actual extracted entities/relationships in 3D

### Cognee Memory Operations in Use

NovelForge exercises all four of Cognee's core operations:

| Operation | Where it's used |
|---|---|
| `remember()` | Storing new chapters, characters, plot points, and novel metadata as they're created or edited |
| `recall()` | Pulling relevant context before AI generation and before consistency checks |
| `improve()` | Manually triggerable "Improve Memory" action to derive new insights (memify) from accumulated content |
| `forget()` | Removing retconned or deleted story elements from memory, per-item or per-dataset |

Each novel gets its own isolated Cognee dataset (`novel_<uuid>`), so multiple stories never leak context into one another.

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- [Ollama](https://ollama.ai/download) installed and running
- Git (optional)

### 1. Clone the Repository

```bash
git clone https://github.com/Navneshwar/novelforge-ai
cd novelforge
```

### 2. Set Up Ollama

```bash
# Pull models for local, low-resource setups
ollama pull llama3.2:3b
ollama pull all-minilm

# For better quality (16GB+ RAM)
ollama pull llama3.1:8b
ollama pull nomic-embed-text
```

### 3. Set Up the Backend

```bash
cd backend

# Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate          # Windows
source venv/bin/activate       # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Copy environment file and adjust as needed
cp .env.example .env           # Windows: copy .env.example .env

# Run the backend
python main.py
```

> ⚠️ Cognee requires `LLM_API_KEY` and `HUGGINGFACE_TOKENIZER` to be set even for local Ollama use (placeholder values are fine). These are already included in `.env.example` — just make sure they carry over into your `.env`.

### 4. Set Up the Frontend

```bash
cd frontend
npm install
npm run dev
```

### 5. Access the Application

| Service | URL |
|---|---|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| API Docs (Swagger) | http://localhost:8000/docs |

## 📁 Project Structure

```
novelforge/
├── backend/                      # FastAPI backend
│   ├── src/
│   │   ├── core/                 # Configuration & database
│   │   ├── models/                # SQLAlchemy models
│   │   ├── services/
│   │   │   ├── memory_service.py     # Cognee wrapper (remember/recall/improve/forget)
│   │   │   ├── llm_service.py        # Ollama client
│   │   │   ├── novel_service.py      # Novel & chapter management
│   │   │   └── consistency_service.py
│   │   ├── api/routes/            # API endpoints
│   │   └── utils/                 # Helper functions
│   ├── data/                      # SQLite & Cognee data (gitignored)
│   ├── logs/                      # Application logs (gitignored)
│   └── main.py
├── frontend/                      # React frontend
│   ├── src/
│   │   ├── components/            # GraphVisualizer, NovelEditor, WorldBuilding, etc.
│   │   ├── pages/                  # Dashboard, NovelPage
│   │   ├── services/                # API client
│   │   └── styles/
│   └── package.json
├── scripts/                       # Windows utility scripts
└── README.md
```

## 🎮 Using NovelForge

**Creating a Novel** — Click "New Novel" on the dashboard → enter a title and genre → start writing.

**Writing with AI** — Write some content, then click "AI Continue." The AI recalls relevant memory from Cognee before generating the next part, so it stays consistent with everything established so far.

**Managing Characters** — Go to the Characters tab to add traits, descriptions, and relationships between characters.

**Checking Consistency** — Click the Consistency tab → "Run Full Check." The checker recalls related memory for your latest chapter and flags genuine contradictions, not just any related content.

**Visualizing Memory** — Click the Memory Graph tab to explore an interactive 3D graph combining Cognee's extracted entities/relationships with the novel's structural data (characters, chapters, plot points).

## 🔧 Configuration

Key environment variables (see `backend/.env.example` for the full list):

```env
# Ollama / Cognee LLM configuration
LLM_PROVIDER=ollama
LLM_MODEL=llama3.2:3b          # or llama3.1:8b for better quality
LLM_ENDPOINT=http://localhost:11434/v1
LLM_API_KEY=ollama              # placeholder; required by Cognee's validator

# Embedding configuration
EMBEDDING_PROVIDER=ollama
EMBEDDING_MODEL=all-minilm      # or nomic-embed-text for better quality
EMBEDDING_ENDPOINT=http://localhost:11434/api/embed
EMBEDDING_DIMENSIONS=384        # 768 for nomic-embed-text
HUGGINGFACE_TOKENIZER=sentence-transformers/all-MiniLM-L6-v2

# Cognee storage
COGNEE_DATABASE_PATH=./data/cognee.db
COGNEE_VECTOR_STORE_PATH=./data/vectors
COGNEE_GRAPH_STORE_PATH=./data/graph

# Application
DEBUG=True
SECRET_KEY=change-this-to-a-random-string-in-production
```

## 📊 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/novels` | Get all novels |
| POST | `/api/novels` | Create a new novel |
| GET | `/api/novels/{id}` | Get a specific novel |
| PUT | `/api/novels/{id}` | Update a novel |
| POST | `/api/novels/{id}/generate` | Generate AI content with memory context |
| POST | `/api/memory/remember/{id}` | Store text in Cognee memory |
| POST | `/api/memory/recall/{id}` | Recall relevant memory |
| POST | `/api/memory/improve/{id}` | Run memify to derive new insights |
| DELETE | `/api/memory/forget/{id}/{item_id}` | Forget a specific memory item |
| GET | `/api/memory/stats/{id}` | Get memory statistics |
| GET | `/api/memory/graph/{id}` | Get the merged Cognee + structural knowledge graph |
| POST | `/api/consistency/check/{id}` | Run a consistency check |
| GET | `/api/characters/{id}` | Get characters for a novel |

Full interactive docs are available at `/docs` once the backend is running.

## 🛠️ Troubleshooting

**Ollama not responding**
```bash
ollama list      # Check if Ollama is running
ollama serve     # Restart it
```

**Cognee import or config errors**
```bash
pip uninstall cognee
pip install cognee
```
Also double-check `.env` has `LLM_API_KEY` and `HUGGINGFACE_TOKENIZER` set — Cognee's config validation fails without them, even for a fully local Ollama setup.

**Frontend build issues**
```bash
rm -rf node_modules package-lock.json
npm install
```

## 🗺️ Roadmap / What We'd Build Next

- Multi-user collaboration on a single novel's memory graph
- Export consistency reports as shareable PDFs
- Fine-grained memory pruning UI built on `forget()`
- Voice-to-draft input for on-the-go writing sessions

## 📝 License

MIT License — see `LICENSE` for details.

## 🙏 Acknowledgments

- [Cognee](https://www.cognee.ai) — the memory layer that makes this whole project possible
- [Ollama](https://ollama.ai) — local LLM runtime
- [WeMakeDevs](https://www.wemakedevs.org) — hackathon organizers
- *The Hangover Part AI: Where's My Context?* — hackathon theme that inspired this build

## 📞 Support

- Discord: WeMakeDevs Discord
- Issues: GitHub Issues on this repository

---

Built with ❤️ (and a lot of context) by **Team Hopeless** for The Hangover Part AI Hackathon.