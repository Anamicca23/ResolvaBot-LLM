<div align="center">
  
<img width="1376" height="768" alt="resolvabot llm" src="https://github.com/user-attachments/assets/b83ca1d8-9382-44e8-9538-e5d5a44ffea5" />

<br/>

<img src="https://img.shields.io/badge/Python-3.9%2B-3776AB?style=for-the-badge&logo=python&logoColor=white"/>
<img src="https://img.shields.io/badge/Streamlit-1.28%2B-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white"/>
<img src="https://img.shields.io/badge/Groq-Llama_3.3_70B-00C7B7?style=for-the-badge&logo=meta&logoColor=white"/>
<img src="https://img.shields.io/badge/FAISS-Vector_Store-0066CC?style=for-the-badge&logo=meta&logoColor=white"/>
<img src="https://img.shields.io/badge/License-MIT-22C55E?style=for-the-badge"/>

<br/><br/>

# 📚 ResolvaBot LLM

### *AI-Powered Textbook Intelligence — Ask Anything, Get Expert Answers*

<p>
A next-generation PDF Q&amp;A platform combining <strong>RAPTOR hierarchical indexing</strong>,
<strong>Hybrid BM25 + Dense retrieval</strong>, and <strong>Llama 3.3 70B via Groq</strong>
to turn any textbook into an interactive AI tutor — with source citations, code examples,
and complexity analysis in every answer.
</p>

<br/>

[![Run Locally](https://img.shields.io/badge/⚡%20Run%20Locally-localhost:8501-7C6AF7?style=for-the-badge)](http://localhost:8501)
&nbsp;
[![Report Bug](https://img.shields.io/badge/🐛%20Report%20Bug-GitHub-f43f5e?style=for-the-badge)](https://github.com/Anamicca23/ResolvaBot-LLM/issues)
&nbsp;
[![Groq Free](https://img.shields.io/badge/🆓%20Groq%20API-Free%20Tier-22C55E?style=for-the-badge)](https://console.groq.com)

<br/>

---

### ✨ Upload a PDF → Index in seconds → Get expert AI answers with source citations ✨

---

</div>

<br/>

## 📋 Table of Contents

- [🚀 What is ResolvaBot?](#-what-is-resolvabot)
- [✨ Features](#-features)
- [🏗️ Architecture](#️-architecture)
- [📁 Project Structure](#-project-structure)
- [⚙️ System Requirements](#️-system-requirements)
- [🛠️ Installation](#️-installation)
- [🔑 API Keys Setup](#-api-keys-setup)
- [▶️ Running the App](#️-running-the-app)
- [🖥️ Using the Interface](#️-using-the-interface)
- [🔬 Technical Deep Dive](#-technical-deep-dive)
- [🎨 UI Themes](#-ui-themes)
- [🧪 Testing the Pipeline](#-testing-the-pipeline)
- [🔧 Troubleshooting](#-troubleshooting)
- [📦 Full Dependencies List](#-full-dependencies-list)
- [🤝 Contributing](#-contributing)

<br/>

---

## 🚀 What is ResolvaBot?

ResolvaBot LLM is a **desktop-first, locally-hosted AI study assistant** that transforms any PDF textbook into a fully searchable, intelligent Q&A knowledge base. It combines cutting-edge retrieval techniques with large language models to deliver structured, cited, code-inclusive answers — just like having a senior tutor available 24/7.


**Who is it built for?**

| Audience | Use Case |
|---|---|
| 🎓 **Students** | Ask questions directly from CS / algorithms / science textbooks |
| 👨‍🏫 **Educators** | Surface relevant passages for lecture preparation instantly |
| 🔬 **Researchers** | Query technical PDFs, papers, and manuals with precision |
| 💻 **Developers** | Understand codebases by uploading technical documentation |

<br/>

<img width="1360" height="624" alt="image" src="https://github.com/user-attachments/assets/b31eae86-2850-401a-860d-ab64d4cc4a73" />

---

## ✨ Features

### 🤖 AI & Retrieval Engine

| Feature | Details |
|---|---|
| **RAPTOR Hierarchical Index** | Recursive GMM clustering + LLM summarization — builds a tree-structured index for multi-granularity retrieval (leaf → branch → root) |
| **Hybrid BM25 + Dense Search** | Keyword matching (Whoosh BM25) + SBERT semantic vectors (FAISS cosine) working together |
| **Reciprocal Rank Fusion (RRF)** | Merges and re-ranks results from both retrieval branches for maximum combined relevance |
| **WordNet Query Expansion** | Automatically expands queries with synonyms to improve recall on paraphrased content |
| **Multi-Model LLM Auto-Fallback** | 5-level fallback: Groq Llama 3.3 70B → Llama 3.1 70B → Llama 3 8B → OpenAI GPT-3.5 → Wikipedia → Raw context |
| **Wikipedia Live Fallback** | When PDF context is insufficient, fetches real-time Wikipedia articles to answer |
| **Source Passage Attribution** | Every answer shows which passages were retrieved and their exact RRF relevance scores |
| **Markdown + Code Answers** | All LLM responses render full markdown — headers, code blocks with syntax highlighting, tables, bold |

### 📄 PDF Processing Pipeline

| Feature | Details |
|---|---|
| **PyMuPDF Extraction** | Fast, accurate text extraction from any digital PDF |
| **Tesseract OCR Fallback** | Automatically uses OCR for scanned / image-based PDFs when detected |
| **NLTK Sentence Chunking** | Smart chunking that preserves sentence boundaries (~100 tokens per chunk) |
| **SBERT Embeddings** | `all-MiniLM-L6-v2` — 384-dimensional semantic embeddings, CPU-fast |
| **FAISS Vector Store** | In-memory approximate nearest-neighbor search — no Docker, no server required |
| **Real-Time 5-Step Progress** | Live pipeline dashboard: Extract → Chunk → RAPTOR → FAISS → BM25 |

### 🖥️ UI & User Experience

| Feature | Details |
|---|---|
| **3-Page Navigation** | Upload & Index → Chat → Sources & PDF Preview |
| **Collapsible Sidebar** | Hamburger ☰ menu with navigation, theme switcher, document info, action buttons |
| **4 Color Themes** | Dark, Light, Indigo, Teal — switches instantly with no reload |
| **ChatGPT-Style Chat Interface** | Bot on left with markdown rendering, user on right with gradient bubbles |
| **Full-Height PDF Viewer** | Native browser PDF rendering with zoom, scroll, search toolbar |
| **No Full-Page Scroll** | Fixed viewport layout — chat and sources scroll independently |
| **Desktop-First Design** | Centered 860px max-width container — optimized for widescreen monitors |
| **Professional Topbar** | Fixed navigation bar with LLM status badge and indexed status indicator |
| **Document Summary Card** | Pages, chunks, RAPTOR nodes, and file size shown after indexing |

<br/>

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      USER UPLOADS PDF                           │
└──────────────────────────┬──────────────────────────────────────┘
                           │
            ┌──────────────▼──────────────┐
            │   1. TEXT EXTRACTION        │
            │   PyMuPDF → OCR fallback    │
            └──────────────┬──────────────┘
                           │
            ┌──────────────▼──────────────┐
            │   2. SENTENCE CHUNKING      │
            │   NLTK → ~100 tokens/chunk  │
            └──────────────┬──────────────┘
                           │
            ┌──────────────▼──────────────┐
            │   3. SBERT EMBEDDINGS       │
            │   all-MiniLM-L6-v2 384-dim  │
            └──────────────┬──────────────┘
                           │
         ┌─────────────────▼─────────────────┐
         │        4. RAPTOR INDEXING          │
         │  Level 0: Original chunks          │
         │    ↓ GMM soft clustering           │
         │  Level 1: LLM cluster summaries    │
         │    ↓ Re-embed + cluster again      │
         │  Level 2: High-level abstractions  │
         │  All nodes stored for retrieval    │
         └──────────┬──────────────┬──────────┘
                    │              │
         ┌──────────▼───┐  ┌───────▼──────┐
         │  FAISS Index │  │  BM25 Index  │
         │  Dense vecs  │  │  Whoosh KW   │
         └──────────────┘  └──────────────┘

               USER ASKS A QUESTION
                        │
         ┌──────────────▼──────────────┐
         │   WordNet Query Expansion   │
         └──────────────┬──────────────┘
                        │
         ┌──────────────▼──────────────────────┐
         │         HYBRID RETRIEVAL            │
         │  BM25 Top-20  +  FAISS Top-20       │
         │         RRF Re-Ranking              │
         │         → Final Top-8               │
         └──────────────┬──────────────────────┘
                        │
         ┌──────────────▼──────────────────────────────┐
         │         LLM ANSWER GENERATION               │
         │  1st → Groq Llama 3.3 70B (free, fast)      │
         │  2nd → Groq Llama 3.1 70B                   │
         │  3rd → Groq Llama 3 8B                      │
         │  4th → OpenAI GPT-3.5 Turbo                 │
         │  5th → Wikipedia API (live articles)        │
         │  6th → Raw context excerpt (last resort)    │
         └──────────────────────────────────────────────┘
```

<br/>

---

## 📁 Project Structure

```
ResolvaBot-LLM/
│
├── 📄 app.py                      # Main Streamlit app — UI, routing, 3 page views
├── 📋 requirements.txt            # All Python dependencies with pinned versions
├── 🔧 setup.sh                    # Automated one-command setup (Linux / macOS)
├── 🔧 setup.bat                   # Automated one-command setup (Windows)
├── 🧪 test_pipeline.py            # Full pipeline validation — no API key needed
├── 🔐 .env.example                # API key template — copy to .env
├── 📖 README.md                   # This documentation file
│
└── 📂 src/                        # Core backend modules
    ├── 🔍 extraction.py           # PyMuPDF PDF text extraction + Tesseract OCR fallback
    ├── ✂️  chunking.py             # NLTK sentence-aware text chunking (~100 token chunks)
    ├── 🧠 embeddings.py           # SBERT all-MiniLM-L6-v2 embedding generation
    ├── 🌲 raptor_index.py         # RAPTOR: GMM clustering + recursive LLM summarization
    ├── ⚡ vector_store.py          # FAISS in-memory vector database (no Docker required)
    ├── 🔎 retrieval.py            # Hybrid BM25 + Dense + RRF re-ranking + WordNet expansion
    └── 💬 question_answering.py   # Multi-model LLM with 5-level auto-fallback chain
```

<br/>

---

## ⚙️ System Requirements

### Hardware

| Component | Minimum | Recommended |
|---|---|---|
| **RAM** | 4 GB | 8 GB+ |
| **Disk** | 3 GB (models + deps) | 5 GB+ |
| **CPU** | Any modern dual-core | Quad-core+ |
| **GPU** | Not required | Optional (speeds embeddings) |

### Software

| Requirement | Minimum | Recommended |
|---|---|---|
| **OS** | Windows 10, macOS 11, Ubuntu 20.04 | Any modern 64-bit OS |
| **Python** | 3.9 | 3.11+ |
| **Browser** | Chrome 90+, Firefox 88+ | Chrome (best PDF viewer support) |
| **Internet** | Required for 1st run (SBERT download) | Broadband |

<br/>

---

## 🛠️ Installation

### Method 1 — Automated Setup ⭐ Recommended

**Linux / macOS:**
```bash
git clone https://github.com/Anamicca23/ResolvaBot-LLM.git
cd ResolvaBot-LLM
bash setup.sh
```

**Windows:**
```bash
git clone https://github.com/Anamicca23/ResolvaBot-LLM.git
cd ResolvaBot-LLM
setup.bat
```

> The script automatically creates a virtualenv, installs all dependencies, downloads NLTK data, and creates your `.env` file.

---

### Method 2 — Manual Step-by-Step

```bash
# 1. Clone repository
git clone https://github.com/Anamicca23/ResolvaBot-LLM.git
cd ResolvaBot-LLM

# 2. Create virtual environment
python -m venv venv

# 3. Activate
source venv/bin/activate        # Linux / macOS
# venv\Scripts\activate.bat    # Windows

# 4. Install all dependencies
pip install -r requirements.txt

# 5. Download NLTK required data
python -c "
import nltk
nltk.download('punkt_tab')
nltk.download('punkt')
nltk.download('wordnet')
nltk.download('averaged_perceptron_tagger')
"

# 6. Set up environment file
cp .env.example .env
# Then edit .env and add your API keys
```

---

### Optional: Install Tesseract OCR (for scanned PDFs)

```bash
# Ubuntu / Debian
sudo apt-get install tesseract-ocr

# macOS (Homebrew)
brew install tesseract

# Windows
# Download installer: https://github.com/UB-Mannheim/tesseract/wiki
```

> Tesseract is **optional** — only needed if your PDFs are scanned images rather than digital text.

<br/>

---

## 🔑 API Keys Setup

### Option A — Groq (FREE & Recommended ⭐)

Groq provides **free** access to Llama 3.3 70B — blazing fast, highest quality, no billing required.

1. Sign up at **[console.groq.com](https://console.groq.com)** — free, no credit card
2. Navigate to **API Keys** → **Create API Key**
3. Add to your `.env` file:

```env
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

---

### Option B — OpenAI GPT-3.5 (Paid, Fallback)

1. Sign up at **[platform.openai.com/api-keys](https://platform.openai.com/api-keys)**
2. Add to `.env`:

```env
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

---

### Option C — No API Key (Wikipedia Mode)

The app **runs fully without any API key**. Answers come from Wikipedia when the PDF context is insufficient. Ideal for testing the pipeline or offline use.

---

### Automatic LLM Fallback Chain

```
Your Question
     │
     ▼
Groq Llama 3.3 70B ──(fail)──► Groq Llama 3.1 70B
                                       │
                              (fail)───▼
                          Groq Llama 3 8B
                                       │
                              (fail)───▼
                          OpenAI GPT-3.5 Turbo
                                       │
                              (fail)───▼
                          Wikipedia Live Article
                                       │
                              (fail)───▼
                          Raw context excerpt
```

<br/>

---

## ▶️ Running the App

```bash
# Activate virtual environment first
source venv/bin/activate          # Linux / macOS
# venv\Scripts\activate.bat      # Windows

# Optional: Verify the pipeline works without API key
python test_pipeline.py
# ✅ All 6 tests passed! Pipeline is working correctly.

# Launch the app
streamlit run app.py
```

Open **[http://localhost:8501](http://localhost:8501)** in your browser.

> 💡 **First run note:** SBERT downloads `all-MiniLM-L6-v2` (~90 MB) on first startup. This takes 1-2 minutes once. All subsequent runs start in seconds.

<br/>

---

## 🖥️ Using the Interface

### Page 1 — Upload & Index

```
① Drag & drop any PDF (up to 200 MB) or click to browse
② Watch the real-time 5-step pipeline execute:

   📝 Extract Text     → PyMuPDF reads all pages
   ✂️  Chunk Text       → NLTK splits into ~100-token chunks
   🌲 RAPTOR Index     → GMM clusters + LLM summarizes (2 levels)
   ⚡ FAISS Store      → Dense embeddings indexed
   📑 BM25 Index       → Keyword inverted index built

③ Document Summary card appears showing:
   • Total pages extracted
   • Number of text chunks
   • RAPTOR tree nodes (chunks + summaries)
   • File size
   • Embedding model used

④ Click "💬 Start Chatting →" to open Chat page
```

---

### Page 2 — Chat

```
① Type any question about the textbook content
② ResolvaBot retrieves the 8 most relevant passages using hybrid search
③ Llama 3.3 70B synthesizes a structured answer including:
   • Concept/intuition explained first
   • Step-by-step details
   • Working code examples with syntax highlighting
   • Time & space complexity analysis
   • Source attribution (which model answered, from textbook or Wikipedia)

④ Click "📋 N source passages" expander to inspect retrieved passages
   • Each passage shows: page number, relevance score, full text
   • Code passages render with syntax highlighting
```

---

### Page 3 — Sources & PDF

```
① Full-height PDF viewer with native browser controls:
   • Page navigation
   • Zoom in/out
   • Text search within PDF
   • Download option
② The PDF viewer renders the currently loaded document
③ Switch back to Chat to ask more questions
```

---

### Sidebar Menu (click ☰ top-left)

```
NAVIGATION
  📂 Upload & Index   → Go to upload page
  💬 Chat             → Go to chat page
  🔍 Sources & PDF    → View PDF

COLOR THEME
  🔵 ⬛ 🟣 🟢 🔴 🟠 ⚫    → 7 theme swatches

DOCUMENT (when PDF is loaded)
  📄 filename.pdf
  296 pages · 1260 chunks · 1.0 MB
  📂 Unload PDF       → Clear and start fresh
  🗑 Clear Chat       → Reset conversation history
```

<br/>

---

## 🔬 Technical Deep Dive

### RAPTOR Indexing — How It Works

RAPTOR (Recursive Abstractive Processing for Tree-Organized Retrieval) solves a fundamental limitation of standard RAG:

> **Standard RAG:** Only retrieves from leaf-level chunks. Fails at "big picture" or cross-chapter questions.
>
> **RAPTOR:** Builds a tree. Retrieves from all levels. Answers both specific facts AND thematic questions.

```
Original Chunks (Level 0)
  "Binary search runs in O(log n)..."
  "A sorted array is required for binary search..."
  "The mid-point is calculated as (lo + hi) / 2..."
         │
         ▼ GMM Soft Clustering
  Cluster A: 3 chunks about binary search
  Cluster B: 4 chunks about sorting algorithms
         │
         ▼ LLM Summarize each cluster
  Summary A: "Binary search is a divide-and-conquer algorithm..."
  Summary B: "Sorting algorithms order elements using comparisons..."
         │
         ▼ Re-embed, cluster again (Level 2)
  Root summary: "Chapter 3 covers search and sorting algorithms..."
```

The final FAISS index contains **all nodes** — original chunks + every level of summaries. This means a question like "What is this chapter about?" can be answered from root nodes, while "What is the time complexity of binary search?" is answered from leaf nodes.

---

### Hybrid Retrieval — Why Both Methods?

| Situation | BM25 Wins | Dense Wins |
|---|---|---|
| "What is `quicksort`?" | ✅ Exact keyword match | |
| "What is the fast sorting method?" | | ✅ Semantic similarity |
| "O(n log n) algorithm" | ✅ Exact notation | |
| "Efficient ordering technique" | | ✅ Conceptual match |

**Reciprocal Rank Fusion** mathematically combines both rankings:
```
RRF_score(doc) = Σ 1 / (60 + rank_in_list_i)
```
The constant `60` prevents high-ranking documents from dominating completely, giving fair weight to documents that appear in both lists.

---

### Embedding Model

| Property | Value |
|---|---|
| Model | `sentence-transformers/all-MiniLM-L6-v2` |
| Dimensions | 384 |
| Download size | ~90 MB |
| Inference | CPU (no GPU required) |
| Similarity metric | Cosine distance |

---

### LLM System Prompt Design

The system prompt enforces structured, educational responses:

- **Concept first** — explain the intuition before the details
- **Code examples** — all algorithm questions get working code in the correct language
- **Complexity analysis** — time and space complexity always mentioned for algorithms
- **Markdown structure** — headers, bullets, numbered steps for organization
- **Minimum depth** — 4-10 sentences minimum, never one-line answers
- **No raw context dumping** — always synthesizes, never pastes

<br/>

---

## 🎨 UI Themes

Switch anytime via **☰ Menu → Color Theme**:

| Theme | Accent | Background | Best For |
|---|---|---|---|
| 🌑 **Dark** | `#58a6ff` Blue | `#0d1117` Almost Black | Extended sessions, night use |
| ☀️ **Light** | `#0969da` Blue | `#f6f8fa` Off-White | Bright environments, printing |
| 🔮 **Indigo** | `#7c6af7` Purple | `#0f0e17` Deep Purple | Creative / focused work |
| 🌊 **Teal** | `#2dd4bf` Teal | `#0a1628` Deep Blue | High contrast reading |

All theme variables cascade through the entire UI — topbar, sidebar, cards, chat bubbles, code blocks, progress bars, and scrollbars all update immediately.

<br/>

---

## 🧪 Testing the Pipeline

```bash
# Activate venv first, then:
python test_pipeline.py
```

What each test validates:

| # | Test | Checks |
|---|---|---|
| ① | PDF Extraction | PyMuPDF reads text from a sample PDF correctly |
| ② | Text Chunking | NLTK splits text into correct chunk sizes with sentence boundaries |
| ③ | SBERT Embeddings | Model loads and produces correct 384-dim vectors |
| ④ | RAPTOR Indexing | GMM clustering runs and produces multi-level node tree |
| ⑤ | FAISS Store | Vectors stored and nearest-neighbor search returns correct results |
| ⑥ | BM25 Index | Whoosh indexes text and returns keyword matches |

Expected output:
```
✅ Test 1 — PDF Extraction:   PASSED
✅ Test 2 — Text Chunking:    PASSED
✅ Test 3 — SBERT Embeddings: PASSED
✅ Test 4 — RAPTOR Indexing:  PASSED
✅ Test 5 — FAISS Store:      PASSED
✅ Test 6 — BM25 Index:       PASSED
────────────────────────────────────
✅ All 6 tests passed! Pipeline is working correctly.
```

<br/>

---

## 🔧 Troubleshooting

<details>
<summary><b>❌ ModuleNotFoundError on startup</b></summary>

The virtual environment may not be activated or dependencies weren't installed:

```bash
# Activate venv
source venv/bin/activate       # Linux / macOS
venv\Scripts\activate.bat      # Windows

# Reinstall
pip install -r requirements.txt
```
</details>

<details>
<summary><b>❌ NLTK punkt_tab / wordnet errors</b></summary>

```bash
python -c "
import nltk
nltk.download('punkt_tab')
nltk.download('punkt')
nltk.download('wordnet')
nltk.download('averaged_perceptron_tagger')
"
```
</details>

<details>
<summary><b>❌ Groq / OpenAI API errors</b></summary>

- Confirm your key is in `.env` with no extra spaces or quotes
- Verify the key is valid at the provider's dashboard
- The app **automatically falls back** to Wikipedia if any key is invalid — answers still work
</details>

<details>
<summary><b>❌ Slow first run (5+ minutes)</b></summary>

This is expected on the **very first run only**. SBERT downloads `all-MiniLM-L6-v2` (~90 MB). Once cached in `~/.cache/huggingface/`, all subsequent runs start in seconds.
</details>

<details>
<summary><b>❌ PDF shows "No readable text found"</b></summary>

Your PDF is a scanned image rather than digital text. Install Tesseract:
```bash
# Ubuntu
sudo apt-get install tesseract-ocr

# macOS
brew install tesseract

# Windows: https://github.com/UB-Mannheim/tesseract/wiki
```
Then re-upload the PDF — OCR activates automatically.
</details>

<details>
<summary><b>❌ Out of memory during RAPTOR indexing</b></summary>

For very large PDFs (500+ pages), RAPTOR may use significant RAM. The pipeline processes in batches automatically. If you hit limits, the app continues with fewer RAPTOR levels and still works correctly.
</details>

<details>
<summary><b>❌ Chat input doesn't respond</b></summary>

Hard-refresh your browser (`Ctrl+Shift+R` or `Cmd+Shift+R`) to clear any cached Streamlit state.
</details>

<details>
<summary><b>❌ PDF viewer not showing the document</b></summary>

Chrome has the best support for the base64 PDF data URI used by the viewer. If using Firefox or Edge and the viewer appears blank, try switching to Chrome.
</details>

<br/>

---

## 📦 Full Dependencies List

```
# Core
numpy >= 1.24.0
pandas >= 2.0.0

# PDF Extraction
pymupdf >= 1.23.0
pytesseract >= 0.3.10
Pillow >= 10.0.0

# NLP & Text Processing
nltk >= 3.8.1

# Embeddings & ML
sentence-transformers >= 2.2.2
transformers >= 4.33.0
torch >= 2.0.0
scikit-learn >= 1.3.0
faiss-cpu >= 1.7.4

# BM25 Keyword Index
whoosh >= 2.7.4

# LLM Providers
groq                     # Free Llama 3.3 70B
openai >= 1.0.0          # GPT-3.5 Turbo fallback

# Wikipedia Fallback
wikipedia-api >= 0.6.0

# Environment & Config
python-dotenv >= 1.0.0

# Web UI
streamlit >= 1.28.0
```

Install all at once:
```bash
pip install -r requirements.txt
```

<br/>

---

## 🤝 Contributing

Contributions, bug reports, and feature requests are very welcome!

```bash
# 1. Fork the repository on GitHub

# 2. Clone your fork
git clone https://github.com/Anamicca23/ResolvaBot-LLM.git
cd ResolvaBot-LLM

# 3. Create a feature branch
git checkout -b feature/your-feature-name

# 4. Make your changes and test
python test_pipeline.py

# 5. Commit and push
git commit -m "feat: describe your change clearly"
git push origin feature/your-feature-name

# 6. Open a Pull Request on GitHub
```

**Ideas welcome for contribution:**

- 📁 Support for DOCX, EPUB, HTML, Markdown files
- 🤖 Additional LLM providers (Anthropic Claude, Google Gemini, local Ollama)
- 💾 Persistent vector store (save index to disk, reload on next session)
- 📤 Export chat history as PDF or Markdown
- 🗂️ Multi-PDF sessions (query across multiple books simultaneously)
- 🐳 Docker containerization for easier deployment
- 🌍 Multi-language PDF support

<br/>

---

<div align="center">

---

<br/>

**Built with ❤️ using Python, Streamlit, RAPTOR, FAISS, and Groq**

*ResolvaBot LLM — Making every textbook infinitely queryable*

<br/>

[![⬆️ Back to Top](https://img.shields.io/badge/⬆️%20Back%20to%20Top-Click%20Here-7C6AF7?style=for-the-badge)](#-resolvabot-llm)

<br/>

</div>
