import sys

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
        self.config = ConfigParser()
        self.config.read(config_path)
        self.config_path = config_path

        self.conf_title = "Config"
        config_section = self.config.sections()
        if self.conf_title not in config_section or self.config.get(
                self.conf_title, "line_dir") == '':
            self.config[self.conf_title] = {}
            self.save_config(self.conf_title, self.get_conf_defaults())
            # Just comment this if too agressive
            print("No line dir")
            line_dir = None
        else:
            line_dir = self.config.get(self.conf_title, 'line_dir')

        self.view_title = "View"
        if self.view_title not in config_section:
            self.config[self.view_title] = {}
            self.save_config(self.view_title, self.get_view_defaults())

        # Central widget
        self._main = QWidget()
        self.setCentralWidget(self._main)

        # Main layout
        layout = QHBoxLayout(self._main)
        self.video_panel = VideoPanel(self.config[self.view_title], line_dir)
        layout.addLayout(self.video_panel)

        # Main menu bar
        self.top_menu = QMenuBar(self)
        self.setMenuBar(self.top_menu)
        self.menu_file = MenuFileAndLine(self)
        self.top_menu.addMenu(self.menu_file)
        self.menu_view = MenuView(
            self, self.config[self.view_title],
            self.video_panel.get_color_vmin_vmax)  # the bad function
        self.top_menu.addMenu(self.menu_view)

        # Signals
        self.menu_file.open_success.connect(self.video_panel.open_video)
        self.menu_file.line_signal.connect(self.video_panel.line_control)
        self.menu_view.color_map_menu.color_chosen.connect(
            self.video_panel.set_color_map)

        # Config
        self.menu_view.color_map_menu.color_chosen.connect(
            self.save_color_map_config)

    def get_conf_defaults(self):
        return {
            "line_dir": '',
        }

    def get_view_defaults(self):
        return {
            "map_color": "gray",
            "norm_type": "Linear",
            "reverse_x": "False",
            "reverse_y": "False",
            "transpose": "False",
            "subtract_background": "False",
            "min_percentile": "1",
            "max_percentile": "99"
        }

    def save_config(self, category, configs):
        try:
            for name in configs.keys():
                self.config[category][name] = configs[name]
            with open(self.config_path, 'w') as f:
                self.config.write(f)
        except PermissionError:
            pass

    @Slot()
    def save_color_map_config(self, map_color):
        self.save_config(self.view_title, {'map_color': map_color})

    @Slot()
    def save_color_norm_config(self, norm_type, gamma):
        configs = {'norm_type': norm_type}
        if norm_type == "Power":
            configs["gamma"] = str(gamma)
        self.save_config(self.view_title, configs)

    def save_checkable_options_config(self, checkable_type, checked):
        if self.config.get(self.view_title, checkable_type) != checked:
            if checked:
                configs = {checkable_type: "True"}
            else:
                configs = {checkable_type: "False"}
            self.save_config(self.view_title, configs)

    @Slot()
    def save_reverseX_config(self, checked):
        self.save_checkable_options_config('reverse_x', checked)

    @Slot()
    def save_reverseY_config(self, checked):
        self.save_checkable_options_config('reverse_y', checked)

    @Slot()
    def save_transpose_config(self, checked):
        self.save_checkable_options_config('transpose', checked)

    @Slot()
    def save_subtract_background_config(self, checked):
        self.save_checkable_options_config("subtract_background", checked)

    @Slot()
    def save_percentile_config(self, min, max):
        config = {'min_percentile': str(min), 'max_percentile': str(max)}
        self.save_config(self.view_title, config)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = ApplicationWindow('config/config.ini')
    w.setFixedSize(1280, 720)
    w.show()
    app.exec()
