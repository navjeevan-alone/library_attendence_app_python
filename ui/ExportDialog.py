from PyQt5 import QtCore, QtWidgets, QtGui
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
