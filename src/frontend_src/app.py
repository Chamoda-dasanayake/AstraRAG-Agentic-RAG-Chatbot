import sys
import os

# Add project root to sys.path BEFORE any imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import streamlit as st
import requests
from src.frontend_src.config.frontend_settings import Settings

settings = Settings()

# ------------------ Page Config ------------------
st.set_page_config(
    page_title="AstraRAG",
    page_icon="🤖",
    layout="centered",
)

st.title("🤖 AstraRAG - Agentic RAG Chatbot")

# ------------------ Session State ------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ------------------ Render Chat History ------------------
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

        # Only assistant messages have extra metadata
        if message.get("role") == "assistant":
            sources = message.get("sources", [])
            tool_used = message.get("tool_used")
            rationale = message.get("rationale")

            if sources:
                st.markdown(f"**Sources:** {', '.join(sources)}")

            if tool_used or rationale:
                with st.expander("Show details (tool & rationale)"):
                    st.markdown(f"**Tool Used:** {tool_used if tool_used else 'N/A'}")
                    st.markdown(f"**Rationale:** {rationale if rationale else 'N/A'}")

# ------------------ User Input ------------------
user_prompt = st.chat_input("Ask Chatbot ...")

if user_prompt:
    # Show user message
    st.chat_message("user").markdown(user_prompt)

    # Save to history
    st.session_state.chat_history.append({
        "role": "user",
        "content": user_prompt
    })

    payload = {"chat_history": st.session_state.chat_history}

    # ------------------ API Call ------------------
    with st.spinner("🤔 Thinking..."):
        try:
            response = requests.post(
                settings.CHAT_ENDPOINT_URL,
                json=payload,
                timeout=120
            )
            response.raise_for_status()
            data = response.json()

            assistant_response = data.get("answer", "(No response)")
            tool_used = data.get("tool_used", "N/A")
            rationale = data.get("rationale", "N/A")
            sources = data.get("sources", [])

        except requests.exceptions.Timeout:
            assistant_response = "Error: Request timed out. Please try again."
            tool_used = "N/A"
            rationale = "N/A"
            sources = []

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                assistant_response = "Error: Rate limited. Please wait and try again."
            else:
                assistant_response = f"Error: {e.response.status_code} {e.response.reason}"
            tool_used = "N/A"
            rationale = "N/A"
            sources = []

        except Exception as e:
            assistant_response = f"Error: {str(e)}"
            tool_used = "N/A"
            rationale = "N/A"
            sources = []

    # Save assistant message
    st.session_state.chat_history.append({
        "role": "assistant",
        "content": assistant_response,
        "tool_used": tool_used,
        "rationale": rationale,
        "sources": sources
    })

    # ------------------ Render Assistant Reply ------------------
    with st.chat_message("assistant"):
        st.markdown(assistant_response)

        if sources:
            st.markdown(f"**Sources:** {', '.join(sources)}")

        with st.expander("Show details (tool & rationale)"):
            st.markdown(f"**Tool Used:** {tool_used}")
            st.markdown(f"**Rationale:** {rationale}")