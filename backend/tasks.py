import csv
import os
from celery import shared_task
from app import create_app
from models import db, Booking, User


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

