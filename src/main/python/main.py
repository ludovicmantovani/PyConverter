import os
import sys

from PySide2.QtWidgets import QApplication

from package.main_window import MainWindow

RESOURCES = os.path.join(
    os.path.dirname(
        os.path.dirname(
            os.getcwd())),
    "resources")

CONTEXT = {
    "style": os.path.join(RESOURCES, "style.css"),
}

if __name__ == '__main__':
    app = QApplication()
    window = MainWindow(CONTEXT)
    window.resize(1500, 600)
    window.show()
    exit_code = app.exec_()
    sys.exit(exit_code)
