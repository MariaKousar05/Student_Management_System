import os
from models.student import Student
from models.subject import Subject
from models.record import Record

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')

class SystemManager:
    def __init__(self):
        os.makedirs(DATA_DIR, exist_ok=True)
        self.students_file = os.path.join(DATA_DIR, 'students.txt')
        self.subjects_file = os.path.join(DATA_DIR, 'subjects.txt')
        self.enrollments_file = os.path.join(DATA_DIR, 'enrollments.txt')
        self.records_file = os.path.join(DATA_DIR, 'records.txt')

        # in-memory data
        self.students = {}   # student_id -> Student
        self.subjects = {}   # subject_code -> Subject
        self.enrollments = set()  # (student_id, subject_code)
        self.records = {}    # (student_id, subject_code) -> Record

        self.load_all()

    # ---------- Persistence ----------
    def load_all(self):
        self._load_students()
        self._load_subjects()
        self._load_enrollments()
        self._load_records()

    def _load_students(self):
        if not os.path.exists(self.students_file):
            open(self.students_file, 'w').close()
        with open(self.students_file, 'r') as f:
            for line in f:
                line = line.strip()
                if not line: continue
                s = Student.deserialize(line)
                if s:
                    self.students[s.student_id] = s

    def _load_subjects(self):
        if not os.path.exists(self.subjects_file):
            open(self.subjects_file, 'w').close()
        with open(self.subjects_file, 'r') as f:
            for line in f:
                line = line.strip()
                if not line: continue
                sub = Subject.deserialize(line)
                if sub:
                    self.subjects[sub.code] = sub

    def _load_enrollments(self):
        if not os.path.exists(self.enrollments_file):
            open(self.enrollments_file, 'w').close()
        with open(self.enrollments_file, 'r') as f:
            for line in f:
                line = line.strip()
                if not line: continue
                parts = [p.strip() for p in line.split('|')]
                if len(parts) >= 2:
                    sid = parts[0]
                    code = parts[1]
                    self.enrollments.add((sid, code))

    def _load_records(self):
        if not os.path.exists(self.records_file):
            open(self.records_file, 'w').close()
        with open(self.records_file, 'r') as f:
            for line in f:
                line = line.strip()
                if not line: continue
                rec = Record.deserialize(line)
                if rec:
                    key = (rec.student_id, rec.subject_code)
                    self.records[key] = rec

    def save_all(self):
        self._save_students()
        self._save_subjects()
        self._save_enrollments()
        self._save_records()

    def _save_students(self):
        with open(self.students_file, 'w') as f:
            for s in self.students.values():
                f.write(s.serialize())

    def _save_subjects(self):
        with open(self.subjects_file, 'w') as f:
            for s in self.subjects.values():
                f.write(s.serialize())

    def _save_enrollments(self):
        with open(self.enrollments_file, 'w') as f:
            for sid, code in sorted(self.enrollments):
                f.write(f"{sid} | {code}\n")

    def _save_records(self):
        with open(self.records_file, 'w') as f:
            for rec in self.records.values():
                f.write(rec.serialize())

    # ---------- Core features ----------
    def add_student(self, student_id, name, section):
        sid = str(student_id)
        if sid in self.students:
            raise ValueError('Student ID already exists')
        s = Student(sid, name, section)
        self.students[sid] = s
        self._save_students()

    def add_subject(self, code, name, credit_hours):
        code = code.upper()
        if code in self.subjects:
            raise ValueError('Subject code already exists')
        sub = Subject(code, name, credit_hours)
        self.subjects[code] = sub
        self._save_subjects()

    def enroll_student(self, student_id, subject_code):
        sid = str(student_id)
        code = subject_code.upper()
        if sid not in self.students:
            raise ValueError('No such student')
        if code not in self.subjects:
            raise ValueError('No such subject')
        key = (sid, code)
        if key in self.enrollments:
            raise ValueError('Student already enrolled in subject')
        self.enrollments.add(key)
        # create record
        if key not in self.records:
            self.records[key] = Record(sid, code)
        self._save_enrollments()
        self._save_records()

    def add_grade(self, student_id, subject_code, grade):
        sid = str(student_id)
        code = subject_code.upper()
        key = (sid, code)
        if key not in self.enrollments:
            raise ValueError('Student not enrolled in subject')
        rec = self.records.get(key)
        if not rec:
            rec = Record(sid, code)
            self.records[key] = rec
        rec.add_grade(float(grade))
        self._save_records()

    def mark_attendance(self, student_id, subject_code, present: bool):
        sid = str(student_id)
        code = subject_code.upper()
        key = (sid, code)
        if key not in self.enrollments:
            raise ValueError('Student not enrolled in subject')
        rec = self.records.get(key)
        if not rec:
            rec = Record(sid, code)
            self.records[key] = rec
        rec.mark_attendance(present)
        self._save_records()

    # ---------- Reports ----------
    def get_student_report_text(self, student_id):
        sid = str(student_id)
        if sid not in self.students:
            raise ValueError('No such student')
        s = self.students[sid]
        lines = []
        lines.append(f"Student ID: {s.student_id}")
        lines.append(f"Name: {s.name}")
        lines.append(f"Section: {s.section}")
        lines.append("\nEnrolled Subjects:")
        enrolled = [code for (st, code) in self.enrollments if st == sid]
        if not enrolled:
            lines.append('  (No subjects enrolled)')
        total_grades = []
        for code in sorted(enrolled):
            sub = self.subjects.get(code)
            rec = self.records.get((sid, code))
            lines.append(f"  - {code}: {sub.name if sub else 'UNKNOWN'} ({sub.credit_hours if sub else '?' } cr)")
            if rec:
                avg = rec.average()
                att = rec.attendance_percent()
                grades_str = ', '.join(str(int(g)) if float(g).is_integer() else str(g) for g in rec.grades) if rec.grades else '(no grades)'
                lines.append(f"      Grades: {grades_str}")
                lines.append(f"      Average: {round(avg,2) if avg is not None else 'N/A'}")
                lines.append(f"      Attendance: {rec.attendance_present}/{rec.attendance_total} -> {round(att,2) if att is not None else 'N/A'}%") 
                if avg is not None:
                    total_grades.append(avg)
            else:
                lines.append('      (no record)')
        # overall snapshot simple average
        overall = None
        if total_grades:
            overall = sum(total_grades)/len(total_grades)
        lines.append('\nOverall Performance Snapshot:')
        lines.append(f"  GPA-like average: {round(overall,2) if overall is not None else 'N/A'}")
        return '\n'.join(lines)

    def list_all_students_text(self):
        lines = []
        if not self.students:
            return '(no students)'
        for sid in sorted(self.students.keys()):
            s = self.students[sid]
            lines.append(f"{s.student_id} | {s.name} | {s.section}")
        return '\n'.join(lines)

    # ---------- CLI ----------
    def run_menu(self):
        while True:
            print('\n--- Student Management System ---')
            print('1. Add Student')
            print('2. Add Subject')
            print('3. Enroll Student')
            print('4. Add Grade')
            print('5. Mark Attendance')
            print('6. View Student Report')
            print('7. View All Students')
            print('8. Exit')
            choice = input('Choose an option: ').strip()
            try:
                if choice == '1':
                    self._cli_add_student()
                elif choice == '2':
                    self._cli_add_subject()
                elif choice == '3':
                    self._cli_enroll()
                elif choice == '4':
                    self._cli_add_grade()
                elif choice == '5':
                    self._cli_mark_attendance()
                elif choice == '6':
                    self._cli_view_report()
                elif choice == '7':
                    print(self.list_all_students_text())
                elif choice == '8':
                    print('Saving and exiting...')
                    self.save_all()
                    break
                else:
                    print('Invalid choice.')
            except Exception as e:
                print('Error:', e)

    # ---------- CLI helpers ----------
    def _cli_add_student(self):
        sid = input('Student ID: ').strip()
        name = input('Full name: ').strip()
        section = input('Section/Batch: ').strip()
        try:
            self.add_student(sid, name, section)
            print('Student added.')
        except Exception as e:
            print('Failed to add student:', e)

    def _cli_add_subject(self):
        code = input('Subject code (e.g. CS101): ').strip()
        name = input('Subject name: ').strip()
        ch = input('Credit hours (integer): ').strip()
        try:
            self.add_subject(code, name, int(ch))
            print('Subject added.')
        except Exception as e:
            print('Failed to add subject:', e)

    def _cli_enroll(self):
        sid = input('Student ID: ').strip()
        code = input('Subject code: ').strip()
        try:
            self.enroll_student(sid, code)
            print('Enrollment done.')
        except Exception as e:
            print('Failed to enroll:', e)

    def _cli_add_grade(self):
        sid = input('Student ID: ').strip()
        code = input('Subject code: ').strip()
        grade = input('Grade (number): ').strip()
        try:
            self.add_grade(sid, code, float(grade))
            print('Grade recorded.')
        except Exception as e:
            print('Failed to add grade:', e)

    def _cli_mark_attendance(self):
        sid = input('Student ID: ').strip()
        code = input('Subject code: ').strip()
        pres = input('Present? (y/n): ').strip().lower()
        present = pres in ('y','yes','1')
        try:
            self.mark_attendance(sid, code, present)
            print('Attendance recorded.')
        except Exception as e:
            print('Failed to mark attendance:', e)

    def _cli_view_report(self):
        sid = input('Student ID: ').strip()
        try:
            print('\n' + self.get_student_report_text(sid))
        except Exception as e:
            print('Failed to get report:', e)
