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
from app.ui_theme import inject_custom_css, render_hero_banner, render_sidebar_student

st.set_page_config(page_title="AI Advisor | Academic Advisor", page_icon="💬", layout="wide")
inject_custom_css()

if "student" not in st.session_state:
    st.warning("⚠️ No student selected. Please select a student from the main page.")
    st.stop()

student: StudentProfile = st.session_state.student
render_sidebar_student(student)

render_hero_banner(
    title="💬 Conversational <span class='gradient-text'>Academic Advisor AI</span>",
    subtitle=f"Ask natural language questions about course eligibility, prerequisite chains, and university policies for <strong>{student.name}</strong>.",
    badge_text=f"🤖 Powered by Hybrid Graph-RAG & {MODEL_NAME}"
)

from app.ui_theme import render_help_tip
render_help_tip(
    title="How to Get the Best Advising Answers",
    explanation="Ask any question in plain English (e.g. <em>'Can I take Algorithms next semester?'</em> or <em>'What happens if I repeat a class?'</em>). The AI searches the Knowledge Graph and official University Policies, answers directly, and gives you verified policy citations so you know it's accurate!",
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

# Initialize chat history
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = [
        {
            "role": "assistant",
            "content": f"Hello **{student.name}**! 👋 I'm your AI Academic Advisor. I have access to your full academic transcript ({student.total_credits_earned} credits completed, GPA: {student.gpa:.2f}), the University Knowledge Graph, and official academic policies.\n\nHow can I help you plan your upcoming semesters or evaluate course prerequisites today?",
            "citations": ["Academic Advising Knowledge Base: Official Curriculum Catalog"],
            "conflicts": []
        }
    ]

# Header bar with reset button
h1, h2 = st.columns([4, 1])
with h1:
    st.markdown("##### 💡 Suggested Advising Prompts")
with h2:
    if st.button("🗑️ Reset Chat", use_container_width=True):
        st.session_state.chat_messages = [
            {
                "role": "assistant",
                "content": f"Hello **{student.name}**! 👋 How can I assist with your course planning today?",
                "citations": ["Academic Advising Knowledge Base"],
                "conflicts": []
            }
        ]
        st.rerun()

q_cols = st.columns(4)
quick_questions = [
    "Can I take CS301 (Algorithms) next term?",
    "What are the prerequisites for CS402 (Machine Learning)?",
    "Am I at risk of delaying my graduation?",
    "What course can substitute for CS350?"
]

for i, col in enumerate(q_cols):
    if col.button(quick_questions[i], use_container_width=True, key=f"quick_btn_{i}"):
        st.session_state.current_prompt = quick_questions[i]

st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

# Display past messages
for msg in st.session_state.chat_messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        
        if msg.get("conflicts"):
            for conf in msg["conflicts"]:
                st.markdown(f"<div style='background: rgba(239, 68, 68, 0.15); border-left: 3px solid #ef4444; padding: 8px 12px; border-radius: 6px; margin: 6px 0; color: #fca5a5;'>⚠️ {conf}</div>", unsafe_allow_html=True)
                
        if msg.get("citations"):
            with st.expander("📚 Citation Sources & Graph Verification"):
                for idx, c in enumerate(msg["citations"]):
                    st.markdown(f"- **[{idx+1}]** {c}")

# Handle input
user_input = st.chat_input("Ask about prerequisites, degree requirements, substitutions, policies...")
if "current_prompt" in st.session_state and st.session_state.current_prompt:
    user_input = st.session_state.current_prompt
    st.session_state.current_prompt = None

if user_input:
    # User message
    st.session_state.chat_messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)
        
    # Assistant response
    with st.chat_message("assistant"):
        with st.spinner("🤖 Traversing knowledge graph & retrieving policy context..."):
            result = advisor.chat_sync(user_input, student=student)
            
            response_text = result.get("response", "No response generated.")
            citations = result.get("citations", [])
            conflicts = result.get("conflicts", [])
            
            st.markdown(response_text)
            
            if conflicts:
                for conf in conflicts:
                    st.markdown(f"<div style='background: rgba(239, 68, 68, 0.15); border-left: 3px solid #ef4444; padding: 8px 12px; border-radius: 6px; margin: 6px 0; color: #fca5a5;'>⚠️ {conf}</div>", unsafe_allow_html=True)
                    
            if citations:
                with st.expander("📚 Citation Sources & Graph Verification"):
                    for idx, c in enumerate(citations):
                        st.markdown(f"- **[{idx+1}]** {c}")
                        
            st.session_state.chat_messages.append({
                "role": "assistant",
                "content": response_text,
                "citations": citations,
                "conflicts": conflicts
            })
