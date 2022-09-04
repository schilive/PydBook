from PySide6 import QtCore, QtWidgets, QtGui

# Constants
APP_TITLE = "PydBook"  # Name of the application, on the titles of the windows, for example.


class MainUI(QtWidgets.QMainWindow):
    """This is the main UI, which is the one shown when the app is started, and whereof everything else is son."""

    def __init__(self):
        super().__init__()

        # Application Variables

        self.isSaveFile: bool = False  # Whether there is a saving file
        self.save_file: str = ""

        self.saved: bool = True  # Whether the current text has been saved, or whether it is blank.
        self.saved_text: str = ""  # This is a bad solution, better would be to save the changes done

        # UI Settings
        self.setWindowTitle(f"Untitled — {APP_TITLE}")

        stylesheet_file = "./style/main.stylesheet"

        with open(stylesheet_file) as file:
            self.setStyleSheet(file.read())

        # UI Widgets

        self.text_editor = QtWidgets.QPlainTextEdit()
        self.text_editor.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.text_editor.textChanged.connect(self.text_changed)
        self.setCentralWidget(self.text_editor)

        # Menu Bar

        self.menuBar_file = self.menuBar().addMenu("&File")
        self.menuBar_file.setWindowFlags(self.menuBar_file.windowFlags() | QtCore.Qt.NoDropShadowWindowHint)

        self.open_action = QtGui.QAction("&Open")
        self.open_action.setShortcut("Ctrl+O")
        self.open_action.triggered.connect(self.open)
        self.menuBar_file.addAction(self.open_action)

        self.menuBar_file.addSeparator()

        self.save_action = QtGui.QAction("&Save")
        self.save_action.setShortcut("Ctrl+S")
        self.save_action.triggered.connect(self.user_save)
        self.menuBar_file.addAction(self.save_action)

        self.save_as_action = QtGui.QAction("Save &As")
        self.save_as_action.setShortcut("Ctrl+Shift+S")
        self.save_as_action.triggered.connect(self.save_as)
        self.menuBar_file.addAction(self.save_as_action)

        self.menuBar_file.addSeparator()

        self.exit_action = QtGui.QAction("E&xit")
        self.exit_action.setShortcut("Ctrl+E")
        self.exit_action.triggered.connect(self.exit)
        self.menuBar_file.addAction(self.exit_action)

        # Status Bar

        self.statusBar = QtWidgets.QStatusBar()
        self.setStatusBar(self.statusBar)

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        self.exit()

    def text_changed(self):
        """Called when the text, of 'self.text_editor', changes."""

        if self.text_editor.toPlainText() != self.saved_text:
            self.saved = False

            if self.isSaveFile:
                file_name = self.save_file.split("/")[-1]
                self.setWindowTitle(f"{file_name}* — {APP_TITLE}")
            else:
                self.setWindowTitle(f"Untitled* — {APP_TITLE}")
        else:
            self.saved = True

            if self.isSaveFile:
                file_name = self.save_file.split("/")[-1]
                self.setWindowTitle(f"{file_name} — {APP_TITLE}")
            else:
                self.setWindowTitle(f"Untitled — {APP_TITLE}")

    def set_saving_file(self, file_src: str):
        """Called when saved or a file is opened. It updates whether the application has a file it can save to."""

        self.isSaveFile = True
        self.save_file = file_src
        self.saved_text = self.text_editor.toPlainText()
        self.saved = True

        file_name = file_src.split("/")[-1]
        self.setWindowTitle(f"{file_name} — {APP_TITLE}")

    def ask_if_wants_to_save(self, second_text: str = "") -> int:
        """This is called for the user to decide whether they want to save the file, before some other action;
        for example, opening a file. The variable 'second_text' adds a text to enlight the user. Returns the pressed
        button (Yes, No, Cancel), and 0 if unsuccessful."""

        # Building the Asking Box

        asking_box = QtWidgets.QMessageBox(self)
        asking_box.setWindowModality(QtCore.Qt.WindowModal)
        asking_box.setWindowTitle(APP_TITLE)

        warning_icon = QtWidgets.QMessageBox.Warning
        asking_box.setIcon(warning_icon)

        cancel_button = QtWidgets.QMessageBox.Cancel
        not_save_button = QtWidgets.QMessageBox.No
        save_button = QtWidgets.QMessageBox.Yes
        asking_box.setStandardButtons(cancel_button | not_save_button | save_button)

        asking_text: str
        if self.isSaveFile:
            save_file_name = self.save_file.split("/")[-1]
            asking_text = f"Would you like to save {save_file_name}?"
        else:
            asking_text = "Would you like to save this file?"

        asking_text += second_text
        asking_box.setText(asking_text)

        # Asking and Interpreting

        pressed_button = asking_box.exec()  # Returns 0 if unsuccessful
        return pressed_button

    def save_warn_if_needed(second_text: str = ""):
        """This is a decorator with the attribute 'second_text'. If the text has not been saved, tt asks if the user
        wants to save the file before an action, which is the function the decorator wraps.

        The attribute is directly concatenated to the asker box. If the user refuses, the action will continue normally;
        if the user accepts, they will be asked to save the file and, then, the action will continue normally; if they
        somehow cancel, nothing shall happen."""

        def decorator(func):
            def wrapper(self, *args, **kwargs):
                if not self.saved:
                    user_will = self.ask_if_wants_to_save(second_text)

                    if user_will == 0 or user_will == QtWidgets.QMessageBox.Cancel:  # Canceled
                        return
                    elif user_will == QtWidgets.QMessageBox.No:  # Not save
                        func(self, *args, **kwargs)
                    elif user_will == QtWidgets.QMessageBox.Yes:  # Wants to save
                        self.user_save()
                        func(self, *args, **kwargs)
                else:
                    func(self, *args, **kwargs)
            return wrapper
        return decorator

    @save_warn_if_needed(" Before opening a file..")
    def open(self):
        """Called for the user to open a file, altering the text to the text in the selected file, using UTF-8."""

        # File Selection

        file_selector = QtWidgets.QFileDialog(self)
        file_selector.setFileMode(QtWidgets.QFileDialog.ExistingFile)  # Only one file is to be selected

        file_selector.setLabelText(file_selector.Accept, "Open")
        file_selector.setLabelText(file_selector.Reject, "Close")
        file_selector.setLabelText(file_selector.FileName, "Name:")
        file_selector.setLabelText(file_selector.LookIn, "Look in:")
        file_selector.setLabelText(file_selector.FileType, "Type:")

        file_selector.setWindowTitle("Open a File")
        text_filter: str = "Text File (*.txt)"
        any_file_filter: str = "Any File (*)"
        file_selector.setNameFilter(f"{text_filter};;{any_file_filter}")  # Filters are separated by ;;

        result = file_selector.exec()  # Returns 1 if file was selected, 0 otherwise; for example, 'cancel' is pressed

        # Interpretation of the File Selection

        if result == 0:
            return

        file_selected: str = file_selector.selectedFiles()[0]  # As only one file can be selected

        try:
            file = open(file_selected, "r", encoding="utf-8")
            text = file.read()
        except Exception:
            warning_box = WarningMessage(self, text=f"{APP_TITLE} could not open the file: {file_selected}.")
            warning_box.exec()
            return
        else:
            file.close()
            self.text_editor.setPlainText(text)

            self.set_saving_file(file_selected)

    def user_save(self):
        """Called when the users want to 'save' the text."""

        if not self.isSaveFile:
            self.save_as()
        else:
            self.save(self.save_file)

    def save_as(self):
        """Called when the user presses 'save as' button. It asks the user to select a file, where the text shall be
        saved, using UTF-8."""

        # File Selector Widget

        file_selector = QtWidgets.QFileDialog(self)
        file_selector.setFileMode(QtWidgets.QFileDialog.AnyFile)  # Only one file is to be selected, existing or not

        file_selector.setLabelText(file_selector.Accept, "Save")
        file_selector.setLabelText(file_selector.Reject, "Close")
        file_selector.setLabelText(file_selector.FileName, "Name:")
        file_selector.setLabelText(file_selector.LookIn, "Look in:")
        file_selector.setLabelText(file_selector.FileType, "Type:")

        file_selector.setWindowTitle("Save As")
        text_filter: str = "Text File (*.txt)"
        any_file_filter: str = "Any File (*)"
        file_selector.setNameFilter(f"{text_filter};;{any_file_filter}")  # Filter are separated by ;;
        file_selector.setViewMode(QtWidgets.QFileDialog.List)

        # File Selection

        result = file_selector.exec()  # Returns 1 if file was selected, 0 otherwise; for example, 'cancel' is pressed

        if result == 0:
            return

        files_selected: list[str] = file_selector.selectedFiles()
        filter_selected: str = file_selector.selectedNameFilter()
        file_src: str = files_selected[0]  # As only one file can be selected

        if filter_selected == text_filter:
            file_name = file_src.split("/")[-1]

            if file_name.endswith(".txt"):
                saving_file = file_src
            else:
                saving_file = file_src + ".txt"
        else:  # filter_selected == any_file_filter:
            saving_file = file_src

        self.save(saving_file)

    def save(self, file_src):
        """It saves the text in the file 'file_src'."""

        try:
            file = open(file_src, "w", encoding="utf-8")
            text = self.text_editor.toPlainText()
            file.write(text)
        except Exception:
            warning_text = f"{APP_TITLE} could not save the text at {file_src}."
            warning_box = WarningMessage(self, text=warning_text)
            warning_box.exec()
        else:
            file.close()
            self.set_saving_file(file_src)

    @save_warn_if_needed(" Before closing.")
    def exit(self):
        self.close()


class WarningMessage(QtWidgets.QMessageBox):
    """This class is called when a warning is needed. As contrast with the ErrorMessage class, this message box
    do not intend to close the program: it is mostly to warn the user. It is only called inside the MainUI class."""

    def __init__(self, parent=None, text=""):
        super().__init__(parent=parent)

        # UI Settings

        self.setWindowModality(QtCore.Qt.WindowModal)
        self.setWindowTitle(APP_TITLE)

        warning_icon = QtWidgets.QMessageBox.Warning
        self.setIcon(warning_icon)

        warning_text = text
        self.setText(warning_text)


class ErrorMessage(QtWidgets.QMessageBox):
    """This class is called when a critical error happens. After its button is clicked, or it is closed, its parent
    is closed. Normally, the parent is MainUI, except for when an instance of MainUI is being formed."""

    def __init__(self, parent=None, exception: Exception = None):
        super().__init__(parent=parent)

        # UI Settings

        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.setWindowTitle(APP_TITLE)

        error_icon = QtWidgets.QMessageBox.Critical
        self.setIcon(error_icon)

        error_text = "An exception was raised" + (f"\n{exception.__str__()}" if exception else "")
        self.setText(error_text)

    def end_all(self):
        """Called to end all the application"""

        if self.parent():  # If there is a parent
            self.parent().close()
        else:
            self.close()

    def exec(self) -> None:
        """Executes normally, with the addition that, afterwards, it calls the 'end_all()' function."""

        super().exec()
        self.end_all()


def main():
    app = QtWidgets.QApplication([])

    try:
        ui = MainUI()
    except Exception as ex:
        error_box = ErrorMessage(exception=ex)
        error_box.exec()
        raise ex
    else:
        ui.resize(800, 600)
        ui.show()

    app.exec()


if __name__ == "__main__":
    main()
