class Student:
    def __init__(self, student_id, name, section):
        self.student_id = str(student_id)
        self.name = name
        self.section = section

    def serialize(self):
        return f"{self.student_id} | {self.name} | {self.section}\n"

    @staticmethod
    def deserialize(line):
        parts = [p.strip() for p in line.split('|')]
        if len(parts) < 3:
            return None
        return Student(parts[0], parts[1], parts[2])
