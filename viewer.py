import sys
import os.path
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from PySide6.QtCore import Slot
from PySide6.QtWidgets import (QApplication, QWidget, QHBoxLayout, QMenuBar,
                               QMainWindow, QMessageBox)
from ui_components.video import VideoPanel
from ui_components.menu_file_line import MenuFileAndLine
from ui_components.menu_view import MenuView
from configparser import ConfigParser


class ApplicationWindow(QMainWindow):

    def __init__(self, config_path):
        QMainWindow.__init__(self, None)

        line_dir = None
        SCOPES = ["https://www.googleapis.com/auth/drive"]
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json", SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json", SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open("token.json", "w") as token:
                token.write(creds.to_json())

        service = build("drive", "v3", credentials=creds)
        self.config = ConfigParser()
        self.config.read(config_path)
        self.config_path = config_path
        self.config_title = "google dirs"
        if self.config_title not in self.config.sections():
            self.config[self.config_title] = {}
            dirs_id = {}
            page_token = None
            while True:
                # Call the Drive v3 API
                response = (service.files().list(
                    q=
                    "mimeType='application/vnd.google-apps.folder' and name='Dati_Ricevitore_Digitale'",
                    spaces="drive",
                    fields="nextPageToken, files(id, name)",
                    pageToken=page_token,
                ).execute())
                for file in response.get("files", []):
                    # Process change
                    print(f'Found file: {file.get("name")}, {file.get("id")}')
                    dirs_id["ricevitore"] = file.get("id")
                page_token = response.get("nextPageToken", None)
                if page_token is None:
                    break
            while True:
                # Call the Drive v3 API
                response = (service.files().list(
                    q=
                    "mimeType='application/vnd.google-apps.folder' and name='Dati_Parabola'",
                    spaces="drive",
                    fields="nextPageToken, files(id, name)",
                    pageToken=page_token,
                ).execute())
                for file in response.get("files", []):
                    # Process change
                    print(f'Found file: {file.get("name")}, {file.get("id")}')
                    dirs_id["parabola"] = file.get("id")
                page_token = response.get("nextPageToken", None)
                if page_token is None:
                    break

            self.save_config(self.config_title, dirs_id)

        self.measure_title = "Data"
        if self.measure_title not in self.config.sections():
            self.config[self.measure_title] = {}
            self.save_config(self.measure_title, {"max_lenght": "150"})

        # Central widget
        self._main = QWidget()
        self.setCentralWidget(self._main)

        # Main layout
        layout = QHBoxLayout(self._main)
        self.video_panel = VideoPanel(
            self.config[self.config_title], service,
            self.config[self.measure_title].getint("max_lenght"))
        layout.addLayout(self.video_panel)

        # Main menu bar
        self.top_menu = QMenuBar(self)
        self.setMenuBar(self.top_menu)
        self.menu_file = MenuFileAndLine(self, service,
                                         self.config[self.config_title])
        self.top_menu.addMenu(self.menu_file)
        self.menu_view = MenuView(self)
        self.top_menu.addMenu(self.menu_view)

        # Signals
        self.menu_file.open_success.connect(self.video_panel.open_video)
        self.menu_file.line_signal.connect(self.video_panel.line_control)
        self.menu_view.color_map_menu.color_chosen.connect(
            self.video_panel.set_color_map)

    def save_config(self, category, configs):
        try:
            for name in configs.keys():
                self.config[category][name] = configs[name]
            with open(self.config_path, 'w') as f:
                self.config.write(f)
        except PermissionError:
            pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    Path("config/").mkdir(parents=True,
                          exist_ok=True)  # Just to assure it exists
    Path("files/").mkdir(parents=True,
                         exist_ok=True)  # Just to assure it exists
    w = ApplicationWindow('config/config.ini')
    w.setFixedSize(1280, 720)
    w.show()
    app.exec()
