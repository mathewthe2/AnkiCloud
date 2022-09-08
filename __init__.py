# from unittest import TextTestRunner
import os
import json
from aqt import mw
from aqt.qt import *
from .icloud.pyicloud import PyiCloudService
from .icloud.anki_cloud import AnkiCloud
# from shutil import copyfileobj
from .icloud.sync_dialog import SyncDialog

user_file_json = os.path.join(os.path.dirname(__file__), 'user.json')

class MainDialog(QDialog):
    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        self.username, self.password = self.get_user()
        self.saved_username = self.username
        self.initUI()

    def initUI(self):
        vbox = QVBoxLayout()
        loginGroup = self.createLoginGroup()
        vbox.addWidget(loginGroup)
        self.setLayout(vbox)
        self.adjustSize()
        self.setWindowTitle('AnkiCloud')
        self.setModal(True)
        self.show()

    def changeUsername(self):
        self.username = self.usernameInput.text().strip()

    def changePassword(self):
        self.password = self.passwordInput.text().strip()

    def createLoginGroup(self):
        layout = QFormLayout()
        groupBox = QGroupBox("Login to iCloud:")

        self.usernameInput = QLineEdit()
        self.passwordInput = QLineEdit()
        self.passwordInput.setEchoMode(QLineEdit.Password)

        self.usernameInput.setText(self.username)
        self.passwordInput.setText(self.password)

        self.usernameInput.textChanged.connect(self.changeUsername)
        self.passwordInput.textChanged.connect(self.changePassword)

        loginButton = QPushButton("Login")
        loginButton.clicked.connect(self.login)

        layout.addRow(QLabel("Username"), self.usernameInput)
        layout.addRow(QLabel("Password"), self.passwordInput)
        layout.addRow(loginButton)
    
        groupBox.setLayout(layout)

        return groupBox

    def get_user(self):
        if os.path.exists(user_file_json):
            with open(user_file_json, 'r') as f:
                data = json.load(f)
            return data['username'], data['password']
        else:
            return '', ''

    def update_user(self):
        user = {
            'username': self.username,
            'password': self.password
        }
        with open(user_file_json, 'w') as f:
            json.dump(user, f, indent=4)

    def login(self):
        if (self.username != self.saved_username or self.password != self.saved_password):
            self.update_user()
        anki_cloud = AnkiCloud(self.username, self.password)
        tsv = anki_cloud.get_tsv_files()
        # QMessageBox.question(self, "result", ', '.join(tsv), QMessageBox.Yes | 
        # QMessageBox.No, QMessageBox.No)

        # QDialog.done(self, 1)
        syncDialog = SyncDialog(mw, anki_cloud)
        syncDialog.exec_()

def showApp():
    mainDialog = MainDialog(mw)
    mainDialog.exec_()


action = QAction("AnkiCloud", mw)
# action.setShortcut(QKeySequence("Ctrl+I"))

# set it to call testFunction when it's clicked
action.triggered.connect(showApp)

mw.form.menuTools.addAction(action)