from PySide6.QtGui import QAction, QActionGroup
from PySide6.QtCore import Slot, Signal
from PySide6.QtWidgets import (QLabel, QHBoxLayout, QVBoxLayout, QMenuBar,
                               QLineEdit, QMenu, QPushButton, QDialog,
                               QMessageBox, QComboBox)


class NormMenu(QMenu):
    norm_chosen = Signal(str, float)  #type and gamma if necessary

    def __init__(self, default_type, default_gamma, parent):
        QMenu.__init__(self, "Color Normalization", parent=parent)
        self.current_gamma = default_gamma
        action_group = QActionGroup(self)
        linear_check = False
        log_check = False
        power_check = False
        match default_type:
            case "Linear":
                linear_check = True
            case "Log":
                log_check = True
            case "Power":
                power_check = True
        self.addAction(
            QAction('Linear',
                    action_group,
                    checkable=True,
                    checked=linear_check,
                    triggered=lambda: self.call_color_map_signal('Linear')))
        self.addAction(
            QAction('Log',
                    action_group,
                    checkable=True,
                    checked=log_check,
                    triggered=lambda: self.call_color_map_signal('Log')))
        self.addAction(
            QAction('Power',
                    action_group,
                    checkable=True,
                    checked=power_check,
                    triggered=lambda: self.call_color_map_signal('Power')))

    def call_color_map_signal(self, norm_type):
        if norm_type == "Power":
            dialog = ChooseGammaNorm(self, self.current_gamma)
            if dialog.exec():
                self.current_gamma = float(dialog.get_gamma())
                self.norm_chosen.emit(norm_type, float(dialog.get_gamma()))
                print("gamma chosen", self.current_gamma)

        self.norm_chosen.emit(norm_type, 0)  # 0 is unused for this types


class ChooseGammaNorm(QDialog):

    def __init__(self, parent, current_gamma):
        super().__init__(parent)

        self.setWindowTitle("Choose Gamma")
        gamma_layout = QHBoxLayout()
        gamma_layout.addWidget(QLabel("Enter Gamma:"))
        self.current_gamma = str(current_gamma)
        self.gamma_value = QLineEdit()
        self.gamma_value.setText(self.current_gamma)
        gamma_layout.addWidget(self.gamma_value)
        button_ok = QPushButton("OK")
        button_ok.clicked.connect(self.check_gamma)
        gamma_layout.addWidget(button_ok)

        self.setLayout(gamma_layout)

    @Slot()
    def check_gamma(self):
        try:
            gamma = float(self.gamma_value.text())
            if gamma > 1 or gamma < 0:
                button = QMessageBox.critical(
                    self,
                    "Out Of Range",
                    "Gamma must stay between 0 and 1",
                    buttons=QMessageBox.Ok,
                    defaultButton=QMessageBox.Ok,
                )
                if button == QMessageBox.Ok:
                    self.gamma_value.setText(self.current_gamma)
            else:
                self.accept()
        except Exception:
            button = QMessageBox.critical(
                self,
                "Wrong Input",
                "Gamma must be a float between 0 and 1",
                buttons=QMessageBox.Ok,
                defaultButton=QMessageBox.Ok)
            if button == QMessageBox.Ok:
                self.gamma_value.setText(self.current_gamma)

    def get_gamma(self):
        return self.gamma_value.text()
