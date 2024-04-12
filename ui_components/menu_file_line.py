from PySide6.QtGui import QAction
from os.path import expanduser
from os import walk
from PySide6.QtCore import Slot, Signal
from PySide6.QtWidgets import (QLabel, QHBoxLayout, QVBoxLayout, QLineEdit,
                               QMenu, QPushButton, QDialog, QComboBox)


class MenuFileAndLine(QMenu):

    line_signal = Signal(str)
    open_success = Signal(str, str)

    def __init__(self, parent=None):
        QMenu.__init__(self, title="&File", parent=parent)

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
        dialog = ChooseExperimentDialog(self)
        if dialog.exec():
            self.open_success.emit(*dialog.get_selection())
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

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Choose Experiment")
        layout = QVBoxLayout()

        self.combo_camera = QComboBox()
        # self.local_dir = dir + '/' if not dir.endswith("/") else dir
        self.local_dir = "./files/"
        self.local_dir = expanduser(self.local_dir)
        filenames = next(walk(self.local_dir),
                         (None, None, []))[2]  # [] if no file
        # line_file = open(local_dir + "line_" + str(count) + ".txt", "w")

        self.combo_camera.addItems(filenames)
        # self.combo_camera.currentTextChanged.connect(self.on_camera_select)
        layout.addWidget(self.combo_camera)

        self.button_ok = QPushButton("OK")
        self.button_ok.clicked.connect(self.accept)
        layout.addWidget(self.button_ok)

        self.setLayout(layout)

    def get_selection(self):
        return (self.combo_camera.currentText(), self.local_dir)
