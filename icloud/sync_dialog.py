from aqt.qt import *

class SyncDialog(QDialog):
    def __init__(self, parent=None, anki_cloud=None):
        QDialog.__init__(self, parent)
        self.anki_cloud= anki_cloud
        self.initUI()

    def initUI(self):
        vbox = QVBoxLayout()
        loginGroup = self.createiCloudGroup()
        vbox.addWidget(loginGroup)
        self.setLayout(vbox)
        self.adjustSize()
        self.setWindowTitle('AnkiCloud Data')
        self.setModal(True)
        self.show()

    def showContents(self, file_name):
        contents_bytes = self.anki_cloud.get_file_contents(file_name)
        contents = str(contents_bytes)
        QMessageBox.question(self, "contents", contents, QMessageBox.Yes | 
        QMessageBox.No, QMessageBox.No)

    def createiCloudGroup(self):
        layout = QFormLayout()
        groupBox = QGroupBox("iCloud:")

        files = self.anki_cloud.get_tsv_files()
        for file_name in files:
            button = QPushButton(file_name)
            button.clicked.connect(lambda: self.showContents(file_name))
            layout.addRow(button)

        # layout.addRow(QLabel("file"), QLabel('tsv file here'))
    
        groupBox.setLayout(layout)

        return groupBox


