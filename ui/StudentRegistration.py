from PyQt5 import QtCore, QtWidgets, QtGui
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
