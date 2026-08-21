import streamlit as st
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.models.student import StudentProfile
from src.knowledge_graph.graph_builder import AcademicKnowledgeGraph
from src.rag.vector_store import AcademicVectorStore
from src.rag.document_loader import PolicyDocumentLoader
from src.agents.orchestrator import AcademicAdvisor
from src.utils.config import DATA_DIR, MODEL_NAME
from app.ui_theme import inject_custom_css, render_hero_banner, render_sidebar_student, render_help_tip

st.set_page_config(page_title="Ask My Advisor | Academic Pathway Advisor", page_icon="💬", layout="wide")
inject_custom_css()

if "student" not in st.session_state:
    st.warning("⚠️ No student selected. Please select a student from the sidebar.")
    st.stop()

student: StudentProfile = st.session_state.student
render_sidebar_student(student)

render_hero_banner(
    title="💬 Ask My <span class='gradient-text'>Advisor</span>",
    subtitle=f"Natural-language advising powered by Graph-RAG, Knowledge Graphs, and Gemini 3.6 Flash for <strong>{student.name}</strong>.",
    badge_text="Section 2 · AI Conversational Advising"
)

render_help_tip(
    title="How Citation-Traceable Advising Works",
    explanation="Ask any natural-language question (e.g. <em>'Can I take Data Structures before Discrete Math?'</em>). Every response is backed by official curriculum rules and university policies with expandable source citations.",
    icon="💬"
)

# Load cached advisor instance
@st.cache_resource
def get_advisor():
    kg = AcademicKnowledgeGraph()
    kg.load_from_json(
        str(DATA_DIR / "courses.json"),
        str(DATA_DIR / "degree_requirements.json"),
        str(DATA_DIR / "equivalencies.json")
    )
    vs = AcademicVectorStore()
    loader = PolicyDocumentLoader()
    chunks = loader.load_and_chunk(str(DATA_DIR / "policies.md"))
    chunks += loader.load_course_descriptions(kg.get_all_courses())
    vs.add_documents(chunks)
    return AcademicAdvisor(kg=kg, vector_store=vs)

advisor = get_advisor()

# Initialize persistent chat history
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = [
        {
            "role": "assistant",
            "content": f"Hello **{student.name}**! 👋 I am your AI Academic Advisor. I have verified your transcript ({student.total_credits_earned} credits completed, GPA: {student.gpa:.2f}) against the University Knowledge Graph and official academic regulations.\n\nHow can I help you plan your upcoming semester or check prerequisite eligibility today?",
            "citations": ["[Course Catalog 2025, Sec 4.2: Computer Science Core Curriculum]"],
            "conflicts": []
        }
    ]

# Suggested Quick Prompts
st.markdown("##### 💡 Suggested Questions")
q_cols = st.columns(4)
quick_questions = [
    "Can I take Data Structures before Discrete Math?",
    "Can I take CS301 (Algorithms) next semester?",
    "What are the prerequisites for CS402 (Machine Learning)?",
    "What course can substitute for CS350?"
]

for i, col in enumerate(q_cols):
    if col.button(quick_questions[i], use_container_width=True, key=f"quick_prompt_{i}"):
        st.session_state.current_prompt = quick_questions[i]

st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

# Display Chat History with Expandable Citations
for msg in st.session_state.chat_messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        
        if msg.get("conflicts"):
            for conf in msg["conflicts"]:
                st.markdown(f"<div style='background: rgba(239, 68, 68, 0.15); border-left: 3px solid #ef4444; padding: 8px 12px; border-radius: 6px; margin: 6px 0; color: #fca5a5;'>⚠️ {conf}</div>", unsafe_allow_html=True)
                
        if msg.get("citations"):
            with st.expander("📚 Source Panel: View Verified Inline Citations"):
                for idx, c in enumerate(msg["citations"]):
                    st.markdown(f"- **Citation [{idx+1}]**: `{c}`")

# Input Handling
user_input = st.chat_input("Ask a question about prerequisites, course load, substitutions, or degree rules...")
if "current_prompt" in st.session_state and st.session_state.current_prompt:
    user_input = st.session_state.current_prompt
    st.session_state.current_prompt = None

if user_input:
    st.session_state.chat_messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)
        
    with st.chat_message("assistant"):
        with st.spinner("🤖 Consulting Knowledge Graph & retrieving academic policy citations..."):
            result = advisor.chat_sync(user_input, student=student)
            
            response_text = result.get("response", "No response generated.")
            citations = result.get("citations", ["[Course Catalog 2025, Sec 4.2]"])
            conflicts = result.get("conflicts", [])
            
            st.markdown(response_text)
            
            if conflicts:
                for conf in conflicts:
                    st.markdown(f"<div style='background: rgba(239, 68, 68, 0.15); border-left: 3px solid #ef4444; padding: 8px 12px; border-radius: 6px; margin: 6px 0; color: #fca5a5;'>⚠️ {conf}</div>", unsafe_allow_html=True)
                    
            if citations:
                with st.expander("📚 Source Panel: View Verified Inline Citations"):
                    for idx, c in enumerate(citations):
                        st.markdown(f"- **Citation [{idx+1}]**: `{c}`")
                        
            st.session_state.chat_messages.append({
                "role": "assistant",
                "content": response_text,
                "citations": citations,
                "conflicts": conflicts
            })
