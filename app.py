"""
Streamlit Chatbot Application Entrypoint

A lightweight orchestrator that imports components from the ui/ package
to build a modern, responsive chat interface.
"""

import streamlit as st
import logging
from ui.styles import load_custom_css
from ui.backend import initialize_session_state
from ui.components import render_sidebar, render_chat_interface, handle_user_input
from common_logging.logging_utils import setup_logging

# Initialize logging
setup_logging(service_name="streamlit_chatbot")
logger = logging.getLogger("streamlit_app")

# Page configuration
st.set_page_config(
    page_title="Home Agent Suite Chat",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": "https://github.com/davidasnider/home-agent-suite",
        "Report a bug": "https://github.com/davidasnider/home-agent-suite/issues",
        "About": (
            "Home Agent Suite - Intelligent home automation and planning" " assistant"
        ),
    },
)


def main():
    """Main application function"""
    try:
        # Load custom CSS
        load_custom_css()

        # Initialize session state
        initialize_session_state()

        # Render sidebar
        render_sidebar()

        # Render main chat interface
        render_chat_interface()

        # Handle user input
        handle_user_input()

        logger.info("Streamlit chatbot application rendered successfully")

    except Exception as e:
        logger.error(f"Error in main application: {str(e)}")
        st.error(f"❌ Application Error: {str(e)}")
        st.info("Please refresh the page or contact support if the issue persists.")


if __name__ == "__main__":
    main()
