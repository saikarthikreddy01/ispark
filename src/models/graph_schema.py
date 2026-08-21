"""Constants for knowledge graph node types and relationship types."""

# Node types
NODE_COURSE = "Course"
NODE_DEPARTMENT = "Department"
NODE_DEGREE_PROGRAM = "DegreeProgram"
NODE_CREDIT_CATEGORY = "CreditCategory"

# Edge / relationship types
REL_REQUIRES = "REQUIRES"           # prerequisite
REL_COREQUISITE = "COREQUISITE"
REL_EQUIVALENT = "EQUIVALENT_TO"
REL_BELONGS_TO = "BELONGS_TO"       # course -> department
REL_SATISFIES = "SATISFIES"         # course -> credit category
REL_PART_OF = "PART_OF"             # course -> degree program
