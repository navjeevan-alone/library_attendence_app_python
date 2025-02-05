import sys
from PyQt5 import QtCore, QtWidgets
from database_handler import DatabaseHandler
from datetime import datetime

# Registration Dialog for unregistered students
class RegistrationDialog(QtWidgets.QDialog):
    def __init__(self, student_id, db_handler, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Register Student")
        self.db_handler = db_handler
        self.student_id = student_id
        self.setup_ui()

    def setup_ui(self):
        layout = QtWidgets.QVBoxLayout()

        # Student ID (read-only)
        id_layout = QtWidgets.QHBoxLayout()
        id_label = QtWidgets.QLabel("Student ID:")
        self.id_edit = QtWidgets.QLineEdit(self.student_id)
        self.id_edit.setReadOnly(True)
        id_layout.addWidget(id_label)
        id_layout.addWidget(self.id_edit)
        layout.addLayout(id_layout)

        # Student Name
        name_layout = QtWidgets.QHBoxLayout()
        name_label = QtWidgets.QLabel("Student Name:")
        self.name_edit = QtWidgets.QLineEdit()
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_edit)
        layout.addLayout(name_layout)

        # Buttons
        btn_layout = QtWidgets.QHBoxLayout()
        register_btn = QtWidgets.QPushButton("Register")
        register_btn.clicked.connect(self.register)
        cancel_btn = QtWidgets.QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(register_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def register(self):
        name = self.name_edit.text().strip()
        if not name:
            QtWidgets.QMessageBox.warning(self, "Input Error", "Please enter a name.")
            return
        self.db_handler.add_student(self.student_id, name)
        QtWidgets.QMessageBox.information(self, "Registration", "Student registered successfully.")
        self.accept()

# Dialog to select date range for exporting attendance
class ExportDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Date Range")
        self.setup_ui()

    def setup_ui(self):
        layout = QtWidgets.QFormLayout()

        self.start_date = QtWidgets.QDateEdit(calendarPopup=True)
        self.start_date.setDisplayFormat("yyyy-MM-dd")
        self.start_date.setDate(QtCore.QDate.currentDate())
        self.end_date = QtWidgets.QDateEdit(calendarPopup=True)
        self.end_date.setDisplayFormat("yyyy-MM-dd")
        self.end_date.setDate(QtCore.QDate.currentDate())

        layout.addRow("Start Date:", self.start_date)
        layout.addRow("End Date:", self.end_date)

        btn_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        btn_box.accepted.connect(self.accept)
        btn_box.rejected.connect(self.reject)
        layout.addWidget(btn_box)

        self.setLayout(layout)

    def get_date_range(self):
        return (self.start_date.date().toString("yyyy-MM-dd"), self.end_date.date().toString("yyyy-MM-dd"))

# Main Application Window
class AttendanceApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = DatabaseHandler()
        self.setWindowTitle("Attendance App")
        self.setGeometry(100, 100, 900, 600)
        self.setup_ui()
        self.refresh_table()

    def setup_ui(self):
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QtWidgets.QVBoxLayout()

        # Top form: Student ID input and Mark Attendance button
        form_layout = QtWidgets.QHBoxLayout()
        self.id_input = QtWidgets.QLineEdit()
        self.id_input.setPlaceholderText("Enter Student ID")
        form_layout.addWidget(self.id_input)

        self.mark_btn = QtWidgets.QPushButton("Mark Attendance")
        self.mark_btn.clicked.connect(self.handle_mark_attendance)
        form_layout.addWidget(self.mark_btn)

        # Import Students Button
        self.import_btn = QtWidgets.QPushButton("Import Students")
        self.import_btn.clicked.connect(self.import_students)
        form_layout.addWidget(self.import_btn)

        main_layout.addLayout(form_layout)

        # Attendance Table
        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Attendance ID", "Student ID", "Name", "Date", "In Time", "Out Time"])
        self.table.horizontalHeader()
        main_layout.addWidget(self.table)

        # Export Button
        btn_layout = QtWidgets.QHBoxLayout()
        self.export_btn = QtWidgets.QPushButton("Export CSV")
        self.export_btn.clicked.connect(self.export_csv)
        btn_layout.addWidget(self.export_btn)
        main_layout.addLayout(btn_layout)

        central_widget.setLayout(main_layout)

    def handle_mark_attendance(self):
        student_id = self.id_input.text().strip()
        if not student_id:
            QtWidgets.QMessageBox.warning(self, "Input Error", "Student ID cannot be empty.")
            return

        # Check if student exists
        student = self.db.get_student(student_id)
        if student is None:
            msg_box = QtWidgets.QMessageBox(self)
            msg_box.setIcon(QtWidgets.QMessageBox.Warning)
            msg_box.setText("Student not registered.")
            register_btn = msg_box.addButton("Register", QtWidgets.QMessageBox.AcceptRole)
            msg_box.addButton("Cancel", QtWidgets.QMessageBox.RejectRole)
            msg_box.exec_()
            if msg_box.clickedButton() == register_btn:
                reg_dialog = RegistrationDialog(student_id, self.db, self)
                if reg_dialog.exec_() == QtWidgets.QDialog.Accepted:
                    # After registration, proceed to mark attendance
                    self.db.mark_attendance(student_id)
            else:
                return
        else:
            self.db.mark_attendance(student_id)

        self.refresh_table()
        self.id_input.clear()

    def import_students(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Import Students CSV", "", "CSV Files (*.csv)")
        if path:
            try:
                self.db.import_students(path)
                QtWidgets.QMessageBox.information(self, "Import", "Students imported successfully.")
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Import Error", f"An error occurred: {e}")

    def refresh_table(self, start_date=None, end_date=None):
        records = self.db.get_all_attendance(start_date, end_date)
        self.table.setRowCount(len(records))
        for row_idx, row_data in enumerate(records):
            for col_idx, item in enumerate(row_data):
                cell = QtWidgets.QTableWidgetItem(str(item) if item is not None else "")
                self.table.setItem(row_idx, col_idx, cell)

    def export_csv(self):
        # Open export dialog for date range selection
        export_dialog = ExportDialog(self)
        if export_dialog.exec_() == QtWidgets.QDialog.Accepted:
            start_date, end_date = export_dialog.get_date_range()
            records = self.db.get_all_attendance(start_date, end_date)
            if not records:
                QtWidgets.QMessageBox.information(self, "Export", "No records found in the selected date range.")
                return
            path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save CSV", "", "CSV Files (*.csv)")
            if path:
                try:
                    import csv
                    with open(path, mode="w", newline="") as file:
                        writer = csv.writer(file)
                        writer.writerow(["Attendance ID", "Student ID", "Name", "Date", "In Time", "Out Time"])
                        for record in records:
                            writer.writerow(record)
                    QtWidgets.QMessageBox.information(self, "Export", "Data exported successfully.")
                except Exception as e:
                    QtWidgets.QMessageBox.critical(self, "Export Error", f"An error occurred: {e}")

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = AttendanceApp()
    window.show()
    sys.exit(app.exec_())
