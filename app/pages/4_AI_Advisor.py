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
from src.utils.config import DATA_DIR

st.set_page_config(page_title="AI Advisor | Academic Advisor", page_icon="💬", layout="wide")

st.title("💬 Graph-RAG Academic Advisor AI")
st.markdown("Ask natural language questions about course eligibility, prerequisite chains, graduation timelines, and university policies with **citation-traceable answers**.")

if "student" not in st.session_state:
    st.warning("⚠️ No student selected. Please select a student from the main page.")
    st.stop()

student: StudentProfile = st.session_state.student

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
            "content": f"Hello **{student.name}**! 👋 I'm your AI Academic Advisor. I have access to your full transcript ({student.total_credits_earned} credits completed, GPA: {student.gpa:.2f}), the University Knowledge Graph, and official academic policies. How can I assist with your course planning today?",
            "citations": ["Academic Advising Knowledge Base"],
            "conflicts": []
        }
    ]

# Quick action sample questions
st.markdown("##### 💡 Suggested Questions")
q_cols = st.columns(4)
quick_questions = [
    f"Can I take CS301 (Algorithms) next term?",
    f"What are the prerequisites for CS402 (Machine Learning)?",
    f"Am I at risk of delaying my graduation?",
    f"What can I take instead of CS350 (Web Dev)?"
]

def set_quick_prompt(q):
    st.session_state.current_prompt = q

for i, col in enumerate(q_cols):
    if col.button(quick_questions[i], use_container_width=True):
        st.session_state.current_prompt = quick_questions[i]

# Display past messages
for msg in st.session_state.chat_messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        
        if msg.get("conflicts"):
            for conf in msg["conflicts"]:
                st.error(f"⚠️ {conf}")
                
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
                    st.error(f"⚠️ {conf}")
                    
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

