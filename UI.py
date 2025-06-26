import streamlit as st
import requests
import time
import speech_recognition as sr
from streamlit_chat import message
from streamlit_lottie import st_lottie

# ============ CONFIGURATION ============
API_BASE = "http://127.0.0.1:8000/api/v1"

st.set_page_config(
    page_title="💬 RAG Chatbot",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom theme styling
st.markdown("""
    <style>
    html, body {
        background-color: #f6f9fc;
    }
    .stTextInput>div>div>input {
        background-color: #e3f2fd;
        color: #0d47a1;
    }
    .stTextArea>div>textarea {
        background-color: #e8f5e9;
        color: #1b5e20;
    }
    .stButton>button {
        background-color: #42a5f5;
        color: white;
        border-radius: 0.5rem;
        transition: 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #1e88e5;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🤖 RAG-based Chatbot with Voice Input")

# ============ STATE INITIALIZATION ============
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "vector_name" not in st.session_state:
    st.session_state.vector_name = ""

# ============ HELPERS ============

# Load Lottie animation from URL
def load_lottie_url(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        st.error("⚠️ Failed to load animation.")
        return None
    return r.json()

# Working chatbot animation
thinking_animation = load_lottie_url("https://assets2.lottiefiles.com/packages/lf20_qp1q7mct.json")

# Typewriter effect
def typewriter(text, delay=0.02):
    placeholder = st.empty()
    printed = ""
    for char in text:
        printed += char
        placeholder.markdown(f"<div style='font-size: 1.05rem; color: #2e7d32'><strong>{printed}</strong></div>", unsafe_allow_html=True)
        time.sleep(delay)
    placeholder.markdown(f"<div style='font-size: 1.05rem; color: #2e7d32'><strong>{printed}</strong></div>", unsafe_allow_html=True)

# ============ LAYOUT ============
tab1, tab2 = st.tabs(["🧠 Chatbot", "📄 Upload Document"])

# ============ 📄 Document Upload ============
with tab2:
    st.header("📄 Upload Resume or Document")
    uploaded_file = st.file_uploader("Upload `.txt` file", type=["txt"])
    if uploaded_file and st.button("🚀 Ingest into Vector DB"):
        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "text/plain")}
        with st.spinner("Ingesting..."):
            try:
                res = requests.post(f"{API_BASE}/ingest", files=files)
                if res.status_code == 200:
                    st.success("✅ Document ingested successfully!")
                else:
                    st.error(f"❌ Upload failed! {res.status_code}: {res.text}")
            except Exception as e:
                st.error(f"⚠️ Request failed: {e}")

# ============ 💬 Chatbot ============
with tab1:
    st.header("💬 Ask Questions")

    st.text_input("📚 Vector Name", key="vector_name")
    query = st.text_area("📝 Type your question to the bot")

    # 🎤 Voice Input
    with st.expander("🎙️ Use Voice Instead"):
        if st.button("🎧 Speak Now"):
            recognizer = sr.Recognizer()
            with sr.Microphone() as source:
                st.info("🎤 Listening for 5 seconds...")
                try:
                    audio = recognizer.listen(source, timeout=5)
                    transcript = recognizer.recognize_google(audio)
                    st.success(f"✅ You said: {transcript}")
                    query = transcript
                except sr.UnknownValueError:
                    st.error("😕 Couldn't understand your speech.")
                except sr.RequestError:
                    st.error("⚠️ Google Speech API unavailable.")

    if st.button("💬 Send Query"):
        if not st.session_state.vector_name:
            st.warning("❗ Vector name is required.")
        elif not query.strip():
            st.warning("❗ Please ask something.")
        else:
            url = f"{API_BASE}/chat?vector_name={st.session_state.vector_name}"
            headers = {"accept": "application/json", "Content-Type": "application/json"}
            data = {"query": query.strip()}

            with st.spinner("🤖 Thinking..."):
                if thinking_animation:
                    st_lottie(thinking_animation, height=140, key="loading-animation")
                else:
                    st.info("🤖 Thinking...")
                try:
                    res = requests.post(url, headers=headers, json=data)
                    if res.status_code == 200:
                        reply = res.json().get("response", "🤖 No response.")
                        st.session_state.chat_history.append(("user", query.strip()))
                        st.session_state.chat_history.append(("bot", reply))
                    else:
                        st.error(f"❌ Error {res.status_code}: {res.text}")
                except Exception as e:
                    st.error(f"❗ Request failed: {e}")

    # Chat history with avatars + typewriter
    if st.session_state.chat_history:
        st.markdown("---")
        st.subheader("📜 Chat History")
        for i, (role, msg) in enumerate(reversed(st.session_state.chat_history)):
            if role == "user":
                message(msg, is_user=True, key=f"user-{i}")
            else:
                message("", is_user=False, key=f"bot-{i}")
                typewriter(msg)

    if st.button("🧹 Clear Chat"):
        st.session_state.chat_history = []
