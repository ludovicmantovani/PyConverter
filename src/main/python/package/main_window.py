from PySide2.QtCore import Qt, QObject, QThread, Signal
from PySide2.QtGui import QKeySequence
from PySide2.QtWidgets import QWidget, QLabel, QSpinBox, QLineEdit, QPushButton, QListWidget, QGridLayout, \
    QListWidgetItem, QStyle, QShortcut, QMessageBox, QProgressDialog

from src.main.python.package.image import CustomImage


class Worker(QObject):
    image_converted = Signal(object, bool)
    finished = Signal()

    def __init__(self, images_to_convert, quality, size, folder):
        super().__init__()
        self.images_to_convert = images_to_convert
        self.quality = quality
        self.size = size
        self.folder = folder
        self.runs = True

    def convert_images(self):
        for image_lw_item in self.images_to_convert:
            if self.runs and not image_lw_item.processed:
                image = CustomImage(path=image_lw_item.text(), folder=self.folder)
                success = image.reduce_image(size=self.size, quality=self.quality)
                self.image_converted.emit(image_lw_item, success)
        self.finished.emit()


# noinspection PyAttributeOutsideInit
class MainWindow(QWidget):
    def __init__(self, context):
        super().__init__()
        self.ctx = context
        self.setWindowTitle("PyConverter")

        self.apply_icon = self.style().standardIcon(QStyle.SP_DialogApplyButton)
        self.cancel_icon = self.style().standardIcon(QStyle.SP_DialogCancelButton)

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
        self.lbl_drop_info = QLabel("^ Déposez les images sur l'interface")

    def modify_widgets(self):
        style_file = self.ctx.get("style", None)
        if style_file:
            with open(style_file, "r") as f:
                self.setStyleSheet(f.read())

        # Alignment
        self.spn_quality.setAlignment(Qt.AlignRight)
        self.spn_size.setAlignment(Qt.AlignRight)
        self.le_dossier_out.setAlignment(Qt.AlignRight)

        # Range
        self.spn_quality.setRange(1, 100)
        self.spn_quality.setValue(75)
        self.spn_size.setRange(1, 100)
        self.spn_size.setValue(75)

        # Divers
        self.le_dossier_out.setPlaceholderText("Dossier de sortie...")
        self.le_dossier_out.setText("reduced")
        self.lbl_drop_info.setVisible(False)

        self.setAcceptDrops(True)
        self.lw_files.setAlternatingRowColors(True)
        self.lw_files.setSelectionMode(QListWidget.ExtendedSelection)

    def create_layouts(self):
        self.main_layout = QGridLayout(self)

    def add_widgets_to_layouts(self):
        self.main_layout.addWidget(self.lbl_quality, 0, 0, 1, 1)
        self.main_layout.addWidget(self.spn_quality, 0, 1, 1, 1)
        self.main_layout.addWidget(self.lbl_size, 1, 0, 1, 1)
        self.main_layout.addWidget(self.spn_size, 1, 1, 1, 1)
        self.main_layout.addWidget(self.lbl_dossier_out, 2, 0, 1, 1)
        self.main_layout.addWidget(self.le_dossier_out, 2, 1, 1, 1)
        self.main_layout.addWidget(self.lw_files, 3, 0, 1, 2)
        self.main_layout.addWidget(self.lbl_drop_info, 4, 0, 1, 2)
        self.main_layout.addWidget(self.btn_convert, 5, 0, 1, 2)

    def setup_connections(self):
        QShortcut(QKeySequence("Backspace"), self.lw_files, self.delete_seleted_items)
        QShortcut(QKeySequence("Delete"), self.lw_files, self.delete_seleted_items)
        self.btn_convert.clicked.connect(self.convert_images)

    def convert_images(self):
        quality = self.spn_quality.value()
        size = self.spn_size.value() / 100.0
        folder = self.le_dossier_out.text()

        lw_items = [self.lw_files.item(index) for index in range(self.lw_files.count())]
        to_convert = [1 for lw_item in lw_items if not lw_item.processed]

        if not to_convert:
            msg_box = QMessageBox(
                QMessageBox.Warning,
                "Aucunne image à convertir",
                "Toutes les images ont déja été converties."
            )
            msg_box.exec_()
            return False

        self.thread = QThread(self)
        self.worker = Worker(images_to_convert=lw_items,
                             quality=quality,
                             size=size,
                             folder=folder)
        self.worker.moveToThread(self.thread)
        self.worker.image_converted.connect(self.image_converted)
        self.thread.started.connect(self.worker.convert_images)
        self.worker.finished.connect(self.thread.quit)
        self.thread.start()

        self.prg_dialog = QProgressDialog("Conversion des images", "Annuler...", 1, len(to_convert))
        self.prg_dialog.canceled.connect(self.abort)
        self.prg_dialog.show()

    def abort(self):
        self.worker.runs = False
        self.thread.quit()

    def image_converted(self, lw_item, success):
        if success:
            lw_item.setIcon(self.apply_icon)
            lw_item.processed = True
            self.prg_dialog.setValue(self.prg_dialog.value() + 1)

    def delete_seleted_items(self):
        for lw_item in self.lw_files.selectedItems():
            row = self.lw_files.row(lw_item)
            self.lw_files.takeItem(row)

    def dragEnterEvent(self, event):
        self.lbl_drop_info.setVisible(True)
        event.accept()

    def dragLeaveEvent(self, event):
        self.lbl_drop_info.setVisible(False)

    def dropEvent(self, event):
        self.lbl_drop_info.setVisible(False)
        event.accept()
        for url in event.mimeData().urls():
            self.add_file(path=url.toLocalFile())

    def add_file(self, path):
        items = [self.lw_files.item(index).text() for index in range(self.lw_files.count())]
        if path not in items:
            lw_item = QListWidgetItem(path)
            lw_item.setIcon(self.cancel_icon)
            lw_item.processed = False
            self.lw_files.addItem(lw_item)
