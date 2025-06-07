import streamlit as st

def create_sidebar():
    """Create the application sidebar"""
    with st.sidebar:
        st.header("🧠 Mental Health Predictor")
        
        # Navigation
        page = st.selectbox(
            "Navigate to:",
            ["Prediction", "History", "Analytics", "About"]
        )
        
        st.markdown("---")
        
        # Quick stats or info
        st.subheader("Quick Info")
        st.info("This tool provides risk assessment based on lifestyle factors.")
        
        # Help section
        st.subheader("Need Help?")
        if st.button("View Documentation"):
            st.markdown("Documentation would be displayed here.")
        
        return page
