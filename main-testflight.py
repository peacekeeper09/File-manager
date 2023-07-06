import os
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTreeView, QFileSystemModel, QDockWidget, QPushButton, QWidget, QVBoxLayout, QMessageBox


class FileManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("File Manager")
        self.setGeometry(100, 100, 800, 600)

        self.tree_view = QTreeView(self)
        self.model = QFileSystemModel()
        self.model.setRootPath("")
        self.tree_view.setModel(self.model)
        self.tree_view.setRootIndex(self.model.index(os.path.expanduser("~")))
        self.tree_view.doubleClicked.connect(self.open_file)

        self.setCentralWidget(self.tree_view)

        self.dock = QDockWidget("File Operations", self)
        self.addDockWidget(1, self.dock)

        self.file_operations_widget = QWidget(self.dock)
        self.dock.setWidget(self.file_operations_widget)

        self.init_file_operations()

    def init_file_operations(self):
        layout = QVBoxLayout()
        self.file_operations_widget.setLayout(layout)

        open_button = QPushButton("Open", self.file_operations_widget)
        open_button.clicked.connect(self.open_selected_file)
        layout.addWidget(open_button)

        delete_button = QPushButton("Delete", self.file_operations_widget)
        delete_button.clicked.connect(self.delete_selected_file)
        layout.addWidget(delete_button)

    def open_selected_file(self):
        selected_index = self.tree_view.selectedIndexes()[0]
        file_path = self.model.filePath(selected_index)
        if os.path.isfile(file_path):
            os.startfile(file_path)

    def delete_selected_file(self):
        selected_index = self.tree_view.selectedIndexes()[0]
        file_path = self.model.filePath(selected_index)
        if os.path.isfile(file_path):
            confirmation = QMessageBox.question(self, "Confirm Deletion",
                                                f"Are you sure you want to delete {file_path}?",
                                                QMessageBox.Yes | QMessageBox.No)
            if confirmation == QMessageBox.Yes:
                os.remove(file_path)
                self.model.remove(file_path)

    def open_file(self, index):
        file_path = self.model.filePath(index)
        if os.path.isfile(file_path):
            os.startfile(file_path)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    file_manager = FileManager()
    file_manager.show()
    sys.exit(app.exec_())
