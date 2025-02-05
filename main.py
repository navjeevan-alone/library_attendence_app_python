import sys
import csv
from PyQt5 import QtCore, QtWidgets, QtGui
from database_handler import DatabaseHandler
from datetime import datetime

# Login Dialog
class LoginDialog(QtWidgets.QDialog):
    def __init__(self, db_handler, parent=None):
        super().__init__(parent)
        self.db_handler = db_handler
        self.current_user = None
        self.setup_ui()
        self.setWindowTitle("Login")

    def setup_ui(self):
        layout = QtWidgets.QVBoxLayout()
        form_layout = QtWidgets.QFormLayout()

        self.phone_edit = QtWidgets.QLineEdit()
        self.phone_edit.setPlaceholderText("Phone")
        self.password_edit = QtWidgets.QLineEdit()
        self.password_edit.setPlaceholderText("Password")
        self.password_edit.setEchoMode(QtWidgets.QLineEdit.Password)

        form_layout.addRow("Phone:", self.phone_edit)
        form_layout.addRow("Password:", self.password_edit)
        layout.addLayout(form_layout)

        self.login_btn = QtWidgets.QPushButton("Login")
        self.login_btn.clicked.connect(self.login)
        layout.addWidget(self.login_btn)

        register_link = QtWidgets.QLabel('<a href="#">Register as new user</a>')
        register_link.setAlignment(QtCore.Qt.AlignCenter)
        register_link.setOpenExternalLinks(False)
        register_link.linkActivated.connect(self.open_registration)
        layout.addWidget(register_link)

        self.setLayout(layout)

    def login(self):
        phone = self.phone_edit.text().strip()
        password = self.password_edit.text().strip()
        user = self.db_handler.get_user(phone, password)
        if user:
            self.current_user = user
            self.accept()
        else:
            QtWidgets.QMessageBox.warning(self, "Login Failed", "Invalid phone or password.")

    def open_registration(self):
        reg_dialog = RegistrationDialog(self.db_handler, parent=self)
        if reg_dialog.exec_() == QtWidgets.QDialog.Accepted:
            QtWidgets.QMessageBox.information(self, "Registration", "Registration successful. You can now log in.")

# Registration Dialog for Users
class RegistrationDialog(QtWidgets.QDialog):
    def __init__(self, db_handler, parent=None):
        super().__init__(parent)
        self.db_handler = db_handler
        self.setup_ui()
        self.setWindowTitle("User Registration")

    def setup_ui(self):
        layout = QtWidgets.QVBoxLayout()
        form_layout = QtWidgets.QFormLayout()

        self.name_edit = QtWidgets.QLineEdit()
        self.phone_edit = QtWidgets.QLineEdit()
        self.org_combo = QtWidgets.QComboBox()
        self.org_combo.setEditable(True)
        self.password_edit = QtWidgets.QLineEdit()
        self.password_edit.setEchoMode(QtWidgets.QLineEdit.Password)
        self.admin_checkbox = QtWidgets.QCheckBox("Register as Admin")

        # Populate organization combo with existing organizations
        self.org_combo.addItem("Create New Organization")
        orgs = self.db_handler.get_all_organizations()
        for org in orgs:
            # org: (organization_id, name)
            self.org_combo.addItem(org[1], org[0])

        form_layout.addRow("Name:", self.name_edit)
        form_layout.addRow("Phone:", self.phone_edit)
        form_layout.addRow("Organization:", self.org_combo)
        form_layout.addRow("Password:", self.password_edit)
        form_layout.addRow("", self.admin_checkbox)
        layout.addLayout(form_layout)

        btn_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        btn_box.accepted.connect(self.register)
        btn_box.rejected.connect(self.reject)
        layout.addWidget(btn_box)

        self.setLayout(layout)

    def register(self):
        name = self.name_edit.text().strip()
        phone = self.phone_edit.text().strip()
        password = self.password_edit.text().strip()
        is_admin = 1 if self.admin_checkbox.isChecked() else 0

        if not (name and phone and password):
            QtWidgets.QMessageBox.warning(self, "Input Error", "Please fill in all required fields.")
            return

        org_index = self.org_combo.currentIndex()
        if org_index == 0:
            # Create new organization
            org_name, ok = QtWidgets.QInputDialog.getText(self, "New Organization", "Enter Organization Name:")
            if ok and org_name.strip():
                org = self.db_handler.add_organization(org_name.strip())
                organization_id = org[0]
            else:
                QtWidgets.QMessageBox.warning(self, "Input Error", "Organization name is required.")
                return
        else:
            organization_id = self.org_combo.itemData(org_index)

        user_id = self.db_handler.add_user(name, phone, organization_id, password, is_admin)
        if user_id is None:
            QtWidgets.QMessageBox.warning(self, "Registration Error", "Maximum number of admins reached for this organization.")
            return

        QtWidgets.QMessageBox.information(self, "Registration", "User registered successfully.")
        self.accept()

# Registration Dialog for Students (when not registered in Students table)
class StudentRegistrationDialog(QtWidgets.QDialog):
    def __init__(self, student_id, db_handler, organization_id, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Register Student")
        self.db_handler = db_handler
        self.student_id = student_id
        self.organization_id = organization_id
        self.setup_ui()

    def setup_ui(self):
        layout = QtWidgets.QVBoxLayout()
        id_layout = QtWidgets.QHBoxLayout()
        id_label = QtWidgets.QLabel("Student ID:")
        self.id_edit = QtWidgets.QLineEdit(self.student_id)
        self.id_edit.setReadOnly(True)
        id_layout.addWidget(id_label)
        id_layout.addWidget(self.id_edit)
        layout.addLayout(id_layout)

        name_layout = QtWidgets.QHBoxLayout()
        name_label = QtWidgets.QLabel("Student Name:")
        self.name_edit = QtWidgets.QLineEdit()
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_edit)
        layout.addLayout(name_layout)

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
        self.db_handler.add_student(self.student_id, name, self.organization_id)
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
    def __init__(self, current_user, db_handler):
        super().__init__()
        self.current_user = current_user  # tuple representing the logged in user
        self.db = db_handler
        self.organization_id = current_user[3]  # organization_id from Users table
        self.setWindowTitle("Attendance App")
        self.setGeometry(100, 100, 900, 600)
        self.setup_ui()
        self.refresh_table()

    def setup_ui(self):
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QtWidgets.QVBoxLayout()

        form_layout = QtWidgets.QHBoxLayout()
        self.id_input = QtWidgets.QLineEdit()
        self.id_input.setPlaceholderText("Enter Student ID")
        form_layout.addWidget(self.id_input)

        self.mark_btn = QtWidgets.QPushButton("Mark Attendance")
        self.mark_btn.clicked.connect(self.handle_mark_attendance)
        form_layout.addWidget(self.mark_btn)

        self.import_btn = QtWidgets.QPushButton("Import Students")
        self.import_btn.clicked.connect(self.import_students)
        form_layout.addWidget(self.import_btn)

        main_layout.addLayout(form_layout)

        # Attendance Table
        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Attendance ID", "Student ID", "Name", "Date", "In Time", "Out Time"])
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        header = self.table.horizontalHeader()
        header.setStretchLastSection(True)
        main_layout.addWidget(self.table)

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

        student = self.db.get_student(student_id, self.organization_id)
        if student is None:
            msg_box = QtWidgets.QMessageBox(self)
            msg_box.setIcon(QtWidgets.QMessageBox.Warning)
            msg_box.setText("Student not registered.")
            reg_btn = msg_box.addButton("Register", QtWidgets.QMessageBox.AcceptRole)
            msg_box.addButton("Cancel", QtWidgets.QMessageBox.RejectRole)
            msg_box.exec_()
            if msg_box.clickedButton() == reg_btn:
                reg_dialog = StudentRegistrationDialog(student_id, self.db, self.organization_id, self)
                if reg_dialog.exec_() == QtWidgets.QDialog.Accepted:
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
                self.db.import_students(path, self.organization_id)
                QtWidgets.QMessageBox.information(self, "Import", "Students imported successfully.")
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Import Error", f"An error occurred: {e}")

    def refresh_table(self, start_date=None, end_date=None):
        records = self.db.get_all_attendance(self.organization_id, start_date, end_date)
        self.table.setRowCount(len(records))
        for row_idx, row_data in enumerate(records):
            for col_idx, item in enumerate(row_data):
                cell = QtWidgets.QTableWidgetItem(str(item) if item is not None else "")
                self.table.setItem(row_idx, col_idx, cell)

    def export_csv(self):
        export_dialog = ExportDialog(self)
        if export_dialog.exec_() == QtWidgets.QDialog.Accepted:
            start_date, end_date = export_dialog.get_date_range()
            records = self.db.get_all_attendance(self.organization_id, start_date, end_date)
            if not records:
                QtWidgets.QMessageBox.information(self, "Export", "No records found in the selected date range.")
                return
            path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save CSV", "", "CSV Files (*.csv)")
            if path:
                try:
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
    # Load QSS styling
    try:
        with open("style.qss", "r") as f:
            app.setStyleSheet(f.read())
    except Exception:
        pass

    db_handler = DatabaseHandler()

    login_dialog = LoginDialog(db_handler)
    if login_dialog.exec_() == QtWidgets.QDialog.Accepted:
        current_user = login_dialog.current_user
        main_window = AttendanceApp(current_user, db_handler)
        main_window.show()
        sys.exit(app.exec_())
