# app.py - Research Knowledge Copilot
import streamlit as st
import json
import pickle
import networkx as nx
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path
import random

# Page configuration
st.set_page_config(
    page_title="Research Knowledge Copilot",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better appearance
st.markdown("""
<style>
    .stButton button {
        width: 100%;
    }
    .css-1d391kg {
        padding: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.title("📚 Research Knowledge Copilot")
st.markdown("*GraphRAG-powered Research Assistant*")

# Sidebar
with st.sidebar:
    st.header("📁 Data Files")
    st.markdown("---")
    
    # File status indicators
    files_status = {
        "knowledge_graph.json": Path("knowledge_graph.json").exists(),
        "extracted_knowledge.json": Path("extracted_knowledge.json").exists(),
        "graphrag_system.pkl": Path("graphrag_system.pkl").exists(),
        "chunks_for_entity_extraction.json": Path("chunks_for_entity_extraction.json").exists(),
        "knowledge_graph.graphml": Path("knowledge_graph.graphml").exists()
    }
    
    for file, exists in files_status.items():
        if exists:
            st.success(f"✅ {file}")
        else:
            st.error(f"❌ {file}")
    
    st.markdown("---")
    st.info("💡 **How to use:**\n1. Explore the graph visualization\n2. Search for entities\n3. Ask questions about your research")

# Function to load knowledge graph
@st.cache_resource
def load_graph():
    """Load knowledge graph from JSON file"""
    try:
        if Path("knowledge_graph.json").exists():
            with open("knowledge_graph.json", 'r') as f:
                data = json.load(f)
            G = nx.node_link_graph(data)
            return G
        elif Path("knowledge_graph.graphml").exists():
            return nx.read_graphml("knowledge_graph.graphml")
        else:
            return None
    except Exception as e:
        st.error(f"Error loading graph: {e}")
        return None

# Function to load extracted knowledge
@st.cache_data
def load_extracted_knowledge():
    """Load extracted entities and relationships"""
    try:
        if Path("extracted_knowledge.json").exists():
            with open("extracted_knowledge.json", 'r') as f:
                return json.load(f)
    except Exception as e:
        st.error(f"Error loading knowledge: {e}")
    return None

# Function to load chunks
@st.cache_data
def load_chunks():
    """Load text chunks"""
    try:
        if Path("chunks_for_entity_extraction.json").exists():
            with open("chunks_for_entity_extraction.json", 'r') as f:
                return json.load(f)
    except Exception as e:
        st.error(f"Error loading chunks: {e}")
    return None

# Load all data
with st.spinner("Loading knowledge graph..."):
    G = load_graph()
    knowledge_data = load_extracted_knowledge()
    chunks = load_chunks()

# Main content area with tabs
tab1, tab2, tab3, tab4 = st.tabs(["📊 Graph Overview", "🔍 Entity Search", "📝 Extracted Knowledge", "🤖 Query Assistant"])

# Tab 1: Graph Overview
with tab1:
    if G is not None:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Number of Nodes", G.number_of_nodes())
        with col2:
            st.metric("Number of Edges", G.number_of_edges())
        with col3:
            density = nx.density(G)
            st.metric("Graph Density", f"{density:.3f}")
        with col4:
            if G.number_of_nodes() > 0:
                avg_degree = 2 * G.number_of_edges() / G.number_of_nodes()
                st.metric("Average Degree", f"{avg_degree:.2f}")
        
        # Graph visualization with Plotly
        st.subheader("📊 Knowledge Graph Visualization")
        
        if G.number_of_nodes() > 0:
            # Create a layout for the graph
            pos = nx.spring_layout(G, k=2, iterations=50)
            
            # Create edge traces
            edge_x = []
            edge_y = []
            for edge in G.edges():
                x0, y0 = pos[edge[0]]
                x1, y1 = pos[edge[1]]
                edge_x.extend([x0, x1, None])
                edge_y.extend([y0, y1, None])
            
            edge_trace = go.Scatter(
                x=edge_x, y=edge_y,
                line=dict(width=0.5, color='#888'),
                hoverinfo='none',
                mode='lines')
            
            # Create node traces
            node_x = []
            node_y = []
            node_text = []
            
            for node in G.nodes():
                x, y = pos[node]
                node_x.append(x)
                node_y.append(y)
                node_text.append(str(node))
            
            node_trace = go.Scatter(
                x=node_x, y=node_y,
                mode='markers+text',
                text=node_text,
                textposition="top center",
                hoverinfo='text',
                marker=dict(
                    showscale=True,
                    colorscale='YlOrRd',
                    size=10,
                    colorbar=dict(title="Node"),
                )
            )
            
            fig = go.Figure(data=[edge_trace, node_trace],
                           layout=go.Layout(
                               title='Knowledge Graph',
                               showlegend=False,
                               hovermode='closest',
                               xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                               yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                               height=600
                           ))
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Node degree distribution
            st.subheader("📈 Node Degree Distribution")
            degrees = [d for n, d in G.degree()]
            fig_hist = px.histogram(x=degrees, nbins=20, title="Distribution of Node Degrees")
            fig_hist.update_layout(xaxis_title="Degree", yaxis_title="Frequency")
            st.plotly_chart(fig_hist, use_container_width=True)
    else:
        st.error("No knowledge graph found. Please ensure knowledge_graph.json or knowledge_graph.graphml exists.")

# Tab 2: Entity Search
with tab2:
    st.subheader("🔍 Search for Entities")
    
    if G is not None and G.number_of_nodes() > 0:
        # Get all nodes
        all_nodes = sorted(list(G.nodes()))
        
        # Search box
        search_term = st.text_input("Enter entity name or keyword:")
        
        if search_term:
            # Find matching nodes
            matches = [node for node in all_nodes if search_term.lower() in str(node).lower()]
            
            if matches:
                st.success(f"Found {len(matches)} matching entities")
                
                for match in matches[:10]:  # Show first 10 matches
                    with st.expander(f"📌 {match}"):
                        # Get neighbors
                        neighbors = list(G.neighbors(match))
                        st.write(f"**Connections:** {len(neighbors)}")
                        if neighbors:
                            st.write("**Connected to:**")
                            for neighbor in neighbors[:5]:
                                st.write(f"- {neighbor}")
                            if len(neighbors) > 5:
                                st.write(f"... and {len(neighbors)-5} more")
            else:
                st.warning("No matching entities found")
        
        # Browse all entities
        st.subheader("📋 Browse All Entities")
        selected_entity = st.selectbox("Select an entity:", all_nodes)
        
        if selected_entity:
            st.write(f"### {selected_entity}")
            neighbors = list(G.neighbors(selected_entity))
            st.write(f"**Connected to {len(neighbors)} entities:**")
            
            for neighbor in neighbors:
                st.write(f"- {neighbor}")
    else:
        st.warning("No graph data available")

# Tab 3: Extracted Knowledge
with tab3:
    st.subheader("📝 Extracted Knowledge")
    
    if knowledge_data:
        # Display statistics
        if isinstance(knowledge_data, dict):
            st.json(knowledge_data)
        elif isinstance(knowledge_data, list):
            st.write(f"**Total items:** {len(knowledge_data)}")
            
            # Show first few items
            for i, item in enumerate(knowledge_data[:10]):
                with st.expander(f"Item {i+1}"):
                    st.json(item)
            
            if len(knowledge_data) > 10:
                st.info(f"Showing 10 of {len(knowledge_data)} items")
    else:
        st.warning("No extracted knowledge found")
    
    # Show chunks if available
    if chunks:
        st.subheader("📄 Text Chunks")
        if isinstance(chunks, list):
            st.write(f"**Total chunks:** {len(chunks)}")
            chunk_num = st.number_input("View chunk number:", min_value=1, max_value=len(chunks), value=1)
            st.text_area(f"Chunk {chunk_num}:", value=str(chunks[chunk_num-1]), height=200)

# Tab 4: Query Assistant
with tab4:
    st.subheader("🤖 Research Query Assistant")
    
    st.markdown("""
    Ask questions about your research data. Examples:
    - "What are the main topics in my research?"
    - "Show me relationships between key concepts"
    - "Summarize the extracted knowledge"
    """)
    
    user_query = st.text_area("Your question:", height=100)
    
    if st.button("Ask", type="primary"):
        if user_query:
            with st.spinner("Analyzing your query..."):
                # Simple response based on available data
                response = []
                
                if G:
                    response.append(f"📊 **Knowledge Graph Stats:**")
                    response.append(f"- {G.number_of_nodes()} concepts/entities")
                    response.append(f"- {G.number_of_edges()} relationships")
                    
                    # Find important nodes (high degree)
                    if G.number_of_nodes() > 0:
                        degrees = dict(G.degree())
                        top_nodes = sorted(degrees.items(), key=lambda x: x[1], reverse=True)[:5]
                        response.append(f"\n🏆 **Most connected concepts:**")
                        for node, degree in top_nodes:
                            response.append(f"- {node} ({degree} connections)")
                
                if knowledge_data:
                    response.append(f"\n📚 **Extracted Knowledge:**")
                    if isinstance(knowledge_data, dict):
                        for key, value in list(knowledge_data.items())[:3]:
                            response.append(f"- {key}: {str(value)[:100]}...")
                    elif isinstance(knowledge_data, list):
                        response.append(f"- Found {len(knowledge_data)} knowledge items")
                
                if chunks:
                    response.append(f"\n📄 **Text Analysis:**")
                    response.append(f"- {len(chunks)} text chunks available for analysis")
                    total_chars = sum(len(str(chunk)) for chunk in chunks)
                    response.append(f"- ~{total_chars//1000}K characters of text")
                
                st.markdown("\n".join(response))
                
                # Simple response to query
                st.info(f"💡 Based on your query: *{user_query}*\n\nThis assistant can help you explore your knowledge graph. Try using the search and visualization tabs above to find specific information!")
        else:
            st.warning("Please enter a question")

# Footer
st.markdown("---")
st.markdown("🚀 **Research Knowledge Copilot** | Powered by GraphRAG, LangChain, and Streamlit")