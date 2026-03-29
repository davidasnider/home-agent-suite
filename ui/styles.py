import streamlit as st


def load_custom_css():
    """Load custom CSS for enhanced styling"""
    st.markdown(
        """
    <style>
    /* Main chat container styling */
    .stChatMessage {
        background-color: var(--background-color);
        border-radius: 15px;
        margin: 10px 0;
        padding: 15px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }

    /* User message styling */
    .stChatMessage[data-testid="user-message"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        margin-left: 20px;
    }

    /* Assistant message styling */
    .stChatMessage[data-testid="assistant-message"] {
        background: var(--secondary-background-color);
        border-left: 4px solid #00d4aa;
        margin-right: 20px;
    }

    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
    }

    /* Chat input styling */
    .stChatInput > div > div > input {
        border-radius: 25px;
        border: 2px solid #00d4aa;
        padding: 12px 20px;
    }

    /* Button styling */
    .stButton > button {
        border-radius: 20px;
        border: none;
        background: linear-gradient(45deg, #00d4aa 0%, #00b894 100%);
        color: white;
        font-weight: 600;
        transition: all 0.3s ease;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,212,170,0.3);
    }

    /* Typing indicator */
    .typing-indicator {
        display: flex;
        align-items: center;
        padding: 10px 20px;
        background: var(--secondary-background-color);
        border-radius: 15px;
        margin: 10px 0;
    }

    .typing-dots {
        display: flex;
        gap: 4px;
    }

    .typing-dots span {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #00d4aa;
        animation: typing 1.4s infinite;
    }

    .typing-dots span:nth-child(2) { animation-delay: 0.2s; }
    .typing-dots span:nth-child(3) { animation-delay: 0.4s; }

    @keyframes typing {
        0%, 60%, 100% { transform: translateY(0); opacity: 0.5; }
        30% { transform: translateY(-10px); opacity: 1; }
    }

    /* Mobile responsive adjustments */
    @media (max-width: 768px) {
        .stChatMessage {
            margin: 5px 0;
            padding: 12px;
        }

        .stChatMessage[data-testid="user-message"] {
            margin-left: 10px;
        }

        .stChatMessage[data-testid="assistant-message"] {
            margin-right: 10px;
        }
    }
    </style>
    """,
        unsafe_allow_html=True,
    )
