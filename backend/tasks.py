import os
import csv
from datetime import datetime, timedelta
from celery import shared_task
from app import create_app
from models import db, Booking, User, Trek


@shared_task(ignore_result=False)
def export_booking_history_csv(user_id, user_email):
    export_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "exports")
    if not os.path.exists(export_dir):
        os.makedirs(export_dir)
    filename = os.path.join(export_dir, f"booking_history_{user_id}.csv")
    
    # Query all bookings for this user
    bookings = Booking.query.filter_by(user_id=user_id).all()
    user = User.query.get(user_id)
    user_name = user.name if user else "Trekker"
    
    # Generate CSV file
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Booking ID", "Trek ID", "Trek Name", "Location", "Start Date", "End Date", "Duration", "Booking Date", "Cancelled Date", "Booking Status"])
        for b in bookings:
            duration = (b.trek.end_date - b.trek.start_date).days + 1
            cancelled_date = b.cancelled_date.strftime("%Y-%m-%d") if b.cancelled_date else ""
            writer.writerow([
                b.id,
                b.trek.id,
                b.trek.name,
                b.trek.location,
                b.trek.start_date.strftime("%Y-%m-%d"),
                b.trek.end_date.strftime("%Y-%m-%d"),
                duration,
                b.booking_date.strftime("%Y-%m-%d"),
                cancelled_date,
                b.status
            ])
    
    # Mock Email Output
    print(f"--- [MOCK EMAIL SENT] ---")
    print(f"To: {user_email}")
    print(f"Subject: Your Booking History Export")
    print(f"Attachment: booking_history_{user_id}.csv")
    print(f"Message: Hi {user_name}, your booking history containing {len(bookings)} records has been exported successfully!")
    
    return f"Export completed for {user_email}. File saved as {filename}"


@shared_task(ignore_result=False)
def send_daily_reminders():
    # Get all trek statistics
    trekkers = User.query.filter_by(role=0).all()
    email_queue = []
    for trekker in trekkers:
        valid_bookings = [b for b in trekker.bookings if b.status == "booked" and b.trek.status in ["open", "full"]]
        if valid_bookings:
            upcoming_treks = []
            for b in valid_bookings:
                upcoming_treks.append({
                    "name": b.trek.name,
                    "location": b.trek.location,
                    "start_date": b.trek.start_date.strftime("%Y-%m-%d")
                })
            email_queue.append({
                "email": trekker.email,
                "name": trekker.name,
                "upcoming_treks": upcoming_treks
            })
    
    # Mock Email Output
    emails_sent = 0
    for data in email_queue:
        print(f"--- [MOCK EMAIL SENT] ---")
        print(f"To: {data['email']}")
        print(f"Subject: Reminder: Your Upcoming Treks")
        trek_details = ""
        for t in data["upcoming_treks"]:
            trek_details += f"\n - {t['name']} at {t['location']} starting on {t['start_date']}"
        print(f"Message: Hi {data['name']}, here is a reminder of your upcoming treks:{trek_details}")
        emails_sent += 1
    
    return f"Sent {emails_sent} daily reminder emails for upcoming treks."


@shared_task(ignore_result=False)
def send_monthly_reports():
    # Get all trek statistics
    total_treks = Trek.query.count()
    active_bookings = Booking.query.filter_by(status="booked").count()
    total_trekkers = User.query.filter_by(role=0).count()
    total_staffs = User.query.filter_by(role=1).count()
    current_month = datetime.utcnow().strftime("%B %Y")
    admin = User.query.filter_by(role=2).first()
    
    # Construct HTML Report Body
    html_body = f"""
    <html>
      <body style="font-family: Arial, sans-serif; color: #333;">
        <h2>Monthly Admin Report - {current_month}</h2>
        <table border="1" cellpadding="10" cellspacing="0" style="border-collapse: collapse;">
          <tr style="background-color: #f8f9fa;"><th>Metric</th><th>Count</th></tr>
          <tr><td>Total Treks</td><td>{total_treks}</td></tr>
          <tr><td>Active Bookings</td><td>{active_bookings}</td></tr>
          <tr><td>Total Trekkers</td><td>{total_trekkers}</td></tr>
          <tr><td>Total Staffs</td><td>{total_staffs}</td></tr>
        </table>
        <p>This is an automatically generated report by TrekAarohan-Nexus.</p>
      </body>
    </html>
    """
    
    # Mock Email Output
    print(f"--- [MOCK HTML EMAIL SENT] ---")
    print(f"To: {admin.email}")
    print(f"Subject: Monthly Platform Report")
    print(f"Body: \n{html_body}")
    
    return f"Sent monthly report to admin ({admin.email})."

