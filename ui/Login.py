from PyQt5 import QtCore, QtWidgets, QtGui
from ui.Register import RegistrationDialog
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

        register_link = QtWidgets.QLabel('<a href="#" style="color:white" >Register as new user</a>')
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
