import sqlite3
import csv
from datetime import datetime, date

class DatabaseHandler:
    def __init__(self, db_name="attendance.db"):
        self.conn = sqlite3.connect(db_name)
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Students (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Attendance (
                attendance_id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT NOT NULL,
                date TEXT NOT NULL,
                in_time TEXT,
                out_time TEXT,
                FOREIGN KEY (student_id) REFERENCES Students(id)
            )
        ''')
        self.conn.commit()

    def get_student(self, student_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM Students WHERE id = ?", (student_id,))
        return cursor.fetchone()

    def add_student(self, student_id, name):
        cursor = self.conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO Students (id, name) VALUES (?, ?)", (student_id, name))
        self.conn.commit()

    def import_students(self, file_path):
        with open(file_path, newline='') as csvfile:
            reader = csv.reader(csvfile)
            # Expect header row: ID,Name
            next(reader, None)
            for row in reader:
                if len(row) >= 2:
                    student_id, name = row[0].strip(), row[1].strip()
                    self.add_student(student_id, name)

    def mark_attendance(self, student_id):
        today = date.today().isoformat()
        now = datetime.now().strftime("%H:%M:%S")
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT attendance_id, in_time, out_time FROM Attendance WHERE student_id = ? AND date = ?",
            (student_id, today)
        )
        record = cursor.fetchone()
        if record is None:
            cursor.execute(
                "INSERT INTO Attendance (student_id, date, in_time) VALUES (?, ?, ?)",
                (student_id, today, now)
            )
        else:
            attendance_id, in_time, out_time = record
            if out_time is None:
                cursor.execute(
                    "UPDATE Attendance SET out_time = ? WHERE attendance_id = ?",
                    (now, attendance_id)
                )
            else:
                # If out_time already set, create a new record for the same day if needed.
                cursor.execute(
                    "INSERT INTO Attendance (student_id, date, in_time) VALUES (?, ?, ?)",
                    (student_id, today, now)
                )
        self.conn.commit()

    def get_all_attendance(self, start_date=None, end_date=None):
        cursor = self.conn.cursor()
        query = '''
            SELECT a.attendance_id, s.id, s.name, a.date, a.in_time, a.out_time
            FROM Attendance a
            JOIN Students s ON a.student_id = s.id
        '''
        conditions = []
        params = []
        if start_date:
            conditions.append("a.date >= ?")
            params.append(start_date)
        if end_date:
            conditions.append("a.date <= ?")
            params.append(end_date)
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        query += " ORDER BY a.date ASC, a.in_time ASC"
        cursor.execute(query, params)
        return cursor.fetchall()
