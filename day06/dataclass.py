
from dataclasses import dataclass

@dataclass
class Student:
    name: str
    score: int
    passed: bool = False

    def is_passed(self):
        return self.score >= 60

s = Student("Alice", 88)
print(s.is_passed())









