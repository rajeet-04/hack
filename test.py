import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_email(to_address, subject, body):
    from_address = "ashrajeet@gmail.com"  # Your Gmail address
    app_password = "Meek@2004"  # Your Gmail app password (or SMTP password)

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

def main():
    send_email("rajeetash@hotmail.com", "Test Subject", "Hi there!")

if __name__ == '__main__':
    main()
