from src.agents.state import AdvisorState
from src.utils.config import GEMINI_API_KEY, OPENAI_API_KEY, MODEL_NAME, DATA_DIR
from src.knowledge_graph.graph_builder import AcademicKnowledgeGraph
from src.rag.vector_store import AcademicVectorStore
from src.rag.document_loader import PolicyDocumentLoader
from src.rag.graph_retriever import GraphRAGRetriever
from src.constraint_engine.prerequisite_checker import PrerequisiteChecker
from src.constraint_engine.schedule_feasibility import ScheduleAnalyzer
import os

try:
    import google.genai as genai
except ImportError:
    genai = None

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

class AcademicAdvisor:
    def __init__(self, kg=None, vector_store=None, llm=None):
        if kg is None:
            self.kg = AcademicKnowledgeGraph()
            self.kg.load_from_json(
                str(DATA_DIR / "courses.json"),
                str(DATA_DIR / "degree_requirements.json"),
                str(DATA_DIR / "equivalencies.json")
            )
        else:
            self.kg = kg

        if vector_store is None:
            self.vector_store = AcademicVectorStore()
            loader = PolicyDocumentLoader()
            chunks = loader.load_and_chunk(str(DATA_DIR / "policies.md"))
            chunks += loader.load_course_descriptions(self.kg.get_all_courses())
            self.vector_store.add_documents(chunks)
        else:
            self.vector_store = vector_store
            
        self.retriever = GraphRAGRetriever(self.kg, self.vector_store)
        self.prereq_checker = PrerequisiteChecker(self.kg)
        self.schedule_analyzer = ScheduleAnalyzer(self.kg)
        
        self.llm = llm
        
        # OpenAI client initialization
        openai_key = os.getenv("OPENAI_API_KEY", OPENAI_API_KEY)
        self.openai_client = None
        if openai_key and OpenAI:
            try:
                self.openai_client = OpenAI(api_key=openai_key)
            except Exception:
                self.openai_client = None
                
        # Gemini client initialization
        gemini_key = os.getenv("GEMINI_API_KEY", GEMINI_API_KEY)
        self.gemini_client = None
        if gemini_key and genai and not self.openai_client:
            try:
                self.gemini_client = genai.Client(api_key=gemini_key)
            except Exception:
                self.gemini_client = None

    def classify_query(self, query: str) -> str:
        q = query.lower()
        if any(k in q for k in ["prereq", "require", "eligible", "can i take", "enroll"]):
            return "prerequisite"
        elif any(k in q for k in ["pathway", "plan", "roadmap", "schedule", "semesters"]):
            return "pathway"
        elif any(k in q for k in ["risk", "graduate", "ontime", "delay", "standing", "probation"]):
            return "risk"
        elif any(k in q for k in ["substitute", "instead of", "equivalent", "alternative"]):
            return "substitution"
        elif any(k in q for k in ["policy", "waiver", "transfer", "repeat", "gpa", "credit limit"]):
            return "policy"
        return "general"

    def chat_sync(self, message: str, student=None) -> dict:
        q_type = self.classify_query(message)
        retrieval = self.retriever.retrieve(message, student=student, top_k=4)
        
        context_parts = []
        if retrieval.graph_context:
            context_parts.append(f"### Academic Knowledge Graph Facts:\n{retrieval.graph_context}")
        if retrieval.policy_context:
            context_parts.append(f"### Relevant University Policies:\n{retrieval.policy_context}")
        if retrieval.course_context:
            context_parts.append(f"### Course Catalog Details:\n{retrieval.course_context}")
            
        full_context = "\n\n".join(context_parts)
        
        # Check for conflicts on mentioned courses if student provided
        detected_conflicts = []
        mentioned_courses = retrieval.raw_chunks
        course_refs = self.retriever._extract_course_references(message)
        
        completed = student.completed_course_ids if (student and hasattr(student, 'completed_course_ids')) else set()
        
        for cid in course_refs:
            if cid in completed:
                detected_conflicts.append(f"{cid} is already completed.")
            else:
                ok, missing = self.prereq_checker.check_prerequisites(cid, completed)
                if not ok:
                    detected_conflicts.append(f"Prerequisite missing for {cid}: requires {', '.join(missing)}")
                    
        # Generate LLM or rule-based response
        reply = ""
        citations_list = []
        for cite in retrieval.citations:
            ref = cite.get("reference", "")
            content = cite.get("content", "")
            citations_list.append(f"**{ref}**: {content[:160]}...")

        prompt = f"""You are an expert Academic Advisor AI. Use the provided Knowledge Graph facts and University Policies to answer the student's question accurately.
Include specific course codes, prerequisite rules, credit requirements, and policy citations in your response.

Student Information:
Name: {getattr(student, 'name', 'Student')}
Major: {getattr(student, 'major', 'Computer Science')}
Completed Courses: {', '.join(completed) if completed else 'None'}
GPA: {getattr(student, 'gpa', 0.0)}

Retrieved Knowledge & Policies:
{full_context}

Student Query: {message}

Provide a comprehensive, encouraging, and citation-backed answer:"""

        if self.openai_client:
            try:
                model = MODEL_NAME if MODEL_NAME.startswith(("gpt", "o1", "o3")) else "gpt-4o-mini"
                completion = self.openai_client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.2
                )
                reply = completion.choices[0].message.content
            except Exception as e:
                reply = self._build_deterministic_response(message, q_type, student, retrieval, detected_conflicts)
        elif self.gemini_client:
            try:
                response = self.gemini_client.models.generate_content(
                    model=MODEL_NAME,
                    contents=prompt
                )
                reply = response.text
            except Exception as e:
                reply = self._build_deterministic_response(message, q_type, student, retrieval, detected_conflicts)
        else:
            reply = self._build_deterministic_response(message, q_type, student, retrieval, detected_conflicts)
            
        return {
            "response": reply,
            "citations": citations_list if citations_list else ["Knowledge Graph: Official Curriculum Catalog"],
            "conflicts": detected_conflicts
        }

    def _build_deterministic_response(self, message: str, q_type: str, student, retrieval, conflicts) -> str:
        s_name = getattr(student, 'name', 'Student')
        completed = student.completed_course_ids if (student and hasattr(student, 'completed_course_ids')) else set()
        
        lines = [f"### 🎓 Academic Advising Assessment for {s_name}\n"]
        
        if conflicts:
            lines.append("⚠️ **Prerequisite Warnings Detected:**")
            for c in conflicts:
                lines.append(f"- {c}")
            lines.append("")
            
        if retrieval.graph_context:
            lines.append("📌 **Curriculum & Knowledge Graph Insights:**")
            lines.append(retrieval.graph_context)
            lines.append("")
            
        if retrieval.policy_context:
            lines.append("📜 **Relevant Policy Directives:**")
            lines.append(retrieval.policy_context[:400] + "...")
            lines.append("")
            
        if q_type == "prerequisite":
            lines.append("💡 **Recommendation:** Ensure all listed foundational courses are completed with a grade of 'C' or better before submitting your registration.")
        elif q_type == "risk":
            feas = self.schedule_analyzer.analyze_graduation_feasibility(student) if student else {}
            lines.append(f"💡 **Graduation Feasibility:** {feas.get('semesters_remaining', 0)} terms remaining. Risk Score: {feas.get('risk_score', 0.0):.2f}.")
        elif q_type == "substitution":
            lines.append("💡 **Substitution Rules:** Course substitutions require at least 75% learning outcome overlap and academic department approval per Policy §2.2.")
        else:
            lines.append("💡 **Advisor Note:** Review your degree audit in the Dashboard tab and consult your department advisor for exceptional override petitions.")
            
        return "\n".join(lines)

