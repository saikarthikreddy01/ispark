"""Constants for knowledge graph node types and relationship types."""

NODE_COURSE = "Course"
NODE_DEPARTMENT = "Department"
NODE_DEGREE_PROGRAM = "DegreeProgram"
NODE_CREDIT_CATEGORY = "CreditCategory"

# Academic relationship types.
REL_REQUIRES = "FORMAL_PREREQUISITE"     # registration-blocking, authoritative rule only
REL_KNOWLEDGE = "REQUIRES_KNOWLEDGE_OF" # non-blocking academic readiness/background
REL_COREQUISITE = "COREQUISITE"
REL_EQUIVALENT = "EQUIVALENT_TO"
REL_BELONGS_TO = "BELONGS_TO"
REL_SATISFIES = "SATISFIES"
REL_PART_OF = "PART_OF"
