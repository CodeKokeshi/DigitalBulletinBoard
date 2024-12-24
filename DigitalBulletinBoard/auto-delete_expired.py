import json
from datetime import datetime
import schedule
import time
import os
import shutil

DATA_FILE_PATH = 'static/data/data.json'
ARCHIVE_FILE_PATH = 'static/data/archived_data.json'
IMAGE_DIR = 'static/images/'
ARCHIVE_IMAGE_DIR = 'static/images/archived/'

def load_data(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def save_data(file_path, data):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)

def generate_new_archive_id(archive_data):
    max_id = 0
    for category in archive_data.values():
        for announcement in category:
            if announcement.get('archive_id', 0) > max_id:
                max_id = announcement['archive_id']
    return max_id + 1

def move_and_rename_image(announcement, archive_id):
    if 'image_attachment' in announcement:
        old_image_path = os.path.join(IMAGE_DIR, os.path.basename(announcement['image_attachment']))
        new_image_name = f"{archive_id}{os.path.splitext(old_image_path)[1]}"
        new_image_path = os.path.join(ARCHIVE_IMAGE_DIR, new_image_name)
        if os.path.exists(old_image_path):
            os.makedirs(ARCHIVE_IMAGE_DIR, exist_ok=True)
            shutil.move(old_image_path, new_image_path)
            announcement['image_attachment'] = f"/{new_image_path}"

def check_and_archive_expired_announcements():
    data = load_data(DATA_FILE_PATH)
    archive_data = load_data(ARCHIVE_FILE_PATH)
    current_date = datetime.now().date()  # Convert to date object for comparison

    if 'important_announcements' not in archive_data:
        archive_data['important_announcements'] = []

    expired_announcements = []
    for category in data:
        if category == "milestones":
            continue  # Skip archiving for milestones

        announcements_to_keep = []
        for announcement in data[category]:
            if datetime.strptime(announcement['sorting_date'], '%m/%d/%Y').date() < current_date:
                archive_id = generate_new_archive_id(archive_data)
                announcement['archive_id'] = archive_id
                move_and_rename_image(announcement, archive_id)
                expired_announcements.append(announcement)
                # Update archive data to ensure unique IDs in subsequent iterations
                archive_data['important_announcements'].append(announcement)
            else:
                announcements_to_keep.append(announcement)

        data[category] = announcements_to_keep

    save_data(DATA_FILE_PATH, data)
    save_data(ARCHIVE_FILE_PATH, archive_data)
    print(f"Checked and archived expired announcements at {current_date}")

# Check expired announcements at startup
check_and_archive_expired_announcements()

# Schedule the check to run every hour
schedule.every().hour.do(check_and_archive_expired_announcements)

if __name__ == "__main__":
    while True:
        schedule.run_pending()
        time.sleep(1)