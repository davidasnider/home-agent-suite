import types
import streamlit as st
import ui.backend as backend


class DummySession(dict):
    """Minimal session_state that supports both dict and attribute access."""

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)

    def __setattr__(self, name, value):
        self[name] = value


def test_create_demo_agent_and_chat():
    # Use __new__ to avoid heavy initialization in __init__
    mgr = backend.ChatbotManager.__new__(backend.ChatbotManager)
    demo = mgr._create_demo_agent()
    resp = demo.chat("hello world")
    assert "Demo Agent Response" in resp
    assert "hello world" in resp


def test_get_primary_agent_logic():
    mgr = backend.ChatbotManager.__new__(backend.ChatbotManager)
    # When supervisor is present
    mgr.agents = {"supervisor": object()}
    assert mgr.get_primary_agent() == "supervisor"

    # When supervisor missing
    mgr.agents = {"demo": object()}
    assert mgr.get_primary_agent() == "demo"


def test_initialize_session_state_creates_manager_and_messages(monkeypatch):
    # Ensure new instances pick the demo fallback
    monkeypatch.setattr(backend, "SUPERVISOR_AVAILABLE", False)
    # Ensure the module-level supervisor_error exists to avoid NameError
    backend.supervisor_error = "supervisor not present"

    dummy = DummySession()
    monkeypatch.setattr(st, "session_state", dummy, raising=False)

    # Call initialize - should populate messages and chatbot_manager
    backend.initialize_session_state()

    assert "messages" in st.session_state
    assert isinstance(st.session_state.messages, list)
    assert "chatbot_manager" in st.session_state
    # chatbot_manager should be an instance of ChatbotManager
    assert isinstance(st.session_state.chatbot_manager, backend.ChatbotManager)


def test_extract_text_from_event_variants():
    mgr = backend.ChatbotManager.__new__(backend.ChatbotManager)

    # event with actions -> action.text
    Action = types.SimpleNamespace
    ev1 = types.SimpleNamespace(actions=[Action(text="from action")])
    assert mgr._extract_text_from_event(ev1) == "from action"

    # event with actions -> action.content.parts[].text
    Part = types.SimpleNamespace
    Content = types.SimpleNamespace
    action_with_parts = Action(content=Content(parts=[Part(text="part text")]))
    ev2 = types.SimpleNamespace(actions=[action_with_parts])
    assert mgr._extract_text_from_event(ev2) == "part text"

    # event with content.parts
    ev3 = types.SimpleNamespace(content=Content(parts=[Part(text="content part")]))
    assert mgr._extract_text_from_event(ev3) == "content part"

    # event with content.text
    ev4 = types.SimpleNamespace(content=Content(text="content text"))
    assert mgr._extract_text_from_event(ev4) == "content text"

    # event with direct text
    ev5 = types.SimpleNamespace(text="direct text")
    assert mgr._extract_text_from_event(ev5) == "direct text"

    # event with no text
    ev6 = types.SimpleNamespace()
    assert mgr._extract_text_from_event(ev6) is None
