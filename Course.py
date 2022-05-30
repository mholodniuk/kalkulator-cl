from dataclasses import dataclass

@dataclass
class Course:
    id: str # course id
    course_name: str # course name
    class_types: str # course type
    ects_value: int # ECTS value 
    grade: float # final grade
