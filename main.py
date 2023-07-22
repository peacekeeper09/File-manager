import os
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTreeView, QFileSystemModel, QDockWidget, QPushButton, QWidget, QVBoxLayout, QMessageBox, QFileDialog, QLineEdit, QInputDialog


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

        self.select_disk_button = QPushButton("Select Disk", self)
        self.select_disk_button.clicked.connect(self.show_disk_selection_dialog)
        self.statusBar().addWidget(self.select_disk_button)

    def init_file_operations(self):
        layout = QVBoxLayout()
        self.file_operations_widget.setLayout(layout)

        open_button = QPushButton("Open", self.file_operations_widget)
        open_button.clicked.connect(self.open_selected_file)
        layout.addWidget(open_button)

        delete_button = QPushButton("Delete", self.file_operations_widget)
        delete_button.clicked.connect(self.delete_selected_file)
        layout.addWidget(delete_button)

        rename_button = QPushButton("Rename", self.file_operations_widget)
        rename_button.clicked.connect(self.rename_selected_file)
        layout.addWidget(rename_button)

        create_folder_button = QPushButton("Create Folder", self.file_operations_widget)
        create_folder_button.clicked.connect(self.create_folder)
        layout.addWidget(create_folder_button)

        file_properties_button = QPushButton("File Properties", self.file_operations_widget)
        file_properties_button.clicked.connect(self.show_file_properties)
        layout.addWidget(file_properties_button)

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

    def rename_selected_file(self):
        selected_index = self.tree_view.selectedIndexes()[0]
        file_path = self.model.filePath(selected_index)
        if not os.path.exists(file_path):
            return

        new_name, ok = QInputDialog.getText(self, "Rename File/Directory", "New Name:", QLineEdit.Normal, os.path.basename(file_path))
        if ok and new_name:
            new_path = os.path.join(os.path.dirname(file_path), new_name)
            try:
                os.rename(file_path, new_path)
                self.model.rename(selected_index, new_path)
            except OSError as e:
                QMessageBox.warning(self, "Error", str(e))

    def create_folder(self):
        selected_index = self.tree_view.selectedIndexes()[0]
        directory_path = self.model.filePath(selected_index)
        if not os.path.isdir(directory_path):
            return

        folder_name, ok = QInputDialog.getText(self, "Create New Folder", "Folder Name:")
        if ok and folder_name:
            folder_path = os.path.join(directory_path, folder_name)
            try:
                os.mkdir(folder_path)
                self.model.mkdir(selected_index, folder_name)
            except OSError as e:
                QMessageBox.warning(self, "Error", str(e))

    def show_file_properties(self):
        selected_index = self.tree_view.selectedIndexes()[0]
        file_path = self.model.filePath(selected_index)
        if not os.path.exists(file_path):
            return

        file_properties = f"File Path: {file_path}\n"
        file_properties += f"Size: {os.path.getsize(file_path)} bytes\n"
        file_properties += f"Created: {os.path.getctime(file_path)}\n"
        file_properties += f"Last Modified: {os.path.getmtime(file_path)}"

        QMessageBox.information(self, "File Properties", file_properties)

    def open_file(self, index):
        file_path = self.model.filePath(index)
        if os.path.isfile(file_path):
            os.startfile(file_path)

    def change_disk(self, disk_path):
        self.tree_view.setRootIndex(self.model.index(disk_path))

    def show_disk_selection_dialog(self):
        selected_disk = QFileDialog.getExistingDirectory(self, "Select Disk")
        if selected_disk:
            self.change_disk(selected_disk)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    file_manager = FileManager()
    file_manager.show()

    # Optional: Show a disk selection dialog at startup
    # file_manager.show_disk_selection_dialog()

    sys.exit(app.exec_())
