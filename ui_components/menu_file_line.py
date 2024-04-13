from PySide6.QtGui import QAction
from os.path import expanduser
from os import walk
from PySide6.QtCore import Slot, Signal
from PySide6.QtWidgets import (QLabel, QHBoxLayout, QVBoxLayout, QLineEdit,
                               QMenu, QMessageBox, QPushButton, QDialog,
                               QComboBox)
import os.path


class MenuFileAndLine(QMenu):

    line_signal = Signal(str)
    open_success = Signal(str, dict, float, float)

    def __init__(self, parent, creds, ids):
        QMenu.__init__(self, title="&File", parent=parent)

        self.creds = creds
        self.ids = ids
        open_action = QAction("Open",
                              parent,
                              triggered=self.open_experiment_dialog)
        open_action.setShortcut("Ctrl+o")
        self.addAction(open_action)

        create_line_action = LineAction(self, self.line_signal, "Create")
        create_line_action.setShortcut("Ctrl+l")
        self.addAction(create_line_action)
        save_line_action = LineAction(self, self.line_signal, "Save")
        save_line_action.setShortcut("Ctrl+s")
        self.addAction(save_line_action)

    def open_experiment_dialog(self):
        dialog = ChooseExperimentDialog(self, self.creds, self.ids["parabola"])
        if dialog.exec():
            self.open_success.emit(*dialog.get_all())
            print("file chosen")


class LineAction(QAction):

    def __init__(self, parent, signal, reason):
        QAction.__init__(self,
                         reason + " Line",
                         parent,
                         triggered=self.call_line_signal)
        self.clicked = signal
        self.reason = reason

    def call_line_signal(self):
        self.clicked.emit(self.reason)


class ChooseExperimentDialog(QDialog):

    def __init__(self, parent, service, parabola_id):
        super().__init__(parent)

        self.setWindowTitle("Choose Experiment")
        layout = QVBoxLayout()

        self.month = QComboBox()
        # self.local_dir = dir + '/' if not dir.endswith("/") else dir
        self.service = service
        self.dir_names = []
        self.dirs_id = []
        page_token = None

        while True:
            # Call the Drive v3 API
            response = (self.service.files().list(
                q=
                f"mimeType='application/vnd.google-apps.folder' and '{parabola_id}' in parents",
                spaces="drive",
                fields="nextPageToken, files(id, name)",
                pageToken=page_token,
            ).execute())
            for file in response.get("files", []):
                # Process change
                self.dir_names.append(file.get("name"))
                self.dirs_id.append(file.get("id"))
            page_token = response.get("nextPageToken", None)
            if page_token is None:
                break

        layout.addWidget(self.month)

        self.day_layout = QHBoxLayout()
        self.day_layout.addWidget(QLabel("Enter the day:"))
        self.day_file = QComboBox()
        self.day_file.setLineEdit(QLineEdit())
        self.day_layout.addWidget(self.day_file)

        layout.addLayout(self.day_layout)

        self.month.currentIndexChanged.connect(self.on_month_select)
        self.month.addItems(self.dir_names)

        elevation_layout = QHBoxLayout()
        elevation_layout.addWidget(QLabel("Elevation:"))
        self.elevation_value = QLineEdit()
        self.elevation_value.setText("20")
        elevation_layout.addWidget(self.elevation_value)
        layout.addLayout(elevation_layout)

        azimuth_layout = QHBoxLayout()
        azimuth_layout.addWidget(QLabel("Azimuth:"))
        self.azimuth_value = QLineEdit()
        self.azimuth_value.setText("100")
        azimuth_layout.addWidget(self.azimuth_value)
        layout.addLayout(azimuth_layout)

        button_ok = QPushButton("OK")
        button_ok.clicked.connect(self.check_selection)
        layout.addWidget(button_ok)

        self.setLayout(layout)

    @Slot()
    def on_month_select(self, index):
        self.day_file.clear()
        id = self.dirs_id[index]
        filenames = []
        self.files_id = []
        page_token = None
        while True:
            # Call the Drive v3 API
            response = (self.service.files().list(
                q=f"'{id}' in parents",
                spaces="drive",
                fields="nextPageToken, files(id, name)",
                pageToken=page_token,
            ).execute())
            for file in response.get("files", []):
                # Process change
                filenames.append(file.get("name"))
                self.files_id.append(file.get("id"))
            page_token = response.get("nextPageToken", None)
            if page_token is None:
                break
        self.day_file.addItems(filenames)

    @Slot()
    def check_selection(self):
        # try:
        elevation, azimuth = self.get_coord()
        if elevation > 80 or elevation < 10:
            button = QMessageBox.critical(
                self,
                "Out Of Range",
                "Elevation must be contained between 10 and 80",
                buttons=QMessageBox.Ok,
                defaultButton=QMessageBox.Ok,
            )
            if button == QMessageBox.Ok:
                self.elevation_value.setText("")
        elif azimuth > 359 or azimuth < 1:
            button = QMessageBox.critical(
                self,
                "Out Of Range",
                "Azimuth must be contained between 1 and 359",
                buttons=QMessageBox.Ok,
                defaultButton=QMessageBox.Ok,
            )
            if button == QMessageBox.Ok:
                self.azimuth_value.setText("")
        else:
            self.accept()

    # except Exception:
    #     button = QMessageBox.critical(self,
    #                                   "Wrong Input",
    #                                   "Lower and Upper must be float",
    #                                   buttons=QMessageBox.Ok,
    #                                   defaultButton=QMessageBox.Ok)
    #     if button == QMessageBox.Ok:
    #         self.lower_value.setText(str(self.current_vmin))
    #         self.upper_value.setText(str(self.current_vmax))

    def get_coord(self):
        return (float(self.elevation_value.text()),
                float(self.azimuth_value.text()))

    def get_all(self):
        return (self.month.currentText(), {
            "name": self.day_file.currentText(),
            "id": self.files_id[self.day_file.currentIndex()]
        }, float(self.elevation_value.text()),
                float(self.azimuth_value.text()))
