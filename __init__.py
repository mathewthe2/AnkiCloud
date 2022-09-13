# from unittest import TextTestRunner
import os
import json
from aqt import mw
from aqt.qt import *
from .icloud.anki_cloud import AnkiCloud

user_file_json = os.path.join(os.path.dirname(__file__), 'user.json')

ANKI_CLOUD_LAYOUTS = {
    "LOGIN": 0,
    "SYNC": 1,
    "CHOOSE_DB_FILE": 2,
    "SUCCESS": 3,
}

class MainDialog(QDialog):
    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        self.username, self.password = self.get_user()
        self.saved_username = self.username
        self.anki_cloud = None
        self.has_data = False
        self.icloud_group = QGroupBox("iCloud:")
        self.success_message = QLabel("Sync complete!")
        self.initUI()


    def initUI(self):
        self.stacklayout = QStackedLayout()
        loginGroup = self.createLoginGroup()
        self.stacklayout.addWidget(loginGroup)
        self.stacklayout.addWidget(QLabel("Syncing..."))
        self.stacklayout.addWidget(self.icloud_group)
        self.stacklayout.addWidget(self.success_message)
        self.setLayout(self.stacklayout)
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

    def transition(self, phase):
        if phase == 'CHOOSE_DB_FILE':
            self._replace_widget(ANKI_CLOUD_LAYOUTS[phase], self.icloud_group, self.createiCloudGroup)
        elif phase == "SUCCESS":
            self._replace_widget(ANKI_CLOUD_LAYOUTS[phase], self.success_message, self.createSuccessMessage)
        self.stacklayout.setCurrentIndex(ANKI_CLOUD_LAYOUTS[phase])

    def _replace_widget(self, layout_index, widget, new_widget_func):
         self.stacklayout.removeWidget(widget)
         widget = new_widget_func()
         self.stacklayout.insertWidget(layout_index, widget)

    def login(self):
        if (self.username != self.saved_username):
            self.update_user()
        self.anki_cloud = AnkiCloud(self.username, self.password)
        if self.anki_cloud.is_logged_in:
            self.has_data = self.anki_cloud.has_data()
            if self.has_data:
                self.transition("SYNC")
                success = self.sync()
                if success:
                    self.transition("SUCCESS")
            else:
                self.transition("CHOOSE_DB_FILE")
            self.show()

    def sync(self):
        self.anki_cloud.sync_data()
        return True
    
    def showContents(self, file_name):
        contents_bytes = self.anki_cloud.get_file_contents(file_name)
        contents = str(contents_bytes)
        QMessageBox.question(self, "contents", contents, QMessageBox.Yes | 
        QMessageBox.No, QMessageBox.No)

    def createiCloudGroup(self):
        groupBox = QGroupBox("iCloud:")
        layout = QFormLayout()
        files = self.anki_cloud.get_files()
        for file_name in files:
            button = QPushButton(file_name)
            button.clicked.connect(lambda: self.showContents(file_name))
            layout.addRow(button)

        groupBox.setLayout(layout)
        return groupBox

    def createSuccessMessage(self):
        new_notes = self.anki_cloud.add_new_notes()
        return QLabel("Added {} new notes".format(new_notes))
            
def showApp():
    mainDialog = MainDialog(mw)
    mainDialog.exec_()


action = QAction("AnkiCloud", mw)
# action.setShortcut(QKeySequence("Ctrl+I"))

# set it to call testFunction when it's clicked
action.triggered.connect(showApp)

mw.form.menuTools.addAction(action)