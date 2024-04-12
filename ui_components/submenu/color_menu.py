from PySide6.QtGui import QAction, QActionGroup
from PySide6.QtCore import Slot, Signal
from PySide6.QtWidgets import QMenu


class ColorMapMenu(QMenu):

    color_chosen = Signal(str)

    def __init__(self, default_col, parent):
        QMenu.__init__(self, title="Color Maps", parent=parent)
        maps = {
            'Perceptually Uniform Sequential':
            ['viridis', 'plasma', 'inferno', 'magma', 'cividis'],
            'Sequential': [
                'Greys', 'Purples', 'Blues', 'Greens', 'Oranges', 'Reds',
                'YlOrBr', 'YlOrRd', 'OrRd', 'PuRd', 'RdPu', 'BuPu', 'GnBu',
                'PuBu', 'YlGnBu', 'PuBuGn', 'BuGn', 'YlGn'
            ],
            'Sequential (2)': [
                'binary', 'gist_yarg', 'gist_gray', 'gray', 'bone', 'pink',
                'spring', 'summer', 'autumn', 'winter', 'cool', 'Wistia',
                'hot', 'afmhot', 'gist_heat', 'copper'
            ],
            'Miscellaneous': [
                'flag', 'prism', 'ocean', 'gist_earth', 'terrain',
                'gist_stern', 'gnuplot', 'gnuplot2', 'CMRmap', 'cubehelix',
                'brg', 'gist_rainbow', 'rainbow', 'jet', 'turbo',
                'nipy_spectral', 'gist_ncar'
            ]
        }

        action_group = QActionGroup(self)
        for type in maps.keys():
            menu_type = QMenu(title=type, parent=self)
            for col in maps[type]:
                menu_type.addAction(
                    QAction(col,
                            action_group,
                            checkable=True,
                            checked=True if col == default_col else False,
                            triggered=self.send_color(col)))
            self.addMenu(menu_type)

    def send_color(
        self, color
    ):  # Otherwise python just rewrites over same pointer and changes the value of color
        return lambda: self.color_chosen.emit(color)
