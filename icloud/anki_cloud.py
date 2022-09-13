import os, sys
import json
from aqt.qt import *
from .pyicloud import PyiCloudService
from shutil import copyfileobj

ANKI_CLOUD_FOLDER = 'AnkiCloud'

class AnkiCloud():
    def __init__(self, username, password):
        self.api = PyiCloudService(username, password)
        self.is_logged_in = self.login()

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

    def get_tsv_files(self):
        if ANKI_CLOUD_FOLDER not in self.api.drive.dir():
            self.api.drive.mkdir(ANKI_CLOUD_FOLDER)
        tsv_files =  self.api.drive[ANKI_CLOUD_FOLDER].dir()
        return tsv_files

    def get_file_contents(self, file_name):
        drive_file = self.api.drive[ANKI_CLOUD_FOLDER][file_name]
        with drive_file.open(stream=True) as response:
            return response.content

# a = AnkiCloud()
# print(a.login())
# print(a.get_user())

        