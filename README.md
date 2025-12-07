# STUDENT MANAGEMENT SYSTEM
This project is a simple Python OOP–based Student Management System. It manages students, subjects, enrollments, grades, attendance, and student reports using a text-based menu and text file storage.

## Data Folder Information
When the user runs:
`python main.py`
The program automatically creates a data/ folder (if it is empty). Inside this folder, four text files are generated:
`students.txt`
`subjects.txt`
`enrollments.txt`
`records.txt`

I have already added some sample data (some students and subjects). You can add more students and subjects using the menu options; the files update automatically.

## How to Run the System
Open terminal / command prompt
Go to the project directory
Run the following command:

```bash
python main.py
```

The Student Management System interface will appear.
## Menu Options
You will see the following options on the screen:
`Add Student`
`Add Subject`
`Enroll Student`
`Add Grade`
`Mark Attendance`
`View Student Report`
`View All Students`
`Exit`
Choose any number to perform that action.

## Features implemented
- Add students with unique IDs
- Add subjects with unique codes
- Enroll students in subjects (creates a record automatically)
- Add grades to student-subject records
- Mark attendance (tracks present/total per record)
- View student report with grades, averages, attendance, and an overall snapshot
- View list of all students
- Data persisted to plain text files in `data/` folder

## How data is stored (plain text files in `data/`)
- `students.txt`: `student_id | name | section`
- `subjects.txt`: `code | name | credit_hours`
- `enrollments.txt`: `student_id | subject_code`
- `records.txt`: `student_id | subject_code | grades=[85,90] | attendance=12/14`


## Summary of Classes Used
`Student`
- Attributes: student_id, name, section
- Methods: serialize(), deserialize()
Stores individual student information.

`Subject`
- Attributes: code, name, credit_hours
- Methods: serialize(), deserialize()
Stores subject information.

`Record`
- Attributes: student_id, subject_code, grades, attendance_present, attendance_total
- Methods:
add_grade(grade) – add grade to the record
mark_attendance(present) – update attendance
average() – calculate average grade
attendance_percent() – calculate attendance percentage
serialize() / deserialize() – for storing and loading from files
Stores grades and attendance for a student in a subject.

`SystemManager`
Handles core functionality: adding students/subjects, enrolling students, grading, marking attendance, generating reports, saving/loading data, and running the CLI menu.
Maintains in-memory dictionaries for fast access to students, subjects, enrollments, and records.

## Important Notes
-Students must exist before enrolling in subjects, marking attendance, or adding grades.

-Subjects must be added before enrolling students.
