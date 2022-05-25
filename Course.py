from dataclasses import dataclass

@dataclass
class Course:
    id: str # kod kursu
    course_name: str # nazwa kursu
    class_types: str # forma zajęć
    ects_value: int # punkty ECTS 
    grade: float # ocena