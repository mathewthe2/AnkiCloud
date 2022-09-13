import os, sys
import json
from aqt.qt import *
from .anki_sync import AnkiSync
from .pyicloud import PyiCloudService
from shutil import copyfileobj
import sqlite3

download_location = os.path.join(os.path.dirname(__file__), '..')

ANKI_CLOUD_FOLDER = 'AnkiCloud'
DB_FILE = 'data.db'

class AnkiCloud():
    def __init__(self, username, password):
        self.api = PyiCloudService(username, password)
        self.is_logged_in = self.login()
        self.con = None
        self.anki_sync = AnkiSync()

    def login(self):
        if self.api.requires_2fa:
            # print("Two-factor authentication required.")
            # code = input("Enter the code you received of one of your approved devices: ")
            code, pressed = QInputDialog.getText(None,"Two-factor authentication required.","Enter the code you received of one of your approved devices:",QLineEdit.Normal,"")
            if pressed:
                result = self.api.validate_2fa_code(code)
                print("Code validation result: %s" % result)

                if not result:
                    print("Failed to verify security code")
                    return False

                if not self.api.is_trusted_session:
                    print("Session is not trusted. Requesting trust...")
                    result = self.api.trust_session()
                    print("Session trust result %s" % result)

                    if not result:
                        print("Failed to request trust. You will likely be prompted for the code again in the coming weeks")
        elif self.api.requires_2sa:
            # TODO: use dialog UI
            import click
            print("Two-step authentication required. Your trusted devices are:")

            devices = self.api.trusted_devices
            for i, device in enumerate(devices):
                print(
                    "  %s: %s" % (i, device.get('deviceName',
                    "SMS to %s" % device.get('phoneNumber')))
                )

            device = click.prompt('Which device would you like to use?', default=0)
            device = devices[device]
            if not self.api.send_verification_code(device):
                print("Failed to send verification code")
                return False

            code = click.prompt('Please enter validation code')
            if not self.api.validate_verification_code(device, code):
                print("Failed to verify verification code")
                return False

        return True

    def get_folders(self):             
        return ''.join(self.api.drive.dir())

    def get_files(self):
        if ANKI_CLOUD_FOLDER not in self.api.drive.dir():
            self.api.drive.mkdir(ANKI_CLOUD_FOLDER)
        tsv_files =  self.api.drive[ANKI_CLOUD_FOLDER].dir()
        return tsv_files

    def get_file_contents(self, file_name):
        drive_file = self.api.drive[ANKI_CLOUD_FOLDER][file_name]
        with drive_file.open(stream=True) as response:
            return response.content

    def has_data(self):
        return DB_FILE in self.api.drive[ANKI_CLOUD_FOLDER].dir()

    def download_data(self, file):
        download = self.api.drive[ANKI_CLOUD_FOLDER][file].open(stream=True)
        with open(os.path.join(download_location, file), 'wb') as opened_file:  
            opened_file.write(download.raw.read()) 

    def get_data(self):
        self.download_data(DB_FILE)
        con = sqlite3.connect(os.path.join(download_location, DB_FILE))
        cur = con.cursor()
        result = ''
        for row in cur.execute("SELECT deckName, fields, tags FROM note ORDER BY updated"):
            result += str(row)
        return result

    def sync_data(self):
        self.download_data(DB_FILE)
        if self.con:
            self.con.close()
        self.con = sqlite3.connect(os.path.join(download_location, DB_FILE))

    def add_new_notes(self):
        if not self.con:
            return
        cur = self.con.cursor()
        notes_added = []
        for row in cur.execute("SELECT deckName, modelName, fields, tags FROM note WHERE added=0 ORDER BY updated"):
            deckName, modelName, raw_fields, raw_tags = row
            fields = json.loads(raw_fields)
            tags = json.loads(raw_tags)
            note_id = self.anki_sync.addNote({
                'deckName': deckName,
                'modelName': modelName,
                'fields': fields,
                'tags': tags
            })
            notes_added.append(note_id)
        return notes_added

    def window(self):
        return aqt.mw

    def collection(self):
        collection = self.window().col
        if collection is None:
            raise Exception('collection is not available')

        return collection


    def count_new_notes(self):
        if not self.con:
            return 0
        cur = self.con.cursor()
        res = cur.execute("SELECT COUNT(*) FROM note WHERE added=0")
        result = res.fetchone()
        if result:
            return result[0]

    


    

# a = AnkiCloud()
# print(a.login())
# print(a.get_user())

        