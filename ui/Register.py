from PyQt5 import QtCore, QtWidgets, QtGui
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
