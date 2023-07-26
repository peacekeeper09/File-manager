import os
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTreeView, QFileSystemModel, QDockWidget, QPushButton, QWidget, QVBoxLayout, QMessageBox, QFileDialog, QLineEdit, QInputDialog, QAction, QMenu, QToolBar, QListView


class FileManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("File Manager")
        self.setGeometry(100, 100, 800, 600)

        self.file_system_model = QFileSystemModel()
        self.file_system_model.setRootPath("")
        self.current_path = os.path.expanduser("~")

        self.tree_view = QTreeView(self)
        self.tree_view.setModel(self.file_system_model)
        self.tree_view.setRootIndex(self.file_system_model.index(self.current_path))
        self.tree_view.doubleClicked.connect(self.open_file)

        self.icon_view = QListView(self)
        self.icon_view.setViewMode(QListView.IconMode)
        self.icon_view.setModel(self.file_system_model)
        self.icon_view.setRootIndex(self.file_system_model.index(self.current_path))
        self.icon_view.doubleClicked.connect(self.open_file)

        self.setCentralWidget(self.tree_view)

        self.dock = QDockWidget("File Operations", self)
        self.addDockWidget(1, self.dock)

        self.file_operations_widget = QWidget(self.dock)
        self.dock.setWidget(self.file_operations_widget)

        self.init_file_operations()

        self.select_disk_button = QPushButton("Select Disk", self)
        self.select_disk_button.clicked.connect(self.show_disk_selection_dialog)
        self.statusBar().addWidget(self.select_disk_button)

        self.create_menu_bar_and_toolbar()

    def create_menu_bar_and_toolbar(self):
        # File Menu
        file_menu = self.menuBar().addMenu("File")

        open_action = QAction("Open", self)
        open_action.triggered.connect(self.open_selected_file)
        file_menu.addAction(open_action)

        delete_action = QAction("Delete", self)
        delete_action.triggered.connect(self.delete_selected_file)
        file_menu.addAction(delete_action)

        rename_action = QAction("Rename", self)
        rename_action.triggered.connect(self.rename_selected_file)
        file_menu.addAction(rename_action)

        create_folder_action = QAction("Create Folder", self)
        create_folder_action.triggered.connect(self.create_folder)
        file_menu.addAction(create_folder_action)

        file_menu.addSeparator()

        properties_action = QAction("File Properties", self)
        properties_action.triggered.connect(self.show_file_properties)
        file_menu.addAction(properties_action)

        # View Menu
        view_menu = self.menuBar().addMenu("View")

        tree_view_action = QAction("Tree View", self)
        tree_view_action.triggered.connect(self.show_tree_view)
        view_menu.addAction(tree_view_action)

        icon_view_action = QAction("Icon View", self)
        icon_view_action.triggered.connect(self.show_icon_view)
        view_menu.addAction(icon_view_action)

        # Toolbar
        toolbar = QToolBar("Toolbar", self)
        self.addToolBar(toolbar)

        toolbar.addAction(open_action)
        toolbar.addAction(delete_action)
        toolbar.addAction(rename_action)
        toolbar.addAction(create_folder_action)

    def init_file_operations(self):
        layout = QVBoxLayout()
        self.file_operations_widget.setLayout(layout)

        # Buttons for common file operations (same as menu actions)
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
        file_path = self.file_system_model.filePath(selected_index)
        if os.path.isfile(file_path):
            os.startfile(file_path)

    def delete_selected_file(self):
        selected_indexes = self.tree_view.selectedIndexes()
        if not selected_indexes:
            return

        selected_index = selected_indexes[0]
        file_path = self.file_system_model.filePath(selected_index)

        if os.path.isfile(file_path):
            confirmation = QMessageBox.question(self, "Confirm Deletion",
                                                f"Are you sure you want to delete {file_path}?",
                                                QMessageBox.Yes | QMessageBox.No)
            if confirmation == QMessageBox.Yes:
                os.remove(file_path)
                self.file_system_model.remove(selected_index)

    def rename_selected_file(self):
        selected_indexes = self.tree_view.selectedIndexes()
        if not selected_indexes:
            return

        selected_index = selected_indexes[0]
        file_path = self.file_system_model.filePath(selected_index)

        if not os.path.exists(file_path):
            return

        new_name, ok = QInputDialog.getText(self, "Rename File/Directory", "New Name:", QLineEdit.Normal, os.path.basename(file_path))
        if ok and new_name:
            new_path = os.path.join(os.path.dirname(file_path), new_name)
            try:
                os.rename(file_path, new_path)
                self.file_system_model.rename(selected_index, new_path)
            except OSError as e:
                QMessageBox.warning(self, "Error", str(e))

    def create_folder(self):
        selected_indexes = self.tree_view.selectedIndexes()
        if not selected_indexes:
            return

        selected_index = selected_indexes[0]
        directory_path = self.file_system_model.filePath(selected_index)

        if not os.path.isdir(directory_path):
            return

        folder_name, ok = QInputDialog.getText(self, "Create New Folder", "Folder Name:")
        if ok and folder_name:
            folder_path = os.path.join(directory_path, folder_name)
            try:
                os.mkdir(folder_path)
                self.file_system_model.mkdir(selected_index, folder_name)
            except OSError as e:
                QMessageBox.warning(self, "Error", str(e))

    def show_file_properties(self):
        selected_indexes = self.tree_view.selectedIndexes()
        if not selected_indexes:
            return

        selected_index = selected_indexes[0]
        file_path = self.file_system_model.filePath(selected_index)

        if not os.path.exists(file_path):
            return

        file_properties = f"File Path: {file_path}\n"
        file_properties += f"Size: {os.path.getsize(file_path)} bytes\n"
        file_properties += f"Created: {os.path.getctime(file_path)}\n"
        file_properties += f"Last Modified: {os.path.getmtime(file_path)}"

        QMessageBox.information(self, "File Properties", file_properties)

    def open_file(self, index):
        file_path = self.file_system_model.filePath(index)
        if os.path.isfile(file_path):
            os.startfile(file_path)

    def change_disk(self, disk_path):
        self.current_path = disk_path
        self.tree_view.setRootIndex(self.file_system_model.index(self.current_path))
        self.icon_view.setRootIndex(self.file_system_model.index(self.current_path))

    def show_disk_selection_dialog(self):
        selected_disk = QFileDialog.getExistingDirectory(self, "Select Disk")
        if selected_disk:
            self.change_disk(selected_disk)

    def show_tree_view(self):
        self.setCentralWidget(self.tree_view)

    def show_icon_view(self):
        self.setCentralWidget(self.icon_view)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    file_manager = FileManager()
    file_manager.show()

    sys.exit(app.exec_())
