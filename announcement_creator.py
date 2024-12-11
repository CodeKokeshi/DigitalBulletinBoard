import sys
import os
import json
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from datetime import *

DATA_PATH = "static/data/data.json"
IMAGE_PATH = "static/images/"

# Load data.json
def load_data():
    if not os.path.exists(DATA_PATH):
        os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
        with open(DATA_PATH, "w") as file:
            json.dump({"important_announcements": [], "upcoming_deadlines_events": [], "milestones": []}, file)
    with open(DATA_PATH, "r") as file:
        return json.load(file)

# Save data to data.json
def save_data(data):
    with open(DATA_PATH, "w") as file:
        json.dump(data, file, indent=4)

class AnnouncementApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Announcement Creator")
        self.setGeometry(100, 100, 1280, 720)
        self.setStyleSheet("background-color: white;")

        # Main Widget and Layout
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self.layout = QVBoxLayout(self.main_widget)

        # Load existing data
        self.data = load_data()

        # Initialize form
        self.init_form()

    def init_form(self):
        form_layout = QFormLayout()

        # External Announcement Checkbox
        self.external_checkbox = QCheckBox("External Announcement")
        self.external_checkbox.stateChanged.connect(self.toggle_external)
        form_layout.addRow("External Announcement:", self.external_checkbox)

        # Link Field
        self.link_input = QLineEdit()
        self.link_input.setPlaceholderText("https://example.com/")
        self.link_input.setEnabled(False)
        form_layout.addRow("Link:", self.link_input)

        # Date Field
        self.date_input = QDateEdit(calendarPopup=True)
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setStyleSheet("QDateEdit { color: black; } QCalendarWidget QToolButton { color: black; }")
        form_layout.addRow("Date:", self.date_input)

        # Date Range Checkbox
        self.date_range_checkbox = QCheckBox("Date Range")
        self.date_range_checkbox.stateChanged.connect(self.toggle_date_range)
        form_layout.addRow("Date Range:", self.date_range_checkbox)

        # End Date Field
        self.end_date_input = QDateEdit(calendarPopup=True)
        self.end_date_input.setDate(QDate.currentDate())
        self.end_date_input.setEnabled(False)
        self.end_date_input.setStyleSheet("QDateEdit { color: black; } QCalendarWidget QToolButton { color: black; }")
        form_layout.addRow("End Date:", self.end_date_input)

        # Title Field
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Enter announcement title")
        form_layout.addRow("Title:", self.title_input)

        # Guest Mode Checkbox
        self.guest_checkbox = QCheckBox("Guest Mode")
        form_layout.addRow("Guest Mode:", self.guest_checkbox)

        # Description Field
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("Enter description")
        self.description_input.setEnabled(True)
        form_layout.addRow("Description:", self.description_input)

        # Category Dropdown
        self.category_dropdown = QComboBox()
        self.category_dropdown.addItems(["Important", "Upcoming", "Milestones"])
        self.category_dropdown.currentIndexChanged.connect(self.update_announcement_id)
        form_layout.addRow("Category:", self.category_dropdown)

        # Announcement ID Display
        self.announcement_id_label = QLabel("1")
        self.update_announcement_id()
        form_layout.addRow("Announcement ID:", self.announcement_id_label)

        # Image Attachment
        self.image_button = QPushButton("Attach Image")
        self.image_button.clicked.connect(self.attach_image)
        self.image_button.setStyleSheet("""
            QPushButton {
                background-color: #2980b9; 
                color: white;
            }
            QPushButton:disabled {
                background-color: #7f8c8d; 
                color: white;
            }
        """)
        self.image_button.setEnabled(True)
        self.image_path_label = QLabel("No image selected")
        image_layout = QHBoxLayout()
        image_layout.addWidget(self.image_button)
        image_layout.addWidget(self.image_path_label)
        form_layout.addRow("Image:", image_layout)

        # Submit Button
        self.submit_button = QPushButton("Submit")
        self.submit_button.setStyleSheet("background-color: #2980b9; color: white;")
        self.submit_button.clicked.connect(self.submit_announcement)
        form_layout.addRow(self.submit_button)

        # Add form layout to main layout
        self.layout.addLayout(form_layout)

    def toggle_external(self, state):
        is_external = state == Qt.Checked
        self.link_input.setEnabled(is_external)
        self.description_input.setEnabled(not is_external)
        self.image_button.setEnabled(not is_external)

    def toggle_date_range(self, state):
        is_range = state == Qt.Checked
        self.end_date_input.setEnabled(is_range)

    def update_announcement_id(self):
        category_index = self.category_dropdown.currentIndex() + 1
        current_category = ["important_announcements", "upcoming_deadlines_events", "milestones"][category_index - 1]
        current_data = self.data[current_category]
        base_id = category_index * 1000
        if current_data:
            max_id = max(item["announcement_id"] for item in current_data)
            next_id = max_id + 1
        else:
            next_id = base_id
        self.announcement_id_label.setText(str(next_id))

    def attach_image(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Select Image", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if file_path:
            announcement_id = self.announcement_id_label.text()
            file_extension = os.path.splitext(file_path)[-1]
            new_path = os.path.join(IMAGE_PATH, f"{announcement_id}{file_extension}")
            os.makedirs(IMAGE_PATH, exist_ok=True)
            with open(file_path, "rb") as src, open(new_path, "wb") as dst:
                dst.write(src.read())
            self.image_path_label.setText(new_path.replace("static", ""))

    def submit_announcement(self):
        if not self.validate_form():
            return

        category_index = self.category_dropdown.currentIndex()
        category_keys = ["important_announcements", "upcoming_deadlines_events", "milestones"]
        selected_category = category_keys[category_index]

        date = self.date_input.date().toString("MM/dd/yyyy")
        sorting_date = date
        if self.date_range_checkbox.isChecked():
            end_date = self.end_date_input.date().toString("MM/dd/yyyy")
            date = f"{date} - {end_date}"
            sorting_date = end_date

        announcement = {
            "link": self.link_input.text() if self.external_checkbox.isChecked() else f"/announcement/{self.announcement_id_label.text()}",
            "date": self.format_date(date),
            "title": self.title_input.text(),
            "guest_mode": self.guest_checkbox.isChecked(),
            "announcement_id": int(self.announcement_id_label.text()),
            "sorting_date": sorting_date,
            "likes": {
                "amount": 0,
                "accounts": []
            }
        }

        if not self.external_checkbox.isChecked():
            announcement["description"] = self.description_input.toPlainText()
        if self.image_path_label.text() != "No image selected":
            announcement["image_attachment"] = self.image_path_label.text()

        self.data[selected_category].append(announcement)
        save_data(self.data)
        self.clear_form()

        # Show success message
        success_msg = QMessageBox()
        success_msg.setIcon(QMessageBox.Information)
        success_msg.setText("Announcement created successfully.")
        success_msg.setWindowTitle("Success")
        success_msg.setStandardButtons(QMessageBox.Ok)
        success_msg.exec_()

    def validate_form(self):
        if not self.title_input.text().strip():
            self.show_error("Title cannot be empty.")
            return False
        if not self.date_input.text().strip():
            self.show_error("Date cannot be empty.")
            return False
        if not self.external_checkbox.isChecked() and not self.description_input.toPlainText().strip():
            self.show_error("Description cannot be empty.")
            return False
        return True

    def show_error(self, message):
        error_dialog = QMessageBox()
        error_dialog.setIcon(QMessageBox.Critical)
        error_dialog.setText(message)
        error_dialog.setWindowTitle("Error")
        error_dialog.exec_()

    def show_error(self, message):
        error_dialog = QMessageBox()
        error_dialog.setIcon(QMessageBox.Critical)
        error_dialog.setText(message)
        error_dialog.setWindowTitle("Error")
        error_dialog.exec_()

    def format_date(self, date_input):
        try:
            if "-" in date_input:
                start, end = date_input.split(" - ")
                start_date = datetime.strptime(start.strip(), "%m/%d/%Y")
                end_date = datetime.strptime(end.strip(), "%m/%d/%Y")
                if start_date.year == end_date.year:
                    return f"{start_date.strftime('%b %d')} - {end_date.strftime('%b %d, %Y')}"
                return f"{start_date.strftime('%b %d, %Y')} - {end_date.strftime('%b %d, %Y')}"
            date = datetime.strptime(date_input.strip(), "%m/%d/%Y")
            return date.strftime("%b %d, %Y")
        except ValueError:
            return date_input

    def clear_form(self):
        self.external_checkbox.setChecked(False)
        self.link_input.clear()
        self.date_input.setDate(QDate.currentDate())
        self.end_date_input.setDate(QDate.currentDate())
        self.end_date_input.setEnabled(False)
        self.date_range_checkbox.setChecked(False)
        self.title_input.clear()
        self.guest_checkbox.setChecked(False)
        self.description_input.clear()
        self.image_path_label.setText("No image selected")
        self.update_announcement_id()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AnnouncementApp()
    window.show()
    sys.exit(app.exec_())