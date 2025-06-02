#!/usr/bin/env python3
"""
AI Data Analyst - Main Application Entry Point
"""

import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path

def main():
    """Main application function"""
    st.set_page_config(
        page_title="AI Data Analyst",
        page_icon="📊",
        layout="wide"
    )
    
    st.title("🤖 AI Data Analyst")
    st.markdown("Welcome to your intelligent data analysis companion!")
    
    # Sidebar for file upload
    st.sidebar.header("Data Upload")
    uploaded_file = st.file_uploader(
        "Choose a data file",
        type=['csv', 'xlsx', 'json'],
        help="Upload your data file to get started with analysis"
    )
    
    if uploaded_file is not None:
        # Load data based on file type
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            elif uploaded_file.name.endswith('.xlsx'):
                df = pd.read_excel(uploaded_file)
            elif uploaded_file.name.endswith('.json'):
                df = pd.read_json(uploaded_file)
            
            st.success(f"Successfully loaded {uploaded_file.name}")
            
            # Display basic info
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Rows", len(df))
            with col2:
                st.metric("Columns", len(df.columns))
            with col3:
                st.metric("Memory Usage", f"{df.memory_usage(deep=True).sum() / 1024:.1f} KB")
            
            # Show data preview
            st.subheader("Data Preview")
            st.dataframe(df.head())
            
            # Basic statistics
            if st.checkbox("Show Statistical Summary"):
                st.subheader("Statistical Summary")
                st.dataframe(df.describe())
                
        except Exception as e:
            st.error(f"Error loading file: {str(e)}")
    else:
        st.info("👆 Please upload a data file to begin analysis")
        
        # Show sample data for demo
        st.subheader("Demo with Sample Data")
        if st.button("Load Sample Dataset"):
            # Create sample data
            np.random.seed(42)
            sample_data = pd.DataFrame({
                'Date': pd.date_range('2023-01-01', periods=100),
                'Sales': np.random.normal(1000, 200, 100),
                'Region': np.random.choice(['North', 'South', 'East', 'West'], 100),
                'Product': np.random.choice(['A', 'B', 'C'], 100)
            })
            
            st.dataframe(sample_data.head())
            st.line_chart(sample_data.set_index('Date')['Sales'])

if __name__ == "__main__":
    main() 