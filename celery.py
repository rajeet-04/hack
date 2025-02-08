from celery import Celery
from datetime import datetime
import pytz

def make_celery(app):
    # Setup Celery to work with Flask
    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']
    )
    celery.conf.update(app.config)
    return celery

# The scheduled task to check and send the notification
@celery.task
def send_scheduled_notification():
    ist = pytz.timezone('Asia/Kolkata')
    now = datetime.now(ist)

    # Check if the time is 18:00 IST
    if now.hour == 18 and now.minute == 0:
        # Simulate sending notification
        print("Sending scheduled notification...")
        # You can use the logic from your existing code to send a push notification
        # Here, we just print a message
        # For example, send_notification(submission_data)
