# 📚 Research Knowledge Copilot

A **GraphRAG-powered** research assistant that transforms extracted knowledge into an interactive, explorable knowledge graph. Built with Streamlit, it lets you visualize entity relationships, search concepts, and query your research data through a clean web interface.

---

## Features

- **Knowledge Graph Visualization** — Interactive graph rendered with Plotly showing nodes (concepts/entities) and edges (relationships), including degree distribution histograms.
- **Entity Search** — Search and browse entities by name or keyword, inspect their connections and neighbors.
- **Extracted Knowledge Explorer** — Browse raw extracted knowledge items and text chunks from your research corpus.
- **Query Assistant** — Ask natural language questions about your research data; the assistant surfaces graph stats, top-connected concepts, and chunk summaries.
- **Data File Status Panel** — Sidebar shows at a glance which data files are loaded and ready.

---

## Tech Stack

| Layer | Library |
|---|---|
| UI | Streamlit |
| Graph | NetworkX |
| Visualization | Plotly |
| Data | Pandas, NumPy |
| LLM / RAG | LangChain, LangChain-Community, OpenAI |
| Knowledge Source | Wikipedia |

---

## Project Structure

```
research-knowledge-copilot/
├── app.py                          # Main Streamlit application
├── knowledge_graph.json            # Knowledge graph (node-link format)
├── knowledge_graph.graphml         # Knowledge graph (GraphML format, fallback)
├── extracted_knowledge.json        # Extracted entities and relationships
├── chunks_for_entity_extraction.json  # Source text chunks
├── graphrag_system.pkl             # Serialized GraphRAG system state
└── requirements.txt                # Python dependencies
```

---

## Getting Started

### Prerequisites

- Python 3.8+
- An OpenAI API key (for LLM-powered features)

### Installation

```bash
git clone https://github.com/mariammuroob/research-knowledge-copilot.git
cd research-knowledge-copilot

pip install -r requirements.txt
```

### Running the App

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`.

> **Note:** The app expects the data files (`knowledge_graph.json`, `extracted_knowledge.json`, etc.) to be present in the root directory. The sidebar will show a red ❌ for any missing files and a green ✅ for files that are loaded successfully.

---

## Usage

The app is organized into four tabs:

1. **Graph Overview** — See high-level graph metrics (node count, edge count, density, average degree) and explore the interactive force-directed graph visualization.
2. **Entity Search** — Type a keyword to find matching entities and inspect their connections, or browse all entities via a dropdown.
3. **Extracted Knowledge** — Browse the raw JSON knowledge items and paginate through the source text chunks.
4. **Query Assistant** — Ask a free-form question about your research. The assistant responds with relevant graph statistics and knowledge summaries.

---

## Dependencies

```
streamlit
networkx
matplotlib
plotly
pandas
numpy
langchain
langchain-community
wikipedia
openai
```

Install all at once with:

```bash
pip install -r requirements.txt
```

---

## License

This project is open source. See the repository for details.
