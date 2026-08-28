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
            
        headings = list(re.finditer(r'(?m)^(#{2,3})\s+(.+?)\s*$', content))
        chunks = []
        intro_end = headings[0].start() if headings else len(content)
        if content[:intro_end].strip():
            chunks.append(DocumentChunk(
                content=content[:intro_end].strip(),
                metadata={"section_title": "Introduction", "section_id": "policy_intro", "source_file": file_path, "type": "policy", "source_status": "UNVERIFIED"},
                chunk_id="policy_intro"
            ))

        for i, heading in enumerate(headings, 1):
            end = headings[i].start() if i < len(headings) else len(content)
            title = heading.group(2).strip()
            body = content[heading.end():end].strip()
            source_match = re.search(r'\[([A-Z]+-[A-Z]-\d+)\]', title)
            section_id = source_match.group(1) if source_match else f"policy_{i}"
            status_match = re.search(r'\*\*Status:\*\*\s*`?([A-Z_]+)`?', body)
            source_status = status_match.group(1) if status_match else "UNVERIFIED"
            chunks.append(DocumentChunk(
                content=f"{heading.group(1)} {title}\n{body}",
                metadata={
                    "section_title": title,
                    "section_id": section_id,
                    "source_file": file_path,
                    "type": "policy",
                    "source_status": source_status,
                },
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
            
            knowledge_list = []
            for groups_name in ('prerequisite_groups', 'knowledge_requirement_groups'):
                for g in getattr(course, groups_name, []) or []:
                    p_ids = [p.course_id for p in g.prerequisites]
                    logic = g.logic_type.value if hasattr(g.logic_type, 'value') else str(g.logic_type)
                    knowledge_list.append(f"({' ' + logic + ' '.join(p_ids)})" if len(p_ids) > 1 else (p_ids[0] if p_ids else 'None'))
            if knowledge_list:
                content += f"Prerequisite knowledge (advisory): {', '.join(knowledge_list)}\n"
            formal_list = []
            for g in getattr(course, 'formal_prerequisite_groups', []) or []:
                p_ids = [p.course_id for p in g.prerequisites]
                formal_list.extend(p_ids)
            if formal_list:
                content += f"Formal registration prerequisites: {', '.join(formal_list)}\n"
                
            chunks.append(DocumentChunk(
                content=content.strip(),
                metadata={
                    "course_id": cid,
                    "course_name": cname,
                    "department": dept,
                    "type": "course",
                    "source_status": getattr(course, 'source_status', 'CURRICULUM_DERIVED'),
                    "reference": getattr(course, 'source_reference', None) or cid,
                },
                chunk_id=f"course_{cid}"
            ))
        return chunks
