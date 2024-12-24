from fastapi import FastAPI, Request, Depends, HTTPException, status, Form, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from starlette.middleware.sessions import SessionMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
from datetime import datetime
from itsdangerous import URLSafeTimedSerializer

import hashlib
import uvicorn
import logging
import mysql.connector
import os
import json
import smtplib
import random
import asyncio

# This contains very sensitive information and configuration details that should not be shared.
SUPER_SECRET_FILE = os.path.join("super_secret_stuff", "supersecret.json")

# Just loads the json file for database and other stuff.
def load_super_secret(file_path):
    with open(file_path, "r") as file:
        return json.load(file)

# Continuing what was said above, this is necessary for:
# Sending verification codes, Initializing Database and tracking User Sessions.
super_secret_data = load_super_secret(SUPER_SECRET_FILE)

# As you can see here, we use the super secret file to get the email address and password.
EMAIL_ADDRESS = super_secret_data["verification"][0]["email_sender"]
EMAIL_PASSWORD = super_secret_data["verification"][0]["password"]

# This is a dictionary that will store the verification codes for each email.
VERIFICATION_CODES = {}

# This has little to no use now because we're now using bootstrap for the frontend.
# But it's still here because I don't know whether some files are still using it.
version = f"{int(datetime.now().timestamp())}" + f"{random.randint(1, 1000)}"

# Sends verification codes to email address depending whether for resetting password or signing up.
async def send_verification_email(to_email, code):
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = to_email
        msg['Subject'] = "Your Verification Code"
        body = f"Your verification code is {code}."
        msg.attach(MIMEText(body, 'plain'))

        # Run the SMTP operations in a separate thread
        await asyncio.to_thread(send_email_sync, msg)

        print("Verification email sent successfully.")
    except Exception as e:
        print(f"Error sending email: {e}")

# Another part of email sending.
def send_email_sync(msg):
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)

# I'm not sure whether I'm still using this one.
def verification_confirmed(to_email):
    try:
        # Create the email
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = to_email
        msg['Subject'] = "Email Verified"
        body = f"""
        Your email has been verified.
        """
        msg.attach(MIMEText(body, 'plain'))

        # Connect to Gmail and send email
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)
        print("Verification email sent successfully.")
    except Exception as e:
        print(f"Error sending email: {e}")

SECRET_KEY = super_secret_data["SuperSecret"][0]["SuperSecretKey"]
serializer = URLSafeTimedSerializer(SECRET_KEY)

app = FastAPI()

# Middleware for managing sessions
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)  # type: ignore

# Database and other setup...
database = mysql.connector.connect(
    host= super_secret_data["Database_Stuff"][0]["host"],
    user= super_secret_data["Database_Stuff"][0]["user"],
    password= super_secret_data["Database_Stuff"][0]["password"],
    port= super_secret_data["Database_Stuff"][0]["port"],
    database= super_secret_data["Database_Stuff"][0]["database"]
)

cursor = database.cursor()

logging.basicConfig(level=logging.DEBUG)
app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize templates
templates = Jinja2Templates(directory="templates")

class User(BaseModel):
    fullName: str
    age: int
    email: str
    password: str

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

# Load data.json
DATA_FILE = os.path.join("static", "data", "data.json")

def load_data(file_path):
    with open(file_path, "r") as file:
        return json.load(file)

# Save data to JSON
def save_data(file_path, data):
    with open(file_path, "w") as file:
        json.dump(data, file, indent=2)

announcement_data = load_data(DATA_FILE)

def get_current_user(session_token: str = Cookie(None)):
    if session_token is None:
        raise HTTPException(status_code=303, detail="Redirect", headers={"Location": "/unauthorized"})
    try:
        email = serializer.loads(session_token)
        return email
    except Exception:
        raise HTTPException(status_code=303, detail="Redirect", headers={"Location": "/unauthorized"})

@app.get("/announcement/{announcement_id}", response_class=HTMLResponse)
async def display_announcement(announcement_id: int, request: Request, session_token: str = Cookie(None)):
    # Reload the announcement data
    announcement_data = load_data(DATA_FILE)
    user = None

    if session_token:
        try:
            user = serializer.loads(session_token)
        except Exception:
            pass

    for section in announcement_data.values():
        for announcement in section:
            if announcement["announcement_id"] == announcement_id:
                comments = announcement.get("comments", [])
                likes = announcement["likes"]["amount"]
                return templates.TemplateResponse(
                    "announcement.html",
                    {
                        "version": version,
                        "request": request,
                        "title": announcement["title"],
                        "date": announcement["date"],
                        "description": announcement.get("description", "No description available."),
                        "user": user,
                        "comments": comments,
                        "likes": likes,
                        "announcement_id": announcement_id,
                        "image_attachment": announcement.get("image_attachment")
                    }
                )
    raise HTTPException(status_code=404, detail="Announcement not found")

@app.get("/feedback", response_class=HTMLResponse)
async def read_feedback(request: Request, user: str = Depends(get_current_user)):
    return templates.TemplateResponse("feedback.html", {"request": request, "user": user, "version": version})

@app.get("/unauthorized", response_class=HTMLResponse)
async def unauthorized_page(request: Request):
    return templates.TemplateResponse("unauthorized.html", {"request": request})

@app.post("/submit_feedback")
async def submit_feedback(request: Request, user: str = Depends(get_current_user)):
    form = await request.form()
    title = form.get('title')
    description = form.get('description')
    attachment = form.get('attachment')

    if not title or not description:
        return JSONResponse({"message": "Title and description are required."}, status_code=400)

    feedback_data = load_data("static/data/feedback.json")
    feedback_id = max([fb["feedback_id"] for fb in feedback_data["feedbacks"]], default=0) + 1

    feedback = {
        "email": user,
        "feedback_title": title,
        "feedback_description": description,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "feedback_id": feedback_id
    }

    if attachment:
        directory = "static/images/Feedback/"
        file_extension = os.path.splitext(attachment.filename)[1]
        new_filename = f"{feedback_id}{file_extension}"
        attachment_path = os.path.join(directory, new_filename)
        with open(attachment_path, "wb") as f:
            f.write(await attachment.read())
        feedback["image_attachment"] = f"/{attachment_path}"

    feedback_data["feedbacks"].append(feedback)

    # Update the current value
    feedback_data["update"][0]["before"] = feedback_data["update"][0]["current"]
    feedback_data["update"][0]["current"] += 1

    save_data("static/data/feedback.json", feedback_data)

    return JSONResponse({"message": "Feedback submitted successfully."}, status_code=200)

@app.post("/announcement/{announcement_id}/comment")
async def add_comment(announcement_id: int, comment: str = Form(...), user: str = Depends(get_current_user)):
    cursor.execute("SELECT full_name FROM users WHERE email = %s", (user,))
    user_data = cursor.fetchone()
    if not user_data:
        raise HTTPException(status_code=404, detail="User not found")

    username = user_data[0]
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    new_comment = {
        "username": username,
        "comment": comment,
        "date": date,
        "email": user
    }

    announcement_data = load_data(DATA_FILE)
    for section in announcement_data.values():
        for announcement in section:
            if announcement["announcement_id"] == announcement_id:
                if "comments" not in announcement:
                    announcement["comments"] = []
                announcement["comments"].append(new_comment)
                save_data(DATA_FILE, announcement_data)
                return JSONResponse({"username": username, "comment": comment, "date": date})

    raise HTTPException(status_code=404, detail="Announcement not found")

@app.delete("/announcement/{announcement_id}/comment/{comment_index}")
async def delete_comment(announcement_id: int, comment_index: int, user: str = Depends(get_current_user)):
    announcement_data = load_data(DATA_FILE)
    for section in announcement_data.values():
        for announcement in section:
            if announcement["announcement_id"] == announcement_id:
                if "comments" in announcement and len(announcement["comments"]) > comment_index:
                    comment = announcement["comments"][comment_index]
                    if comment["email"] != user:
                        raise HTTPException(status_code=403, detail="You can only delete your own comments")
                    del announcement["comments"][comment_index]
                    save_data(DATA_FILE, announcement_data)
                    return JSONResponse({"message": "Comment deleted successfully"})
    raise HTTPException(status_code=404, detail="Announcement or comment not found")

@app.post("/announcement/{announcement_id}/like")
async def like_announcement(announcement_id: int, user: str = Depends(get_current_user)):
    announcement_data = load_data(DATA_FILE)
    for section in announcement_data.values():
        for announcement in section:
            if announcement["announcement_id"] == announcement_id:
                if user in announcement["likes"]["accounts"]:
                    announcement["likes"]["accounts"].remove(user)
                    announcement["likes"]["amount"] -= 1
                else:
                    announcement["likes"]["accounts"].append(user)
                    announcement["likes"]["amount"] += 1
                save_data(DATA_FILE, announcement_data)
                return JSONResponse({"likes": announcement["likes"]["amount"]})
    raise HTTPException(status_code=404, detail="Announcement not found")

@app.get("/signup_verification", response_class=HTMLResponse)
async def signup_verification_page(request: Request):
    return templates.TemplateResponse("signup_verification.html", {"request": request})

@app.post("/verify_code")
async def verify_code(data: dict):
    email = data.get('email')
    code = data.get('code')

    if not email or not code:
        return JSONResponse({"message": "Email and code are required."}, status_code=400)

    if email in VERIFICATION_CODES and VERIFICATION_CODES[email]["code"] == code:
        user_data = VERIFICATION_CODES[email]["user_data"]

        # Write user data to the database
        hashed_password = hash_password(user_data["password"])
        cursor.execute(
            "INSERT INTO users (full_name, age, email, password) VALUES (%s, %s, %s, %s)",
            (user_data["fullName"], user_data["age"], user_data["email"], hashed_password),
        )
        database.commit()
        del VERIFICATION_CODES[email]

        return RedirectResponse(url="/", status_code=303)  # Redirect to login
    else:
        return JSONResponse({"message": "Invalid verification code"}, status_code=400)

@app.post("/resend-code")
async def resend_code(data: dict):
    email = data.get('email')
    if not email:
        return JSONResponse({"message": "Email is required."}, status_code=400)

    if email in VERIFICATION_CODES:
        verification_code = VERIFICATION_CODES[email]["code"]
        asyncio.create_task(send_verification_email(email, verification_code))  # type: ignore
        return JSONResponse({"message": "Verification code resent."}, status_code=200)
    else:
        return JSONResponse({"message": "Email not found."}, status_code=404)

@app.post("/signup")
async def read_signup(user: User):
    # Check if email already exists
    cursor.execute("SELECT * FROM users WHERE email = %s", (user.email,))
    existing_user = cursor.fetchone()
    if existing_user:
        return JSONResponse({"message": "Email already exists"}, status_code=400)

    # Generate and store verification code
    verification_code = f"{random.randint(100000, 999999)}"
    VERIFICATION_CODES[user.email] = {
        "code": verification_code,
        "user_data": user.model_dump()  # Store user data temporarily
    }

    # Send email asynchronously
    asyncio.create_task(send_verification_email(user.email, verification_code))

    # Redirect to the verification page immediately
    return RedirectResponse(url=f"/signup_verification?email={user.email}", status_code=303)

@app.post("/login")
async def read_login(request: Request):
    credentials = await request.json()
    email = credentials['email']
    password = hash_password(credentials['password'])

    # Retrieve user data from the database
    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()

    if user and user[4] == password:  # Assuming password is in the 5th column
        # Create a session token
        session_token = serializer.dumps(email)  # Tokenized email for session
        response = RedirectResponse(url="/homepage", status_code=303)
        response.set_cookie(key="session_token", value=session_token, httponly=True)
        return response

    return JSONResponse({"message": "Login failed"}, status_code=401)

@app.get("/login_form", response_class=HTMLResponse)
async def read_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "version": version})

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("guest_view.html", {"request": request, "version": version})

@app.get("/signup_form", response_class=HTMLResponse)
async def read_signup_form(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request, "version": version})

# opens up in new tab when terms and conditions is clicked
@app.get("/terms", response_class=HTMLResponse)
async def read_terms(request: Request):
    return templates.TemplateResponse("terms.html", {"request": request})

@app.get("/homepage", response_class=HTMLResponse)
async def read_homepage(request: Request, user: str = Depends(get_current_user)):
    return templates.TemplateResponse("homepage.html", {"request": request, "user": user, "version": version})

@app.get("/upcoming", response_class=HTMLResponse)
async def read_upcoming(request: Request, user: str = Depends(get_current_user)):
    return templates.TemplateResponse("upcoming.html", {"request": request, "user": user, "version": version})

@app.get("/important", response_class=HTMLResponse)
async def read_important(request: Request, user: str = Depends(get_current_user)):
    return templates.TemplateResponse("important.html", {"request": request, "user": user, "version": version})

@app.get("/milestones", response_class=HTMLResponse)
async def read_milestones(request: Request, user: str = Depends(get_current_user)):
    return templates.TemplateResponse("milestones.html", {"request": request, "user": user, "version": version})

@app.post("/logout")
async def logout():
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie(key="session_token")
    return response

@app.get("/forgot_password", response_class=HTMLResponse)
async def forgot_password_page(request: Request):
    return templates.TemplateResponse("forgot_password.html", {"request": request, "version": version})

@app.post("/forgot_password/send_verification_code")
async def forgot_password_send_verification_code(email: str = Form(...)):
    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()
    if not user:
        return JSONResponse({"message": "Email not found"}, status_code=404)

    verification_code = f"{random.randint(100000, 999999)}"
    VERIFICATION_CODES[email] = verification_code
    await send_verification_email(email, verification_code)
    return JSONResponse({"message": "Verification code sent"}, status_code=200)

@app.post("/forgot_password/verify_code")
async def forgot_password_verify_code(email: str = Form(...), code: str = Form(...)):
    if email in VERIFICATION_CODES and VERIFICATION_CODES[email] == code:
        return JSONResponse({"message": "Code verified"}, status_code=200)
    return JSONResponse({"message": "Invalid verification code"}, status_code=400)

@app.post("/forgot_password/reset_password")
async def forgot_password_reset_password(email: str = Form(...), new_password: str = Form(...)):
    hashed_password = hash_password(new_password)
    cursor.execute("UPDATE users SET password = %s WHERE email = %s", (hashed_password, email))
    database.commit()
    return RedirectResponse(url="/", status_code=303)

@app.get("/archives", response_class=HTMLResponse)
async def read_archives(request: Request, user: str = Depends(get_current_user)):
    return templates.TemplateResponse("archived.html", {"request": request, "user": user, "version": version})

@app.get("/archives/{archive_id}", response_class=HTMLResponse)
async def read_archives_section(archive_id: int, request: Request, user: str = Depends(get_current_user)):
    archived_data = load_data("static/data/archived_data.json")

    for section in archived_data.values():
        for announcement in section:
            if announcement["archive_id"] == archive_id:
                comments = announcement.get("comments", [])
                return templates.TemplateResponse(
                    "archived_announcement.html",
                    {
                        "request": request,
                        "title": announcement["title"],
                        "date": announcement["date"],
                        "description": announcement.get("description", "No description available."),
                        "likes": announcement["likes"]["amount"],
                        "announcement_id": announcement["announcement_id"],
                        "image_attachment": announcement.get("image_attachment"),
                        "comments": comments
                    }
                )
    raise HTTPException(status_code=404, detail="Announcement not found")

@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 404:
        return templates.TemplateResponse("four-o-four.html", {"request": request}, status_code=404)
    elif exc.status_code == 303:
        return templates.TemplateResponse("unauthorized.html", {"request": request}, status_code=303)
    return JSONResponse({"detail": exc.detail}, status_code=exc.status_code)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse({"detail": exc.errors()}, status_code=400)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
