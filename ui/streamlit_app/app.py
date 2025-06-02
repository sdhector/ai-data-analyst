"""
AI Data Analyst - Streamlit Application

Main Streamlit application providing a chatbot interface with visualization capabilities.
Layout: Left panel (chatbot) + Right panel (visualization grid with 1-6 containers).
"""

import streamlit as st
import plotly.graph_objects as go
from typing import Dict, Any, List
import json
import os
from datetime import datetime

# Import our core modules
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from core.ai_engine import AIOrchestrator
from core.function_registry.grid_management_functions import get_grid_status, _grid_containers

# Page configuration
st.set_page_config(
    page_title="AI Data Analyst",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1rem 0;
        border-bottom: 2px solid #f0f2f6;
        margin-bottom: 2rem;
    }
    
    .chat-container {
        height: 600px;
        overflow-y: auto;
        padding: 1rem;
        border: 1px solid #e6e9ef;
        border-radius: 10px;
        background-color: #fafafa;
    }
    
    .user-message {
        background-color: #007bff;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 15px;
        margin: 0.5rem 0;
        margin-left: 2rem;
        text-align: right;
    }
    
    .assistant-message {
        background-color: #f8f9fa;
        color: #333;
        padding: 0.5rem 1rem;
        border-radius: 15px;
        margin: 0.5rem 0;
        margin-right: 2rem;
        border-left: 4px solid #28a745;
    }
    
    .function-call {
        background-color: #fff3cd;
        color: #856404;
        padding: 0.3rem 0.8rem;
        border-radius: 8px;
        margin: 0.2rem 0;
        font-size: 0.85em;
        border-left: 3px solid #ffc107;
    }
    
    .grid-container {
        border: 2px dashed #dee2e6;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem;
        min-height: 200px;
        background-color: #f8f9fa;
    }
    
    .grid-container-filled {
        border: 2px solid #28a745;
        background-color: white;
    }
    
    .status-indicator {
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        margin-right: 5px;
    }
    
    .status-success { background-color: #28a745; }
    .status-error { background-color: #dc3545; }
    .status-warning { background-color: #ffc107; }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize Streamlit session state variables"""
    if 'ai_orchestrator' not in st.session_state:
        st.session_state.ai_orchestrator = None
    
    if 'conversation_id' not in st.session_state:
        st.session_state.conversation_id = None
    
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    if 'system_status' not in st.session_state:
        st.session_state.system_status = None
    
    if 'grid_containers' not in st.session_state:
        st.session_state.grid_containers = {}

def initialize_ai_orchestrator():
    """Initialize the AI Orchestrator"""
    try:
        if st.session_state.ai_orchestrator is None:
            # Check for API key
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                st.error("🔑 OpenAI API key not found. Please set OPENAI_API_KEY in your environment variables.")
                st.info("Create a `.env` file in the project root with: `OPENAI_API_KEY=your_api_key_here`")
                return False
            
            # Initialize AI Orchestrator
            with st.spinner("🚀 Initializing AI Engine..."):
                st.session_state.ai_orchestrator = AIOrchestrator()
                
                # Test system status
                status = st.session_state.ai_orchestrator.get_system_status()
                st.session_state.system_status = status
                
                if status["status"] == "success":
                    # Create conversation
                    st.session_state.conversation_id = st.session_state.ai_orchestrator.conversation_manager.create_conversation()
                    st.success("✅ AI Engine initialized successfully!")
                    return True
                else:
                    st.error(f"❌ AI Engine initialization failed: {status.get('error', 'Unknown error')}")
                    return False
        
        return True
        
    except Exception as e:
        st.error(f"❌ Error initializing AI Engine: {str(e)}")
        return False

def render_chat_interface():
    """Render the chat interface in the left panel"""
    st.subheader("🤖 AI Data Analyst Chat")
    
    # System status indicator
    if st.session_state.system_status:
        status = st.session_state.system_status
        if status["status"] == "success":
            st.markdown('<span class="status-indicator status-success"></span>**System Online**', unsafe_allow_html=True)
            st.caption(f"Model: {status['configuration']['model']} | Functions: {status['functions']['total_available']}")
        else:
            st.markdown('<span class="status-indicator status-error"></span>**System Offline**', unsafe_allow_html=True)
    
    # Chat history container
    chat_container = st.container()
    
    with chat_container:
        if st.session_state.chat_history:
            for message in st.session_state.chat_history:
                if message["role"] == "user":
                    st.markdown(f'<div class="user-message">{message["content"]}</div>', unsafe_allow_html=True)
                elif message["role"] == "assistant":
                    st.markdown(f'<div class="assistant-message">{message["content"]}</div>', unsafe_allow_html=True)
                    
                    # Show function calls if any
                    if "function_calls" in message and message["function_calls"]:
                        for call in message["function_calls"]:
                            status_icon = "✅" if call["result"]["status"] == "success" else "❌"
                            st.markdown(f'<div class="function-call">{status_icon} Called: {call["function_name"]}</div>', unsafe_allow_html=True)
        else:
            st.info("👋 Welcome! I'm your AI Data Analyst. I can help you load datasets, create visualizations, and analyze data. Try asking me to 'Load the sales dataset and create a chart'!")
    
    # Chat input
    user_input = st.chat_input("Ask me anything about data analysis...")
    
    if user_input and st.session_state.ai_orchestrator:
        # Add user message to history
        st.session_state.chat_history.append({
            "role": "user",
            "content": user_input,
            "timestamp": datetime.now().isoformat()
        })
        
        # Process with AI
        with st.spinner("🧠 AI is thinking..."):
            response = st.session_state.ai_orchestrator.process_request(
                user_message=user_input,
                conversation_id=st.session_state.conversation_id,
                enable_functions=True
            )
        
        # Add assistant response to history
        if response["status"] == "success":
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": response["message"],
                "function_calls": response.get("function_calls", []),
                "timestamp": datetime.now().isoformat()
            })
        else:
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": f"❌ Error: {response.get('error', 'Unknown error')}",
                "timestamp": datetime.now().isoformat()
            })
        
        # Refresh the page to show new messages
        st.rerun()

def render_visualization_grid():
    """Render the visualization grid in the right panel"""
    st.subheader("📊 Visualization Grid")
    
    # Get current grid status
    grid_status = get_grid_status()
    
    if grid_status["status"] == "success":
        grid_info = grid_status["result"]
        containers = grid_info["containers"]
        
        # Grid status info
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Containers", f"{len(containers)}/6")
        with col2:
            st.metric("Available", f"{6 - len(containers)}")
        with col3:
            if st.button("🗑️ Clear Grid"):
                # Clear grid function call
                if st.session_state.ai_orchestrator:
                    result = st.session_state.ai_orchestrator.execute_function_directly("clear_grid", {})
                    if result["status"] == "success":
                        st.success("Grid cleared!")
                        st.rerun()
        
        # Render grid containers (2x3 layout)
        for row in range(2):
            cols = st.columns(3)
            for col_idx, col in enumerate(cols):
                position = row * 3 + col_idx + 1
                
                # Find container at this position
                container_at_position = None
                for container in containers:
                    if container["position"] == position:
                        container_at_position = container
                        break
                
                with col:
                    if container_at_position:
                        # Render filled container
                        render_container_content(container_at_position)
                    else:
                        # Render empty container placeholder
                        st.markdown(f"""
                        <div class="grid-container">
                            <center>
                                <h4>Position {position}</h4>
                                <p>Empty Container</p>
                                <small>Visualizations will appear here</small>
                            </center>
                        </div>
                        """, unsafe_allow_html=True)
    else:
        st.error(f"Error getting grid status: {grid_status.get('error', 'Unknown error')}")

def render_container_content(container: Dict[str, Any]):
    """Render content for a specific container"""
    container_id = container["id"]
    position = container["position"]
    content_type = container.get("content_type")
    title = container.get("title", f"Container {position}")
    
    # Container header
    st.markdown(f"**{title}** (Position {position})")
    
    # Get container content from global state
    if container_id in _grid_containers:
        container_data = _grid_containers[container_id]
        content = container_data.get("content")
        
        if content and content_type:
            try:
                if content_type == "chart":
                    # Render Plotly chart
                    if "chart_config" in content:
                        fig_dict = content["chart_config"]
                        fig = go.Figure(fig_dict)
                        st.plotly_chart(fig, use_container_width=True, key=f"chart_{container_id}")
                    else:
                        st.warning("Chart configuration not found")
                
                elif content_type == "table":
                    # Render data table
                    if "table_data" in content:
                        import pandas as pd
                        df = pd.DataFrame(content["table_data"])
                        st.dataframe(df, use_container_width=True, key=f"table_{container_id}")
                    else:
                        st.warning("Table data not found")
                
                else:
                    # Render as text/JSON
                    st.json(content)
                    
            except Exception as e:
                st.error(f"Error rendering content: {str(e)}")
        else:
            st.info("No content available")
    else:
        st.warning("Container data not found")
    
    # Container actions (no nested columns to avoid Streamlit limitation)
    st.markdown("---")
    
    # Use inline buttons without columns
    if st.button("🗑️ Remove Container", key=f"remove_{container_id}", help="Remove this container", use_container_width=True):
        if st.session_state.ai_orchestrator:
            result = st.session_state.ai_orchestrator.execute_function_directly("remove_container", {"container_id": container_id})
            if result["status"] == "success":
                st.success("Container removed!")
                st.rerun()

def render_sidebar():
    """Render the sidebar with additional controls"""
    with st.sidebar:
        st.title("🔧 Controls")
        
        # System status
        st.subheader("System Status")
        if st.session_state.system_status:
            status = st.session_state.system_status
            if status["status"] == "success":
                st.success("✅ System Online")
                
                # Usage stats
                if "llm_usage" in status:
                    usage = status["llm_usage"]
                    st.metric("Tokens Used", usage.get("total_tokens_used", 0))
                    st.metric("Requests", usage.get("request_count", 0))
                    st.metric("Est. Cost", f"${usage.get('estimated_cost_usd', 0):.4f}")
            else:
                st.error("❌ System Offline")
        
        # Conversation controls
        st.subheader("Conversation")
        if st.button("🗑️ Clear Chat"):
            st.session_state.chat_history = []
            if st.session_state.ai_orchestrator and st.session_state.conversation_id:
                st.session_state.ai_orchestrator.clear_conversation(st.session_state.conversation_id)
            st.rerun()
        
        # Function information
        st.subheader("Available Functions")
        if st.session_state.ai_orchestrator:
            functions_info = st.session_state.ai_orchestrator.get_available_functions()
            if functions_info["status"] == "success":
                st.metric("Total Functions", functions_info["total_functions"])
                
                # Show function categories
                categories = {
                    "📊 Data Analysis": ["load_", "filter_", "group_", "sort_", "calculate_", "get_"],
                    "📈 Visualization": ["create_"],
                    "🎛️ Grid Management": ["add_", "remove_", "clear_", "resize_", "update_"]
                }
                
                for category, prefixes in categories.items():
                    count = sum(1 for name in functions_info["functions"].keys() 
                              if any(name.startswith(prefix) for prefix in prefixes))
                    st.metric(category, count)

def main():
    """Main application function"""
    # Initialize session state
    initialize_session_state()
    
    # Header
    st.markdown('<div class="main-header"><h1>🤖 AI Data Analyst</h1><p>Intelligent Data Analysis with Conversational AI</p></div>', unsafe_allow_html=True)
    
    # Initialize AI Engine
    if not initialize_ai_orchestrator():
        st.stop()
    
    # Main layout: Left panel (chat) + Right panel (visualizations)
    left_panel, right_panel = st.columns([1, 2])
    
    with left_panel:
        render_chat_interface()
    
    with right_panel:
        render_visualization_grid()
    
    # Sidebar
    render_sidebar()

if __name__ == "__main__":
    main() 