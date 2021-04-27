import sys
from PySide2 import QtWidgets, QtGui

from ambilight import CaptureBordersThread, set_color
from color_circle_dialog import ColorCircleDialog


class SystemTrayIcon(QtWidgets.QSystemTrayIcon):
    """
    CREATE A SYSTEM TRAY ICON CLASS AND ADD MENU
    """

    def __init__(self, icon, parent=None):
        QtWidgets.QSystemTrayIcon.__init__(self, icon, parent)
        # self.setToolTip(f'VFX Pipeline Application Build - 3.2.56')
        menu = QtWidgets.QMenu(parent)
        open_app = menu.addAction("Ambilight")
        open_app.triggered.connect(self.start_ambilight)
        open_app.setIcon(QtGui.QIcon("icon.png"))

        open_app = menu.addAction("Stop Ambilight")
        open_app.triggered.connect(self.stop_ambilight)
        open_app.setIcon(QtGui.QIcon("icon.png"))

        open_app = menu.addAction("Select color")
        open_app.triggered.connect(self.show_color_picker)
        open_app.setIcon(QtGui.QIcon("icon.png"))

        exit_ = menu.addAction("Exit")
        exit_.triggered.connect(self.exit)
        exit_.setIcon(QtGui.QIcon("icon.png"))

        menu.addSeparator()
        self.setContextMenu(menu)
        self.capture_borders_thread = None

    def exit(self):
        if self.capture_borders_thread is not None:
            self.capture_borders_thread.stop()
        sys.exit()

    def show_color_picker(self):
        def color_picker_cb(x):
            rgb = x.getRgb()
            set_color([rgb[0], rgb[1], rgb[2]])

        window = ColorCircleDialog()
        window.currentColorChanged.connect(color_picker_cb)
        window.show()

    def start_ambilight(self):
        self.capture_borders_thread = CaptureBordersThread()
        self.capture_borders_thread.start()

    def stop_ambilight(self):
        """
        this function will open application
        :return:
        """
        self.capture_borders_thread.stop()


def main():
    app = QtWidgets.QApplication(sys.argv)
    w = QtWidgets.QWidget()
    tray_icon = SystemTrayIcon(QtGui.QIcon("icon.png"), w)
    tray_icon.show()
    # tray_icon.showMessage('VFX Pipeline', 'Hello "Name of logged in ID')
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
