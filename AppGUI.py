import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,\
                            QLabel, QLineEdit, QPushButton, QDateTimeEdit, QFileDialog, QStyleFactory
from PyQt6.QtCore import QDateTime, Qt
from PyQt6.QtGui import QPalette, QColor
from ReadLogs import ReadLogs


class LogViewer(QMainWindow):
    def __init__(self, read_logs):
        super().__init__()

        self.read_logs = read_logs

        # Tworzę okno aplikacji
        self.setWindowTitle("Log browser")
        self.setMinimumWidth(800)

        # Dodaję centralny widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Tworzę wertykalny main_layout
        self.main_layout = QVBoxLayout(self.central_widget)

        # Tworzę horyzontalny top_layout dla wczytywania pliku
        self.top_layout = QHBoxLayout()
        self.file_path_label = QLineEdit()
        self.file_path_label.setReadOnly(True)
        self.top_layout.addWidget(self.file_path_label)

        self.load_button = QPushButton("Load_file")
        self.load_button.clicked.connect(self.load_logs)
        self.top_layout.addWidget(self.load_button)

        self.main_layout.addLayout(self.top_layout)

        # Tworzę horyzontalny middle_layout
        self.middle_layout = QHBoxLayout()
        self.main_layout.addLayout(self.middle_layout)

        # Tworzę wertykalny left_layout i dodaję do middle_layout
        self.left_layout = QVBoxLayout()
        self.middle_layout.addLayout(self.left_layout)

        # Tworzę filtry dla logów jako horyzontalny layout
        self.filter_layout = QHBoxLayout()
        self.start_datetime = QDateTimeEdit()
        self.start_datetime.setDisplayFormat("MMM dd hh:mm:ss")
        self.start_datetime.setDateTime(QDateTime.currentDateTime())
        self.filter_layout.addWidget(self.start_datetime)

        self.end_datetime = QDateTimeEdit()
        self.end_datetime.setDisplayFormat("MMM dd hh:mm:ss")
        self.end_datetime.setDateTime(QDateTime.currentDateTime())
        self.filter_layout.addWidget(self.end_datetime)

        self.left_layout.addLayout(self.filter_layout)

        # Tworzę przycisk do filtrowania logów
        self.filter_button = QPushButton("Filter")
        self.filter_button.clicked.connect(self.filter_logs)

        self.left_layout.addWidget(self.filter_button)

        # Tworzę listę logów do przeglądania
        self.logs_list = QListWidget()
        self.logs_list.itemSelectionChanged.connect(self.show_log_details)
        self.left_layout.addWidget(self.logs_list)

        # Tworzę wertykalny right_layout
        self.right_layout = QVBoxLayout()
        self.middle_layout.addLayout(self.right_layout)

        # Dodaję wszystkie potrzebne informacje jako widgety do right_layout
        self.log_details_label = QLabel("Selected log details")
        self.log_details_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.log_details_label.setStyleSheet("font-weight: bold;")
        self.right_layout.addWidget(self.log_details_label)

        self.host_label = QLabel("Host name:")
        self.right_layout.addWidget(self.host_label)
        self.host_view = QLineEdit()
        self.host_view.setReadOnly(True)
        self.right_layout.addWidget(self.host_view)

        self.date_label = QLabel("Date: ")
        self.right_layout.addWidget(self.date_label)
        self.date_view = QLineEdit()
        self.date_view.setReadOnly(True)
        self.right_layout.addWidget(self.date_view)

        self.endpoint_label = QLabel("Application: ")
        self.right_layout.addWidget(self.endpoint_label)
        self.endpoint_view = QLineEdit()
        self.endpoint_view.setReadOnly(True)
        self.right_layout.addWidget(self.endpoint_view)

        self.response_label = QLabel("Pid number: ")
        self.right_layout.addWidget(self.response_label)
        self.response_view = QLineEdit()
        self.response_view.setReadOnly(True)
        self.right_layout.addWidget(self.response_view)

        self.size_label = QLabel("Message: ")
        self.right_layout.addWidget(self.size_label)
        self.size_view = QLineEdit()
        self.size_view.setReadOnly(True)
        self.right_layout.addWidget(self.size_view)

        # Tworzę horyzontalny bottom_layout
        self.bottom_layout = QHBoxLayout()
        self.main_layout.addLayout(self.bottom_layout)

        # Tworzę przyciski next i previous
        self.prev_button = QPushButton("Previous")
        self.prev_button.clicked.connect(self.prev_log)
        self.prev_button.setEnabled(False)
        self.bottom_layout.addWidget(self.prev_button)

        self.next_button = QPushButton("Next")
        self.next_button.clicked.connect(self.next_log)
        self.next_button.setEnabled(False)
        self.bottom_layout.addWidget(self.next_button)

        self.all_logs = []

    def load_logs(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open log file", "", "Log files (*.log *.txt)")
        if file_name:
            logs = self.read_logs.read(file_name)
            self.file_path_label.setText(file_name)
            self.all_logs = logs
            self.update_logs_list(logs)

    def update_logs_list(self, logs):
        self.logs_list.clear()
        for log in logs:
            short_log = log[:60] + "..." if len(log) > 55 else log
            item = QListWidgetItem(short_log)
            item.full_log = log
            self.logs_list.addItem(item)

    def show_log_details(self):
        selected_items = self.logs_list.selectedItems()
        if selected_items:
            log = selected_items[0].full_log
            log_details = self.read_logs.parse_log(log)
            self.host_view.setText(log_details["hostname"])
            self.date_view.setText(log_details["timestamp"])
            self.endpoint_view.setText(log_details["application"])
            self.response_view.setText(log_details["pid_number"])
            self.size_view.setText(log_details["message"])
            self.update_nav_buttons()

    def filter_logs(self):
        start_datetime = self.start_datetime.dateTime().toString("MMM dd hh:mm:ss")
        end_datetime = self.end_datetime.dateTime().toString("MMM dd hh:mm:ss")
        filtered_logs = self.read_logs.filter_logs(self.all_logs, start_datetime, end_datetime)
        self.update_logs_list(filtered_logs)

    def update_nav_buttons(self):
        current_row = self.logs_list.currentRow()
        self.prev_button.setEnabled(current_row > 0)
        self.next_button.setEnabled(current_row < self.logs_list.count() - 1)

    def prev_log(self):
        current_row = self.logs_list.currentRow()
        if current_row > 0:
            self.logs_list.setCurrentRow(current_row - 1)

    def next_log(self):
        current_row = self.logs_list.currentRow()
        if current_row < self.logs_list.count() - 1:
            self.logs_list.setCurrentRow(current_row + 1)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle(QStyleFactory.create("Fusion"))
    dark_palette = QPalette()
    dark_palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
    dark_palette.setColor(QPalette.ColorRole.Base, QColor(35, 35, 35))
    dark_palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.white)
    dark_palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
    dark_palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
    dark_palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
    dark_palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
    dark_palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.black)
    app.setPalette(dark_palette)
    viewer = LogViewer(ReadLogs())
    viewer.show()
    sys.exit(app.exec())
