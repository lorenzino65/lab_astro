from os.path import expanduser
from os import walk
from pathlib import Path


class Line(object):

    # other time with no better solution than to pass the function
    def __init__(self, line):
        self.line = line
        self.xs = [0]
        self.ys = [0]
        self.cid = line.figure.canvas.mpl_connect('button_press_event', self)
        self.start = True

    def __del__(self):
        self.line.remove()

    def __call__(self, event):
        print("click", event)
        if event.inaxes != self.line.axes or len(self.xs) == 2: return
        if self.start:
            self.start = False
            # Other alternative is just event.x, event.y, TO-DO: ask Michael
            self.xs = [event.xdata]
            self.ys = [event.ydata]
        else:
            self.xs.append(event.xdata)
            self.ys.append(event.ydata)
        self.line.set_data(self.xs, self.ys)
        self.line.figure.canvas.draw()
        if len(self.xs) == 2:
            self.line.figure.canvas.mpl_disconnect(self.cid)

    def save_line(self, name, experiment, dir):
        if dir is not None:
            try:
                local_dir = dir + '/' if not dir.endswith("/") else dir
                local_dir = expanduser(dir + name + "/" + experiment + "/")
                Path(local_dir).mkdir(
                    parents=True, exist_ok=True)  # Just to assure it exists
                filenames = next(walk(local_dir),
                                 (None, None, []))[2]  # [] if no file
                print(filenames)
                print(local_dir)
                count = 0
                for file in filenames:
                    if file.startswith('line_'):
                        count += 1
                count += 1
                line_file = open(local_dir + "line_" + str(count) + ".txt",
                                 "w")
                line_file.write(
                    "Start:%5.3f,%5.3f\nEnd:%5.3f,%5.3f" %
                    (self.xs[0], self.ys[0], self.xs[1], self.ys[1]))
                line_file.close()
                print("Line Saved")
            except PermissionError:
                print(
                    "File cannot be written, missing permission from user:\n It will be printed here:\n"
                )
                print(name, experiment, "\n")
                print("Start:%5.3f,%5.3f\nEnd:%5.3f,%5.3f" %
                      (self.xs[0], self.ys[0], self.xs[1], self.ys[1]))
        else:
            print(name, experiment, "\n")
            print("Start:%5.3f,%5.3f\nEnd:%5.3f,%5.3f" %
                  (self.xs[0], self.ys[0], self.xs[1], self.ys[1]))
        # print((self.name))

    @property
    def isValid(self):
        return len(self.xs) == 2 and len(self.ys) == 2
