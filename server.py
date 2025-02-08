import os
import datetime
import json
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from apscheduler.schedulers.background import BackgroundScheduler
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import pytz
import llm
import db
# Initialize Flask app
app = Flask(__name__)

# Configuration for Uploads
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Allowed file extensions
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}

# Helper function to validate file type
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Helper function to save submission metadata
def save_submission_data(filename, deadline):
    submission_data = {"filename": filename, "deadline": deadline}
    with open("submissions.json", "a") as f:
        json.dump(submission_data, f)
        f.write("\n")

# Email sending function (using Gmail's SMTP)
def send_email(to_address, subject, body):
    from_address = "barshannaskar5@gmail.com"  # Your Gmail address
    app_password = "barshan20"  # Your Gmail app password (or SMTP password)

    # Create the email message
    msg = MIMEMultipart()
    msg['From'] = from_address
    msg['To'] = to_address
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    # Send email via Gmail's SMTP server
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(from_address, app_password)
        text = msg.as_string()
        server.sendmail(from_address, to_address, text)
        server.quit()
        print(f"Email sent to {to_address}")
    except Exception as e:
        print(f"Failed to send email to {to_address}. Error: {str(e)}")

# Function to send scheduled email notifications
def send_scheduled_notifications():
    submissions = []
    try:
        with open("submissions.json", "r") as file:
            submissions = [json.loads(line.strip()) for line in file.readlines()]
    except FileNotFoundError:
        submissions = []

    # Filter submissions with upcoming deadlines
    upcoming_deadlines = []
    for submission in submissions:
        deadline_date = datetime.datetime.strptime(submission['deadline'], "%Y-%m-%d")
        if deadline_date > datetime.datetime.now():
            upcoming_deadlines.append(submission)

    # Send email notifications for upcoming deadlines
    for submission in upcoming_deadlines:
        user_email = "rajeetash@hotmail.com"  # Replace with actual user email
        subject = f"Upcoming Deadline for {submission['filename']}"
        body = f"Dear User,\n\nThis is a reminder that the deadline for {submission['filename']} is approaching on {submission['deadline']}.\n\nBest regards,\nYour Notification System"
        print("Email sent")
        send_email(user_email, subject, body)

# Schedule the email notifications to run at 18:00 IST daily
scheduler = BackgroundScheduler(timezone=pytz.timezone("Asia/Kolkata"))
scheduler.add_job(send_scheduled_notifications, 'cron', hour=18, minute=3)  # At 18:00 IST
scheduler.start()

# Routes
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]
    deadline = request.form.get("deadline")

    # Validate file presence and type
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "Unsupported file type"}), 400

    if not deadline:
        return jsonify({"error": "Please select a deadline"}), 400

    # Validate and parse deadline
    try:
        deadline_date = datetime.datetime.strptime(deadline, "%Y-%m-%d")
    except ValueError:
        return jsonify({"error": "Invalid date format"}), 400

    # Save the file securely
    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(file_path)

    # Process the file (if needed)
    db.process_file(file_path, "chroma")

    # Save metadata for future reference
    save_submission_data(filename, deadline)

    return render_template("chat.html", filename=filename)

# Chat Page Route (GET)
@app.route("/chat")
def chat_page():
    return render_template("chat.html")


# Chat API Route (POST)
@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message", "").strip()

    if not user_input:
        return jsonify({"error": "Empty message received"}), 400

    # Placeholder AI response for demonstration
    response_text = f'{user_input}'

    # Use query_rag to get the prompt (assuming llm.py is implemented with query_rag and send_to_local_server)
    rag_prompt = llm.query_rag(user_input)
    print(rag_prompt)
    if not rag_prompt:
        return jsonify({"error": "No relevant context found"}), 400

    # Send the prompt to the local server
    response = llm.send_to_local_server(rag_prompt)

    if response.status_code == 200:
        response_text = response.json().get('content', '')
        return jsonify({"message": response_text})
    else:
        return jsonify({"error": "Failed to get response from the local server"}), 500

# Notifications Page Route (GET)
@app.route("/notifications")
def notifications_page():
    # Read submission data from the file
    submissions = []
    try:
        with open("submissions.json", "r") as file:
            submissions = [json.loads(line.strip()) for line in file.readlines()]
    except FileNotFoundError:
        submissions = []

    # Filter notifications for upcoming deadlines
    upcoming_deadlines = []
    for submission in submissions:
        deadline_date = datetime.datetime.strptime(submission['deadline'], "%Y-%m-%d")
        if deadline_date > datetime.datetime.now():
            upcoming_deadlines.append(submission)

    return render_template("notifications.html", deadlines=upcoming_deadlines)

# Main entry point
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=6969, debug=False)
