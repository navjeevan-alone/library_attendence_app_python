import sqlite3
import csv
from datetime import datetime, date

class DatabaseHandler:
    def __init__(self, db_name="attendance.db"):
        self.conn = sqlite3.connect(db_name)
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()
        # Organizations Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Organizations (
                organization_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL
            )
        ''')
        # Users Table: multiple admins per organization allowed (max 5 enforced in app logic)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT,
                organization_id INTEGER NOT NULL,
                password TEXT NOT NULL,
                is_admin INTEGER DEFAULT 0,
                FOREIGN KEY (organization_id) REFERENCES Organizations(organization_id)
            )
        ''')
        # Students Table: each student belongs to an organization
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Students (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                organization_id INTEGER NOT NULL,
                FOREIGN KEY (organization_id) REFERENCES Organizations(organization_id)
            )
        ''')
        # Attendance Table: each record links to a student (and thus indirectly to organization)
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

    # Organization operations
    def get_organization_by_name(self, name):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM Organizations WHERE name = ?", (name,))
        return cursor.fetchone()

    def add_organization(self, name):
        cursor = self.conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO Organizations (name) VALUES (?)", (name,))
        self.conn.commit()
        return self.get_organization_by_name(name)

    def get_all_organizations(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM Organizations")
        return cursor.fetchall()

    # User operations
    def add_user(self, name, phone, organization_id, password, is_admin=0):
        # Check current admin count if registering as admin
        if is_admin:
            cursor = self.conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM Users WHERE organization_id = ? AND is_admin = 1", (organization_id,))
            count = cursor.fetchone()[0]
            if count >= 5:
                return None  # Exceeded allowed admins
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO Users (name, phone, organization_id, password, is_admin)
            VALUES (?, ?, ?, ?, ?)
        """, (name, phone, organization_id, password, is_admin))
        self.conn.commit()
        return cursor.lastrowid

    def get_user(self, phone, password):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM Users WHERE phone = ? AND password = ?", (phone, password))
        return cursor.fetchone()

    # Student operations
    def get_student(self, student_id, organization_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM Students WHERE id = ? AND organization_id = ?", (student_id, organization_id))
        return cursor.fetchone()

    def add_student(self, student_id, name, organization_id):
        cursor = self.conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO Students (id, name, organization_id) VALUES (?, ?, ?)",
                       (student_id, name, organization_id))
        self.conn.commit()

    def import_students(self, file_path, organization_id):
        with open(file_path, newline='') as csvfile:
            reader = csv.reader(csvfile)
            # Expect header row: ID,Name
            next(reader, None)
            for row in reader:
                if len(row) >= 2:
                    sid, name = row[0].strip(), row[1].strip()
                    self.add_student(sid, name, organization_id)

    # Attendance operations
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
                cursor.execute(
                    "INSERT INTO Attendance (student_id, date, in_time) VALUES (?, ?, ?)",
                    (student_id, today, now)
                )
        self.conn.commit()

    def get_all_attendance(self, organization_id, start_date=None, end_date=None):
        cursor = self.conn.cursor()
        query = '''
            SELECT a.attendance_id, s.id, s.name, a.date, a.in_time, a.out_time
            FROM Attendance a
            JOIN Students s ON a.student_id = s.id
            WHERE s.organization_id = ?
        '''
        params = [organization_id]
        if start_date:
            query += " AND a.date >= ?"
            params.append(start_date)
        if end_date:
            query += " AND a.date <= ?"
            params.append(end_date)
        query += " ORDER BY a.date ASC, a.in_time ASC"
        cursor.execute(query, params)
        return cursor.fetchall()
