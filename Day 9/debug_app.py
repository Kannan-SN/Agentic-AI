#!/usr/bin/env python3
"""
Debug script to test Streamlit components
"""

import streamlit as st
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def main():
    st.title("🔧 Debug - Alumni Network Builder")
    st.write("Testing basic Streamlit functionality...")
    
    # Test 1: Basic Streamlit
    st.header("Test 1: Basic Streamlit ✅")
    st.write("If you can see this, Streamlit is working!")
    
    # Test 2: Configuration
    st.header("Test 2: Configuration")
    try:
        from config.settings import load_config
        config = load_config()
        st.success("✅ Configuration loaded successfully")
        st.write(f"Project root: {config.get('PROJECT_ROOT', 'Not found')}")
    except Exception as e:
        st.error(f"❌ Configuration error: {e}")
    
    # Test 3: Database
    st.header("Test 3: Database Connection")
    try:
        from database.mongodb_client import MongoDBClient
        db_client = MongoDBClient()
        if db_client.connect():
            st.success("✅ Database connected successfully")
        else:
            st.error("❌ Database connection failed")
    except Exception as e:
        st.error(f"❌ Database error: {e}")
    
    # Test 4: Agent Imports
    st.header("Test 4: AI Agent Imports")
    
    agents_status = {}
    
    # Test CrewAI
    try:
        from agents.crew_agent import CrewAlumniAgent
        agents_status['CrewAI'] = "✅ Available"
    except Exception as e:
        agents_status['CrewAI'] = f"❌ Error: {str(e)[:100]}"
    
    # Test LangChain
    try:
        from agents.langchain_agent import LangChainDomainAgent
        agents_status['LangChain'] = "✅ Available"
    except Exception as e:
        agents_status['LangChain'] = f"❌ Error: {str(e)[:100]}"
    
    # Test LangGraph
    try:
        from agents.langgraph_agent import LangGraphReferralAgent
        agents_status['LangGraph'] = "✅ Available"
    except Exception as e:
        agents_status['LangGraph'] = f"❌ Error: {str(e)[:100]}"
    
    # Test AutoGen
    try:
        from agents.autogen_agent import AutoGenOutreachAgent
        agents_status['AutoGen'] = "✅ Available"
    except Exception as e:
        agents_status['AutoGen'] = f"❌ Error: {str(e)[:100]}"
    
    for agent, status in agents_status.items():
        st.write(f"**{agent}:** {status}")
    
    # Test 5: RAG Pipeline
    st.header("Test 5: RAG Pipeline")
    try:
        from rag.rag_pipeline import RAGPipeline
        st.success("✅ RAG Pipeline import successful")
    except Exception as e:
        st.error(f"❌ RAG Pipeline error: {e}")
    
    # Test 6: UI Components
    st.header("Test 6: UI Components")
    try:
        from ui.components.dashboard import create_dashboard
        from ui.components.student_form import create_student_form
        st.success("✅ UI components import successful")
    except Exception as e:
        st.error(f"❌ UI components error: {e}")
    
    # Test 7: Google API
    st.header("Test 7: Google API Configuration")
    try:
        import google.generativeai as genai
        from config.settings import load_config
        config = load_config()
        
        api_key = config.get("GOOGLE_API_KEY")
        if api_key and api_key != "your_gemini_api_key_here":
            st.success("✅ Google API key configured")
            
            # Test API connection
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel("gemini-1.5-flash")
                response = model.generate_content("Hello")
                st.success("✅ Google API connection working")
            except Exception as api_e:
                st.error(f"❌ Google API connection failed: {api_e}")
        else:
            st.error("❌ Google API key not configured")
            st.info("Please add your Google API key to the .env file")
    except Exception as e:
        st.error(f"❌ Google API test error: {e}")
    
    # Summary
    st.header("🎯 Summary")
    st.write("If you see errors above, those are the issues preventing the main app from loading.")
    st.write("Once all tests show ✅, the main application should work properly.")

if __name__ == "__main__":
    main()