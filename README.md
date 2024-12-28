# Digital Bulletin Board 📋

The **Digital Bulletin Board** is a web-based system designed to display school announcements. It categorizes announcements into three editable sections: **Important**, **Upcoming**, and **Milestones**. This system offers features for both administrators and users.

## Features ✨

### Website Operation 🌐

1. **Guest View:**
   - View announcements marked as `guest_mode = true`.
   - Limited interaction (no likes or comments).
   - Redirects based on login status.

2. **Signup Process:**
   - Register with full name, age, email, and password.
   - Email verification ensures valid accounts.

3. **Logged-In User Features:**
   - Comment, like, and view archived announcements.
   - Submit feedback.
   - Filter and sort announcements.

4. **Error Handling:**
   - Unauthorized access gets a "Not Authorized" page.
   - Invalid links display a custom 404 error.

### Admin Features 🔧

1. **Dashboard:**
   - Tracks active users, announcements, and feedback.

2. **Management Tools:**
   - Create, manage, and edit announcements.
   - Oversee user accounts.

## Setup Guide 🛠️

### File Overview 📁
- **main.py**: Backend server implementation.
- **auto-delete_expired.py**: Handles archiving expired announcements.

### Database Setup 💾
1. Create the following table in your MySQL database:
   ```sql
   CREATE TABLE users (
       id INT NOT NULL AUTO_INCREMENT,
       full_name VARCHAR(255) NOT NULL,
       age INT NOT NULL,
       email VARCHAR(255) NOT NULL UNIQUE,
       password VARCHAR(255) NOT NULL,
       PRIMARY KEY (id)
   );
   ```
2. Ensure your MySQL server is running and accessible.

### `supersecret.json` Setup 🔐
1. Create a `supersecret.json` file in the `DigitalBulletinBoard/super_secret_stuff` directory.
2. Use the following structure:
   ```json
   {
     "verification": [
       {
         "email_sender": "your_email_here",
         "password": "app_password_here"
       }
     ],
     "SuperSecret": [
       {
         "SuperSecretKey": "your_secret_key"
       }
     ],
     "Database_Stuff": [
       {
         "host": "localhost",
         "user": "root",
         "password": "your_mysql_password",
         "port": "3306",
         "database": "your_database_name"
       }
     ]
   }
   ```
3. Replace placeholders with actual credentials.

### Folder Notes 🗂️
- **Images Folder** (`DigitalBulletinBoard/static/images`): Store announcement images, feedback attachments, and archived images.
- **Data Folder** (`DigitalBulletinBoard/static/data`): Automatically generated during announcement creation. Do not modify.

### License 📜
This project uses the **GPL 3 License**.

## Installation 🚀

1. Clone the repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up the database and `supersecret.json` file.
4. Run the backend server:
   ```bash
   python main.py
   ```
5. Access the web application at `http://localhost:8000`.

## Contributing 🤝

Contributions are welcome! To contribute:
1. Fork the repository.
2. Create a new branch for your feature or bugfix.
3. Commit your changes and push the branch.
4. Submit a pull request.

