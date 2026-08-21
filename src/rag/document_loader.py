from dataclasses import dataclass
import re

@dataclass
class DocumentChunk:
    content: str
    metadata: dict
    chunk_id: str

class PolicyDocumentLoader:
    def load_and_chunk(self, file_path: str) -> list[DocumentChunk]:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except FileNotFoundError:
            return []
            
        sections = re.split(r'(?m)^## ', content)
        if not sections:
            return []
            
        chunks = []
        if sections[0].strip():
            chunks.append(DocumentChunk(
                content=sections[0].strip(),
                metadata={"section_title": "Introduction", "source_file": file_path, "type": "policy"},
                chunk_id="policy_intro"
            ))
            
        for i, section in enumerate(sections[1:], 1):
            lines = section.split('\n', 1)
            title = lines[0].strip()
            body = lines[1].strip() if len(lines) > 1 else ""
            
            section_id = f"policy_{i}"
            match = re.search(r'§\s*([\d\.]+)', title)
            if match:
                section_id = f"policy_{match.group(1).replace('.', '_')}"
                
            chunks.append(DocumentChunk(
                content=f"## {title}\n{body}",
                metadata={"section_title": title, "section_id": section_id, "source_file": file_path, "type": "policy"},
                chunk_id=section_id
            ))
            
        return chunks
    
    def load_course_descriptions(self, courses: list) -> list[DocumentChunk]:
        chunks = []
        for course in courses:
            cid = getattr(course, 'id', getattr(course, 'course_id', 'UNKNOWN'))
            cname = getattr(course, 'name', '')
            dept = getattr(course, 'department', '')
            credits = getattr(course, 'credits', 3)
            desc = getattr(course, 'description', '')
            
            content = f"Course: {cid} - {cname} (Dept: {dept}, Credits: {credits})\nDescription: {desc}\n"
            
            prereq_list = []
            if hasattr(course, 'prerequisite_groups'):
                for g in course.prerequisite_groups:
                    p_ids = [p.course_id for p in g.prerequisites]
                    logic = g.logic_type.value if hasattr(g.logic_type, 'value') else str(g.logic_type)
                    prereq_list.append(f"({' ' + logic + ' '.join(p_ids)})" if len(p_ids) > 1 else (p_ids[0] if p_ids else 'None'))
            if prereq_list:
                content += f"Prerequisites: {', '.join(prereq_list)}\n"
                
            chunks.append(DocumentChunk(
                content=content.strip(),
                metadata={"course_id": cid, "course_name": cname, "department": dept, "type": "course"},
                chunk_id=f"course_{cid}"
            ))
        return chunks
