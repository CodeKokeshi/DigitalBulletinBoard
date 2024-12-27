# Digital Bulletin Board

The **Digital Bulletin Board** is a web-based system designed to display school announcements. It categorizes announcements into three editable sections: **Important**, **Upcoming**, and **Milestones**. The project provides an efficient way to manage and view announcements, with features tailored for both administrators and users.

## Features

### Website Operation:

1. **Guest View:**
   - When accessing the site, visitors land on the guest view.
   - The navigation bar includes options for filtering announcements, logging in, and signing up.
   - Only announcements with `guest_mode = true` are visible, ensuring restricted content for guests.
   - The Milestones category is hidden in guest mode.
   - Clicking the logo redirects users to either the guest mode homepage or the user homepage (if logged in).

2. **Announcement Details:**
   - Guests can view announcement details and comments but cannot interact (e.g., like or comment).

3. **Signup Process:**
   - Guests can register by providing their full name, age, email, and password, and agreeing to terms and conditions.
   - A verification code is sent to the provided email to confirm its validity.

4. **Logged-In User Features:**
   - Logged-in users can:
     - Comment and like announcements.
     - View archived announcements.
     - Submit feedback.
     - Sort announcements by deadline proximity.
     - Filter announcements based on keywords or dates.

5. **Error Handling:**
   - Unauthorized access redirects to a dedicated "Not Authorized" page.
   - Non-existent links return a custom 404 error page.

### Admin Features:

1. **Dashboard:**
   - Displays:
     - Number of active users.
     - Total users (including offline users).
     - Total archived announcements.
     - Total announcements.
     - Unread feedback count.

2. **Management Tools:**
   - Interfaces for system settings, announcement creation, management, and editing.
   - User account management.

### Current Progress:

- **Frontend:**
  - Implemented with HTML, CSS, JavaScript, and Bootstrap for a responsive design.

- **Backend:**
  - FastAPI-based server architecture.
  - Uses Python libraries like `mysql-connector`, `pydantic`, `cryptography`, `mimes`, and `multiparts`.
  - Credentials (signups and logins) are stored in MySQL.
  - Announcements are currently stored in JSON, with plans to transition to NoSQL in the future.

### Planned Enhancements:
- Transition announcement storage to a NoSQL database.
- Further refine admin interfaces.

## Installation and Setup

Currently, the setup process is incomplete. Instructions will be provided once the system becomes fully operational.

## Contributing

Contributions are welcome! To contribute:
1. Fork the repository.
2. Create a new branch for your feature or bugfix.
3. Commit your changes and push the branch.
4. Submit a pull request.
