import streamlit as st
import time
import json
import html
from datetime import datetime


def export_chat_history():
    """Export chat history as JSON"""
    try:
        chat_data = {
            "conversation_id": st.session_state.conversation_id,
            "export_timestamp": datetime.now().isoformat(),
            "message_count": len(st.session_state.messages),
            "messages": st.session_state.messages,
        }
        json_string = json.dumps(chat_data, indent=2, ensure_ascii=False)
        st.download_button(
            label="💾 Download Chat History",
            data=json_string,
            file_name=f"chat_history_{st.session_state.conversation_id}.json",
            mime="application/json",
            use_container_width=True,
        )
        st.success("✅ Chat history prepared for download!")
    except Exception as e:
        st.error(f"❌ Error exporting chat history: {str(e)}")


def render_sidebar():
    """Render the sidebar with settings and controls"""
    with st.sidebar:
        st.title("🏠 Home Agent Suite")
        st.markdown("---")
        st.subheader("🤖 Intelligent Agent")
        primary_agent = st.session_state.chatbot_manager.get_primary_agent()
        if primary_agent == "supervisor":
            st.success("🧠 **Supervisor Agent Active**")
            st.markdown("""
            The supervisor agent intelligently routes your queries to:
            - 🌤️ **Weather & Planning** for forecasts and activities
            - 🔍 **Web Search** for information and research
            """)
        else:
            st.warning("🎭 **Demo Mode**")
            st.markdown("Using demo agent - check configuration for full functionality")
        st.markdown("---")
        st.subheader("💬 Conversation")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🗑️ Clear Chat", use_container_width=True):
                st.session_state.messages = [st.session_state.messages[0]]
                st.session_state.conversation_id = f"chat_{int(time.time())}"
                st.rerun()
        with col2:
            if st.button("📥 Export Chat", use_container_width=True):
                export_chat_history()
        st.markdown("---")
        st.subheader("📊 Statistics")
        message_count = len(
            [msg for msg in st.session_state.messages if msg["role"] == "user"]
        )
        st.metric("Messages Sent", message_count)
        st.metric("Conversation ID", st.session_state.conversation_id[-8:])
        st.markdown("---")
        st.subheader("ℹ️ About")
        st.markdown("""
        This chatbot integrates with:
        - **Day Planner Agent**: Weather-based activity planning
        - **Google Search Agent**: Real-time information retrieval
        Built with Streamlit and Google ADK.
        """)


def show_typing_indicator():
    """Show typing indicator while processing"""
    typing_placeholder = st.empty()
    with typing_placeholder.container():
        st.markdown(
            """
        <div class="typing-indicator">
            <span>🤖 Assistant is typing</span>
            <div class="typing-dots">
                <span></span>
                <span></span>
                <span></span>
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )
    time.sleep(1.5)
    typing_placeholder.empty()


def render_chat_interface():
    """Render the main chat interface"""
    st.title("💬 Home Agent Chat")
    st.markdown("Ask me about day planning, weather insights, or general questions!")
    for message in st.session_state.messages:
        role = message["role"]
        content = message["content"]
        agent = message.get("agent", "unknown")
        timestamp = message.get("timestamp", "")
        try:
            dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            time_display = dt.strftime("%H:%M")
        except Exception:
            time_display = ""
        avatar = (
            "👤"
            if role == "user"
            else (
                "🗓️"
                if agent == "day_planner"
                else ("🔍" if agent == "google_search" else "🤖")
            )
        )
        with st.chat_message(role, avatar=avatar):
            st.markdown(content)
            if time_display:
                st.caption(f"⏰ {time_display}")


def handle_user_input():
    """Handle user input and generate response"""
    if prompt := st.chat_input("Type your message here..."):
        current_time = time.time()
        if current_time - st.session_state.last_request_time < 3:
            st.toast("You are sending requests too quickly. Please wait a moment.")
            return
        st.session_state.last_request_time = current_time
        try:
            prompt.encode("utf-8").decode("utf-8")
        except UnicodeDecodeError:
            st.toast("Error: Invalid input encoding. Please use UTF-8.")
            return
        if len(prompt) > 1024:
            st.toast(
                "Error: Input is too long. Please limit your query to 1024 characters."
            )
            return
        sanitized_prompt = html.escape(prompt)
        user_message = {
            "role": "user",
            "content": sanitized_prompt,
            "timestamp": datetime.now().isoformat(),
            "agent": "user",
        }
        st.session_state.messages.append(user_message)
        with st.chat_message("user", avatar="👤"):
            st.markdown(sanitized_prompt)
        with st.chat_message("assistant", avatar="🤖"):
            show_typing_indicator()
            selected_agent = st.session_state.chatbot_manager.get_primary_agent()
            response = st.session_state.chatbot_manager.get_agent_response(
                selected_agent, sanitized_prompt
            )
            st.markdown(response)
            assistant_message = {
                "role": "assistant",
                "content": response,
                "timestamp": datetime.now().isoformat(),
                "agent": selected_agent,
            }
            st.session_state.messages.append(assistant_message)
            agent_title = selected_agent.replace("_", " ").title()
            timestamp = datetime.now().strftime("%H:%M")
            st.caption(f"⏰ {timestamp} • Agent: {agent_title}")
