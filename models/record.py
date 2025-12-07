class Record:
    def __init__(self, student_id, subject_code, grades=None, attendance_present=0, attendance_total=0):
        self.student_id = str(student_id)
        self.subject_code = subject_code
        self.grades = grades if grades is not None else []
        self.attendance_present = int(attendance_present)
        self.attendance_total = int(attendance_total)

    def add_grade(self, grade):
        self.grades.append(float(grade))

    def mark_attendance(self, present: bool):
        self.attendance_total += 1
        if present:
            self.attendance_present += 1

    def average(self):
        if not self.grades:
            return None
        return sum(self.grades)/len(self.grades)

    def attendance_percent(self):
        if self.attendance_total == 0:
            return None
        return (self.attendance_present / self.attendance_total) * 100

    def serialize(self):
        grades_str = ','.join(str(int(g)) if float(g).is_integer() else str(g) for g in self.grades)
        return f"{self.student_id} | {self.subject_code} | grades=[{grades_str}] | attendance={self.attendance_present}/{self.attendance_total}\n"

    @staticmethod
    def deserialize(line):
        parts = [p.strip() for p in line.split('|')]
        if len(parts) < 4:
            return None
        student_id = parts[0]
        subject_code = parts[1]
        # parse grades
        grades_part = parts[2]
        attendance_part = parts[3]
        grades = []
        if grades_part.startswith('grades='):
            inner = grades_part[len('grades='):].strip()
            inner = inner.strip('[]')
            if inner:
                grades = [float(x.strip()) for x in inner.split(',') if x.strip()]
        attendance_present = 0
        attendance_total = 0
        if attendance_part.startswith('attendance='):
            att = attendance_part[len('attendance='):].strip()
            if '/' in att:
                a,b = att.split('/',1)
                attendance_present = int(a)
                attendance_total = int(b)
        return Record(student_id, subject_code, grades, attendance_present, attendance_total)
