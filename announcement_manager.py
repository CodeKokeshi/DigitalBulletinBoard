import sys
import os
import json
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

DATA_PATH = "static/data/data.json"
COMMENTS_PATH = "static/data/comments/comments.json"
IMAGE_PATH = "static/images/"


def load_json(path, default_data=None):
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as file:
            json.dump(default_data or {}, file, indent=4)
    with open(path, "r") as file:
        return json.load(file)


def save_json(path, data):
    with open(path, "w") as file:
        json.dump(data, file, indent=4)


class AnnouncementManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Announcement Manager")
        self.setGeometry(100, 100, 1280, 720)
        self.setStyleSheet("background-color: white;")

        self.data = load_json(DATA_PATH, {"important_announcements": [], "upcoming_deadlines_events": [], "milestones": []})
        self.comments = load_json(COMMENTS_PATH, {"comments": []})

        self.init_ui()

    def init_ui(self):
        main_layout = QHBoxLayout()

        # Sidebar for categories
        self.category_list = QListWidget()
        self.category_list.addItems(["Important", "Upcoming", "Milestones"])
        self.category_list.clicked.connect(self.load_announcements)
        main_layout.addWidget(self.category_list, 2)

        # Announcements list
        self.announcement_list = QListWidget()
        self.announcement_list.clicked.connect(self.load_announcement_details)
        main_layout.addWidget(self.announcement_list, 4)

        # Announcement details
        self.details_widget = QWidget()
        self.details_layout = QVBoxLayout(self.details_widget)

        # Title Input
        self.title_input = QLineEdit()
        self.details_layout.addWidget(QLabel("Title:"))
        self.details_layout.addWidget(self.title_input)

        # Link Input
        self.link_input = QLineEdit()
        self.details_layout.addWidget(QLabel("Link:"))
        self.details_layout.addWidget(self.link_input)

        # Date Input
        self.date_input = QDateEdit(calendarPopup=True)
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setStyleSheet("QDateEdit { color: black; } QCalendarWidget QToolButton { color: black; }")
        self.details_layout.addWidget(QLabel("Date:"))
        self.details_layout.addWidget(self.date_input)

        # Date Range Checkbox
        self.date_range_checkbox = QCheckBox("Date Range")
        self.date_range_checkbox.stateChanged.connect(self.toggle_date_range)
        self.details_layout.addWidget(QLabel("Date Range:"))
        self.details_layout.addWidget(self.date_range_checkbox)

        # End Date Input
        self.end_date_input = QDateEdit(calendarPopup=True)
        self.end_date_input.setDate(QDate.currentDate())
        self.end_date_input.setEnabled(False)
        self.end_date_input.setStyleSheet("QDateEdit { color: black; } QCalendarWidget QToolButton { color: black; }")
        self.details_layout.addWidget(QLabel("End Date:"))
        self.details_layout.addWidget(self.end_date_input)

        # Guest Mode Checkbox
        self.guest_checkbox = QCheckBox("Guest Mode")
        self.details_layout.addWidget(QLabel("Guest Mode:"))
        self.details_layout.addWidget(self.guest_checkbox)

        # Description Input
        self.description_input = QTextEdit()
        self.details_layout.addWidget(QLabel("Description:"))
        self.details_layout.addWidget(self.description_input)

        # Attach Image
        self.image_label = QLabel("No image selected")
        self.attach_image_btn = QPushButton("Attach Image")
        self.attach_image_btn.clicked.connect(self.attach_image)
        self.attach_image_btn.setStyleSheet("""
            QPushButton {
                background-color: #2980b9;
                color: white;
            }
            QPushButton:disabled {
                background-color: #7f8c8d;
                color: white;
            }
        """)
        image_layout = QHBoxLayout()
        image_layout.addWidget(self.image_label)
        image_layout.addWidget(self.attach_image_btn)
        self.details_layout.addLayout(image_layout)

        # Save and Delete Buttons
        self.save_btn = QPushButton("Save Changes")
        self.save_btn.setStyleSheet("background-color: #2980b9; color: white;")
        self.save_btn.clicked.connect(self.save_changes)
        self.delete_btn = QPushButton("Delete Announcement")
        self.delete_btn.setStyleSheet("background-color: #2980b9; color: white;")
        self.delete_btn.clicked.connect(self.delete_announcement)
        self.details_layout.addWidget(self.save_btn)
        self.details_layout.addWidget(self.delete_btn)

        # Comments Section
        self.comments_list = QListWidget()
        self.comments_list.setSelectionMode(QAbstractItemView.MultiSelection)
        self.details_layout.addWidget(QLabel("Comments:"))
        self.details_layout.addWidget(self.comments_list)

        self.delete_comments_btn = QPushButton("Delete Selected Comments")
        self.delete_comments_btn.setStyleSheet("background-color: #2980b9; color: white;")
        self.delete_comments_btn.clicked.connect(self.delete_comments)
        self.details_layout.addWidget(self.delete_comments_btn)

        main_layout.addWidget(self.details_widget, 6)

        # Main Widget
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # Disable editing fields initially
        self.set_editing_fields_enabled(False)

    def set_editing_fields_enabled(self, enabled, link=None):
        # If link is a Facebook share link, override enabled for specific fields
        if link and link.startswith(("http://", "https://")):
            self.title_input.setEnabled(enabled)
            self.link_input.setEnabled(enabled)
            self.date_input.setEnabled(enabled)
            self.date_range_checkbox.setEnabled(enabled)
            self.end_date_input.setEnabled(enabled)
            self.guest_checkbox.setEnabled(enabled)

            # Specifically disable these
            self.description_input.setEnabled(False)
            self.attach_image_btn.setEnabled(False)
        elif link and link.startswith("/announcement/"):
            # For internal announcements, enable all
            self.title_input.setEnabled(enabled)
            self.date_input.setEnabled(enabled)
            self.date_range_checkbox.setEnabled(enabled)
            self.end_date_input.setEnabled(enabled)
            self.guest_checkbox.setEnabled(enabled)
            self.description_input.setEnabled(enabled)
            self.attach_image_btn.setEnabled(enabled)
        else:
            # Default behavior for other links
            self.title_input.setEnabled(enabled)
            self.date_input.setEnabled(enabled)
            self.date_range_checkbox.setEnabled(enabled)
            self.end_date_input.setEnabled(enabled)
            self.guest_checkbox.setEnabled(enabled)
            self.description_input.setEnabled(enabled)
            self.attach_image_btn.setEnabled(enabled)

        # Continue with the rest of the original method
        self.save_btn.setEnabled(enabled)
        self.delete_btn.setEnabled(enabled)
        self.comments_list.setEnabled(enabled)
        self.delete_comments_btn.setEnabled(enabled)

        # Apply styles to buttons
        button_style = """
            QPushButton {
                background-color: #2980b9;
                color: white;
            }
            QPushButton:disabled {
                background-color: #7f8c8d;
                color: white;
            }
        """
        self.attach_image_btn.setStyleSheet(button_style)
        self.save_btn.setStyleSheet(button_style)
        self.delete_btn.setStyleSheet(button_style)
        self.delete_comments_btn.setStyleSheet(button_style)

    def clear_fields_when_unfocused(self):
        # gray out attach_image_btn, save_btn, delete_btn, delete_comments_btn
        self.attach_image_btn.setStyleSheet("background-color: #7f8c8d; color: white;")
        self.save_btn.setStyleSheet("background-color: #7f8c8d; color: white;")
        self.delete_btn.setStyleSheet("background-color: #7f8c8d; color: white;")
        self.delete_comments_btn.setStyleSheet("background-color: #7f8c8d; color: white;")

        # disable attach_image_btn, save_btn, delete_btn, delete_comments_btn
        self.attach_image_btn.setEnabled(False)
        self.save_btn.setEnabled(False)
        self.delete_btn.setEnabled(False)
        self.delete_comments_btn.setEnabled(False)

        # clear title, link, description, image_label
        self.title_input.clear()
        self.link_input.clear()
        self.description_input.clear()
        self.image_label.setText("No image selected")

        # disable title, link, date_input, date_range_checkbox, end_date_input, guest_checkbox, description_input
        self.title_input.setEnabled(False)
        self.link_input.setEnabled(False)
        self.date_input.setEnabled(False)
        self.date_range_checkbox.setEnabled(False)
        self.end_date_input.setEnabled(False)
        self.guest_checkbox.setEnabled(False)
        self.description_input.setEnabled(False)


    def toggle_date_range(self, state):
        self.end_date_input.setEnabled(state == Qt.Checked)

    def load_announcements(self):
        self.clear_fields_when_unfocused()  # Clear fields when a category is clicked
        self.announcement_list.clear()
        category = self.get_selected_category()
        if not category:
            return

        for announcement in self.data[category]:
            self.announcement_list.addItem(f"{announcement['announcement_id']} - {announcement['title']}")

    def load_announcement_details(self):
        self.clear_fields_when_unfocused()
        item = self.announcement_list.currentItem()
        if not item:
            self.set_editing_fields_enabled(False)
            return

        category = self.get_selected_category()
        if not category:
            self.set_editing_fields_enabled(False)
            return

        announcement_id = int(item.text().split(" - ")[0])
        for announcement in self.data[category]:
            if announcement["announcement_id"] == announcement_id:
                self.current_announcement = announcement
                self.title_input.setText(announcement.get("title", ""))
                self.link_input.setText(announcement.get("link", ""))
                self.date_input.setDate(QDate.fromString(announcement["date"].split(" - ")[0], "MMM dd, yyyy"))

                if " - " in announcement["date"]:
                    end_date = announcement["date"].split(" - ")[1]
                    self.end_date_input.setDate(QDate.fromString(end_date, "MMM dd, yyyy"))
                    self.date_range_checkbox.setChecked(True)
                else:
                    self.date_range_checkbox.setChecked(False)
                    self.end_date_input.setDate(QDate.currentDate())

                self.guest_checkbox.setChecked(announcement.get("guest_mode", False))

                # Check link conditions
                link = announcement.get("link", "")
                self.set_editing_fields_enabled(True, link)

                if link.startswith(("http://", "https://")) and not link.startswith("/announcement/"):
                    # Disable description and image attachment for external links
                    self.description_input.setEnabled(False)
                    self.attach_image_btn.setEnabled(False)
                    self.description_input.setText("")  # Clear description
                else:
                    # Enable description and image attachment for internal announcements or no link
                    self.description_input.setEnabled(True)
                    self.attach_image_btn.setEnabled(True)
                    self.description_input.setText(announcement.get("description", ""))

                self.image_label.setText(announcement.get("image_attachment", "No image selected"))

                self.load_comments(announcement_id)
                break
    def load_comments(self, announcement_id):
        self.comments_list.clear()
        for comment in self.comments["comments"]:
            if comment["announcement_id"] == announcement_id:
                self.comments_list.addItem(f"{comment['username']}: {comment['comment']} ({comment['date']})")

    def attach_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if file_path:
            file_extension = os.path.splitext(file_path)[-1]
            announcement_id = self.current_announcement["announcement_id"]
            new_path = os.path.join(IMAGE_PATH, f"{announcement_id}{file_extension}")
            os.makedirs(IMAGE_PATH, exist_ok=True)
            with open(file_path, "rb") as src, open(new_path, "wb") as dst:
                dst.write(src.read())
            self.image_label.setText(new_path.replace("static", ""))

    def save_changes(self):
        category = self.get_selected_category()
        if not category or not self.current_announcement:
            return

        self.current_announcement["title"] = self.title_input.text()
        self.current_announcement["link"] = self.link_input.text()
        self.current_announcement["guest_mode"] = self.guest_checkbox.isChecked()

        start_date = self.date_input.date().toString("MMM dd, yyyy")
        if self.date_range_checkbox.isChecked():
            end_date = self.end_date_input.date().toString("MMM dd, yyyy")
            start_year = self.date_input.date().year()
            end_year = self.end_date_input.date().year()
            if start_year == end_year:
                self.current_announcement["date"] = f"{self.date_input.date().toString('MMM dd')} - {end_date}"
            else:
                self.current_announcement["date"] = f"{start_date} - {end_date}"
            self.current_announcement["sorting_date"] = self.end_date_input.date().toString("MM/dd/yyyy")
        else:
            self.current_announcement["date"] = start_date
            self.current_announcement["sorting_date"] = self.date_input.date().toString("MM/dd/yyyy")

        if not self.current_announcement["link"].startswith("http://") and not self.current_announcement[
            "link"].startswith("https://"):
            self.current_announcement["description"] = self.description_input.toPlainText()
            self.current_announcement[
                "image_attachment"] = self.image_label.text() if self.image_label.text() != "No image selected" else None

        save_json(DATA_PATH, self.data)
        self.load_announcements()
        self.clear_fields_when_unfocused()  # Clear fields after saving changes

        # Show success message
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText("Changes saved successfully.")
        msg.setWindowTitle("Success")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

    def delete_announcement(self):
        category = self.get_selected_category()
        if not category or not self.current_announcement:
            return

        self.data[category].remove(self.current_announcement)
        save_json(DATA_PATH, self.data)
        self.load_announcements()
        self.clear_fields_when_unfocused()  # Clear fields after deleting an announcement

        # Show success message
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText("Announcement deleted successfully.")
        msg.setWindowTitle("Success")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

    def delete_comments(self):
        selected_comments = [item.text() for item in self.comments_list.selectedItems()]
        if not selected_comments:
            return

        self.comments["comments"] = [
            comment for comment in self.comments["comments"]
            if f"{comment['username']}: {comment['comment']} ({comment['date']})" not in selected_comments
        ]
        save_json(COMMENTS_PATH, self.comments)
        self.load_comments(self.current_announcement["announcement_id"])

    def get_selected_category(self):
        selected_item = self.category_list.currentItem()
        if not selected_item:
            return None
        return {
            "Important": "important_announcements",
            "Upcoming": "upcoming_deadlines_events",
            "Milestones": "milestones"
        }.get(selected_item.text(), None)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AnnouncementManager()
    window.show()
    sys.exit(app.exec_())