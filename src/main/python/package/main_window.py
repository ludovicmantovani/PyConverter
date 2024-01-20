from functools import partial

from PySide2.QtWidgets import QWidget, QLabel, QSpinBox, QLineEdit, QPushButton, QListWidget


# noinspection PyAttributeOutsideInit
class MainWindow(QWidget):
    def __init__(self, context):
        super().__init__()
        self.ctx = context
        self.setWindowTitle("PyConverter")
        self.setup_ui()

    def setup_ui(self):
        self.create_widgets()
        self.modify_widgets()
        self.create_layouts()
        self.add_widgets_to_layouts()
        self.setup_connections()

    def create_widgets(self):
        self.lbl_quality = QLabel("Qualité:")
        self.spn_quality = QSpinBox()
        self.lbl_size = QLabel("Taille:")
        self.spn_size = QSpinBox()
        self.lbl_dossier_out = QLabel("Dossier de sortie:")
        self.le_dossier_out = QLineEdit()
        self.lw_files = QListWidget()
        self.btn_convert = QPushButton("Conversion")
        self.lbl_drop_info = QLabel("^Déposez les images sur l'interface")

    def modify_widgets(self):
        style_file = self.ctx.get("style", None)
        if style_file:
            with open(style_file, "r") as f:
                self.setStyleSheet(f.read())

    def create_layouts(self):
        pass

    def add_widgets_to_layouts(self):
        pass

    def setup_connections(self):
        pass
