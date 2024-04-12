from PySide6.QtGui import QAction
from PySide6.QtCore import Slot, Signal
from PySide6.QtWidgets import (QLabel, QHBoxLayout, QVBoxLayout, QLineEdit,
                               QMenu, QPushButton, QDialog, QMessageBox)
from .submenu.color_menu import ColorMapMenu
# from .submenu.norm_menu import NormMenu


class MenuView(QMenu):

    min_max_changed = Signal(float, float)
    percentile_changed = Signal(float, float)

    # Passing the function here is terrible, I cannot find a better solution, maybe make the video open the dialog itself (seems clunky)
    def __init__(self, parent):
        QMenu.__init__(self, title="&View", parent=parent)

        # self.color_norm_menu = NormMenu(
        #     config["norm_type"],
        #     0 if config["norm_type"] != "Power" else config.getfloat("gamma"),
        #     self)
        # self.addMenu(self.color_norm_menu)

        self.color_map_menu = ColorMapMenu("gray", self)
        self.addMenu(self.color_map_menu)

        # self.orientation_menu = self.addMenu("Orientation")
        # self.orientation_menu.reverseX_action = QAction(
        #     "Reverse X",
        #     self.orientation_menu,
        #     checkable=True,
        #     checked=config.getboolean("reverse_x"))
        # self.orientation_menu.reverseY_action = QAction(
        #     "Reverse Y",
        #     self.orientation_menu,
        #     checked=config.getboolean("reverse_y"),
        #     checkable=True)
        # self.orientation_menu.transpose_action = QAction(
        #     "Transpose",
        #     self.orientation_menu,
        #     checked=config.getboolean("transpose"),
        #     checkable=True)
        # self.orientation_menu.addAction(self.orientation_menu.reverseX_action)
        # self.orientation_menu.addAction(self.orientation_menu.reverseY_action)
        # self.orientation_menu.addAction(self.orientation_menu.transpose_action)
        #
        # self.cutoff_menu = self.addMenu("CutOff")
        # self.cutoff_menu.addAction(
        #     QAction("Change Color limits",
        #             self.cutoff_menu,
        #             triggered=lambda: self.open_min_max_color_dialog(
        #                 get_min_max_function)))
        # self.min_percentile = config.getfloat("min_percentile")
        # self.max_percentile = config.getfloat("max_percentile")
        # self.cutoff_menu.addAction(
        #     QAction("Change Percentiles",
        #             self.cutoff_menu,
        #             triggered=self.open_percentile_dialog))
        # self.subtract_background_action = QAction(
        #     "Subtract background",
        #     self,
        #     checked=config.getboolean("subtract_background"),
        #     checkable=True)
        # self.addAction(self.subtract_background_action)

    def open_min_max_color_dialog(self, get_percentile_function):
        dialog = ChooseMinMaxDialog(*get_percentile_function(), self)
        if dialog.exec():
            self.min_max_changed.emit(*dialog.get_selection())
            print("Color limits changed")

    def open_percentile_dialog(self):

        dialog = ChoosePercentageDialog(self, self.min_percentile,
                                        self.max_percentile)
        if dialog.exec():
            self.percentile_changed.emit(*dialog.get_values())
            self.min_percentile, self.max_percentile = dialog.get_values()
            print("Percentile changed")


class ChoosePercentageDialog(QDialog):

    def __init__(self, parent, min_per, max_per):
        super().__init__(parent)
        self.setWindowTitle("Set Percentile")
        layout = QVBoxLayout()

        upper_layout = QHBoxLayout()
        upper_layout.addWidget(QLabel("Upper:"))
        self.upper_value = QLineEdit()
        self.upper_value.setText(str(max_per))
        upper_layout.addWidget(self.upper_value)
        layout.addLayout(upper_layout)

        lower_layout = QHBoxLayout()
        lower_layout.addWidget(QLabel("Lower:"))
        self.lower_value = QLineEdit()
        self.lower_value.setText(str(min_per))
        lower_layout.addWidget(self.lower_value)
        layout.addLayout(lower_layout)

        self.current_per_min = min_per
        self.current_per_max = max_per
        button_ok = QPushButton("OK")
        button_ok.clicked.connect(self.check_selection)
        layout.addWidget(button_ok)

        self.setLayout(layout)

    @Slot()
    def check_selection(self):
        try:
            max = float(self.upper_value.text())
            min = float(self.lower_value.text())
            if min < 0 or max > 100 or min >= max:
                button = QMessageBox.critical(
                    self,
                    "Out Of Range",
                    "Percentile Values between 0 and 100\nMin must be smaller than max",
                    buttons=QMessageBox.Ok,
                    defaultButton=QMessageBox.Ok,
                )
                if button == QMessageBox.Ok:
                    self.lower_value.setText(self.current_per_min)
                    self.upper_value.setText(self.current_per_max)
            else:
                self.accept()
        except Exception:
            button = QMessageBox.critical(
                self,
                "Wrong Input",
                "Percentile Values between 0 and 100\nMin must be smaller than max",
                buttons=QMessageBox.Ok,
                defaultButton=QMessageBox.Ok)
            if button == QMessageBox.Ok:
                self.lower_value.setText(self.current_per_min)
                self.upper_value.setText(self.current_per_max)

    def get_values(self):
        return float(self.lower_value.text()), float(self.upper_value.text())


class ChooseMinMaxDialog(QDialog):

    def __init__(self, min, max, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Set Percentile")
        layout = QVBoxLayout()

        upper_layout = QHBoxLayout()
        upper_layout.addWidget(QLabel("Upper:"))
        self.upper_value = QLineEdit()
        self.upper_value.setText(str(max))
        upper_layout.addWidget(self.upper_value)
        layout.addLayout(upper_layout)

        lower_layout = QHBoxLayout()
        lower_layout.addWidget(QLabel("Lower:"))
        self.lower_value = QLineEdit()
        self.lower_value.setText(str(min))
        lower_layout.addWidget(self.lower_value)
        layout.addLayout(lower_layout)

        self.current_vmin = min
        self.current_vmax = max
        button_ok = QPushButton("OK")
        button_ok.clicked.connect(self.check_selection)
        layout.addWidget(button_ok)

        self.setLayout(layout)

    @Slot()
    def check_selection(self):
        try:
            vmin, vmax = self.get_selection()
            if vmax < vmin:
                button = QMessageBox.critical(
                    self,
                    "Out Of Range",
                    "Lower and Upper must be ordered",
                    buttons=QMessageBox.Ok,
                    defaultButton=QMessageBox.Ok,
                )
                if button == QMessageBox.Ok:
                    self.lower_value.setText(str(self.current_vmin))
                    self.upper_value.setText(str(self.current_vmax))
            else:
                self.accept()
        except Exception:
            button = QMessageBox.critical(self,
                                          "Wrong Input",
                                          "Lower and Upper must be float",
                                          buttons=QMessageBox.Ok,
                                          defaultButton=QMessageBox.Ok)
            if button == QMessageBox.Ok:
                self.lower_value.setText(str(self.current_vmin))
                self.upper_value.setText(str(self.current_vmax))

    def get_selection(self):
        return float(self.lower_value.text()), float(self.upper_value.text())
