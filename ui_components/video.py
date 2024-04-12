import math
import numpy as np
from matplotlib.backends.backend_qtagg import FigureCanvas
from matplotlib.figure import Figure
import matplotlib.colors as colors
from matplotlib import colormaps
from PySide6.QtCore import Slot, Qt
from PySide6.QtWidgets import (
    QLabel,
    QVBoxLayout,
)
from .video_commands import VideoCommands
from .line import Line
from .table import MegaTable


def conv(x):
    return x.replace(',', '.').encode()


class VideoPanel(QVBoxLayout):

    def __init__(self, ids, service, max_lenght, parent=None):
        QVBoxLayout.__init__(self)

        self.line_dir = None
        self.ids = ids
        self.service = service
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.cid = self.canvas.mpl_connect('button_press_event',
                                           self.give_point)
        self.figure.set_canvas(self.canvas)
        # self.axes = self.canvas.figure.add_subplot(111)
        self.axes = self.canvas.figure.subplots()
        self.plot, = self.axes.plot([], [])
        self.mean_plot, = self.axes.plot([], [])
        self.max_lenght = max_lenght
        # self.image = self.axes.imshow(np.zeros((640, 512)),
        #                               cmap='gray',
        # vmin=0,
        # vmax=1)
        # for tick in self.axes.get_xticklabels():
        #     tick.set_visible(False)
        # for tick in self.axes.get_yticklabels():
        # #     tick.set_visible(False)
        # self.axes.set_axis_off()
        # self.axes.set_xlim(0, 511)
        # self.axes.set_ylim(0, 511)
        # self.axes.set_aspect(1)

        self.name = "Nothing"
        self.experiment = "Empty"
        self.is_video_loaded = False
        self.is_line_loaded = False
        self.current_frame = -1
        self.hist_min = 1
        self.hist_max = 99
        self.vmin = 0
        self.vmax = 1
        self.cmap = colormaps["gray"]

        self.canvas.draw()

        # Layout
        self.title = QLabel("Looking at nothing")
        self.title.setAlignment(Qt.AlignCenter)
        self.addWidget(self.title, 1)
        self.addWidget(self.canvas, 90)
        self.commands = VideoCommands()
        self.addLayout(self.commands, 7)

        # Signals
        self.commands.updateFrame.connect(self.check_and_set_frame)
        self.commands.updateTime.connect(self.set_time)  # Still dont know

    def give_point(self, event):
        print("click", event)

    def get_movement_now(self):
        if self.is_video_loaded:
            return self.movement(self.video.time[self.current_frame])
        else:
            return (0, 0)

    @Slot()
    def open_video(self, month, file, elevation, azimuth):
        print(file)
        # self.video = self.get_video(camera, experiment_number)
        # self.movement = self.get_movement(camera, experiment_number)
        self.table = MegaTable(self.service, self.ids["ricevitore"], month,
                               file, elevation, azimuth, self.max_lenght)
        self.name = file["name"]  # For saving the lines
        self.title.setText("Looking at " + file["name"])
        self.is_video_loaded = True

        self.plot.set(color=self.cmap(0.5))
        self.axes.set_xlim(self.table.x[0], self.table.x[-1])
        # to see if better way
        self.axes.set_ylim(np.min(self.table.video.min(0)[3:]),
                           np.max(self.table.video.max(0)[3:]))
        self.commands.set_range(0, len(self.table.video))
        self.commands.reset()
        self.set_frame(0)

    def get_line_color(self):
        color = self.cmap(0.5)
        return (1 - color[0], 1 - color[1], 1 - color[2], 1.0
                )  # Highest contrast

    def remove_line(self):
        try:
            del self.line
        except Exception as Error:
            print(Error)

    def add_line(self):
        if hasattr(self, 'line'):
            self.remove_line()
        line, = self.axes.plot([0], [0], color=self.get_line_color())

        self.line = Line(line)

    @Slot()
    def line_control(self, reason):
        match reason:
            case "Create":
                self.add_line()
            case "Save":
                if not hasattr(self, 'line') or not self.line.isValid:
                    raise Exception('Line not valid')
                self.line.save_line(self.name, self.experiment, self.line_dir)
            case _:
                print("Something broke")

    @Slot()
    def set_norm(self, norm_type, gamma):
        match norm_type:
            case "Linear":
                self.norm = colors.Normalize()
            case "Log":
                self.norm = colors.LogNorm()
            case "Power":
                self.norm = colors.PowerNorm(gamma=gamma)
            case _:
                print("Something broke with norms")

        if self.is_video_loaded:
            self.image.set_norm(self.norm)
            self.canvas.draw()

    @Slot()
    def set_color_map(self, color):
        self.cmap = colormaps[color]
        # if self.is_video_loaded:
        # self.image.set_cmap(self.cmap)
        self.plot.set(color=self.cmap(0.5))
        self.mean_plot.set(color=self.get_line_color())
        if hasattr(self, 'line'):
            self.line.line.set(color=self.get_line_color())
        self.canvas.draw()

    @Slot()
    def set_reverseX(self, checked):
        if checked:
            self.reverseX = -1
        else:
            self.reverseX = 1
        self.check_and_set_frame(self.current_frame)

    @Slot()
    def set_reverseY(self, checked):
        if checked:
            self.reverseY = -1
        else:
            self.reverseY = 1
        self.check_and_set_frame(self.current_frame)

    @Slot()
    def set_transpose(self, checked):
        self.transpose = checked
        self.check_and_set_frame(self.current_frame)

    def get_color_vmin_vmax(self):
        return self.vmin, self.vmax

    @Slot()
    def set_percentile(self, min, max):
        self.hist_min = min
        self.hist_max = max
        self.check_and_set_frame(self.current_frame)

    @Slot()
    def set_color_vmin_vmax(self, vmin, vmax):
        self.vmax = vmax
        self.vmin = vmin
        if self.is_video_loaded:
            self.image.set(clim=(self.vmin, self.vmax))
            self.canvas.draw()

    @Slot()
    def set_remove_background(self, checked):
        self.remove_background = checked
        self.check_and_set_frame(self.current_frame)

    @Slot()
    def set_time(self, time):
        if self.is_video_loaded:
            index = np.abs(self.video.time - time).argmin()
            self.set_frame(index)

    @Slot()
    def check_and_set_frame(self, index):
        if self.is_video_loaded:
            self.set_frame(index)

    def set_frame(self, index):
        if index != self.current_frame:
            try:
                if index >= 0 and index < len(self.table.video):
                    self.commands.set_all(index, index)
                    temp = self.table.video[index][3:]
                    # temp[temp < 0] = 0
                    # temp[temp >= 0x7FFF] = 0x7FFF - 1
                    # self.image.set_data(temp)

                    self.plot.set_data(self.table.x, temp)
                    self.mean_plot.set_data(
                        self.table.x,
                        self.table.mean[math.floor(index / self.max_lenght)])
                    # self.axes.plot(self.x, temp[3:])
                    # self.axes.set_xlim(0, temp.shape[1] - 1)
                    # self.axes.set_ylim(0, temp.shape[0] - 1)
                    # self.vmin = np.percentile(temp, self.hist_min)
                    # self.vmax = np.percentile(temp, self.hist_max)
                    self.current_frame = index
                    self.canvas.draw()
            except Exception as Error:
                print(Error)
