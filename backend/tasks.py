import os
import csv
from datetime import datetime, timedelta
from app import create_app
from models import db, Booking, User, Trek
from celery import shared_task
from flask_mail import Message
from mail import mail


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
    
    # Send Email with attachment
    msg = Message("Your Booking History Export", recipients=[user_email])
    html_body = f"""
    <div style="font-family: system-ui, -apple-system, sans-serif; background-color: #f7fafc; padding: 2rem;">
      <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; padding: 2rem; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
        <h2 style="color: #2C5E3B; margin-top: 0;">TrekAarohan-Nexus</h2>
        <h3 style="color: #1A202C;">Booking History Export</h3>
        <p style="color: #4A5568; font-size: 16px; line-height: 1.5;">Hi <strong>{user_name}</strong>,</p>
        <p style="color: #4A5568; font-size: 16px; line-height: 1.5;">Your requested booking history containing <strong>{len(bookings)}</strong> records has been successfully exported.</p>
        <p style="color: #4A5568; font-size: 16px; line-height: 1.5;">Please find the CSV file securely attached to this email.</p>
        <hr style="border: none; border-top: 1px solid #e2e8f0; margin: 2rem 0;" />
        <p style="color: #718096; font-size: 12px; text-align: center;">This is an automated message from TrekAarohan-Nexus.</p>
      </div>
    </div>
    """
    msg.html = html_body
    with open(filename, "rb") as fp:
        msg.attach(os.path.basename(filename), "text/csv", fp.read())
    mail.send(msg)
    
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
    
    # Execute mailing logic atomically
    emails_sent = 0
    for data in email_queue:
        msg = Message("Reminder: Your Upcoming Treks", recipients=[data["email"]])
        trek_details_html = ""
        for t in data["upcoming_treks"]:
            trek_details_html += f'''
            <li style="margin-bottom: 12px;">
                <strong style="color: #1A202C;">{t['name']}</strong> at {t['location']} <br/>
                <span style="color: #718096; font-size: 14px;">Starting on: {t['start_date']}</span>
            </li>
            '''
        html_body = f"""
        <div style="font-family: system-ui, -apple-system, sans-serif; background-color: #f7fafc; padding: 2rem;">
          <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; padding: 2rem; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
            <h2 style="color: #2C5E3B; margin-top: 0;">TrekAarohan-Nexus</h2>
            <h3 style="color: #1A202C;">Upcoming Trek Reminder</h3>
            <p style="color: #4A5568; font-size: 16px; line-height: 1.5;">Hi <strong>{data['name']}</strong>,</p>
            <p style="color: #4A5568; font-size: 16px; line-height: 1.5;">Get your gear ready! Here is a quick reminder of your upcoming treks:</p>
            <ul style="color: #4A5568; font-size: 16px; line-height: 1.5; background-color: #FFFBEB; border-left: 4px solid #D97706; padding: 1.5rem 1.5rem 1.5rem 2.5rem; border-radius: 6px; margin: 1.5rem 0;">
                {trek_details_html}
            </ul>
            <p style="color: #4A5568; font-size: 16px; line-height: 1.5;">We can't wait to see you on the trail!</p>
            <hr style="border: none; border-top: 1px solid #e2e8f0; margin: 2rem 0;" />
            <p style="color: #718096; font-size: 12px; text-align: center;">This is an automated message from TrekAarohan-Nexus.</p>
          </div>
        </div>
        """
        msg.html = html_body
        mail.send(msg)
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
    <div style="font-family: system-ui, -apple-system, sans-serif; background-color: #f7fafc; padding: 2rem;">
      <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; padding: 2rem; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
        <h2 style="color: #2C5E3B; margin-top: 0;">TrekAarohan-Nexus</h2>
        <h3 style="color: #1A202C;">Monthly Platform Report</h3>
        <p style="color: #4A5568; font-size: 16px; line-height: 1.5;">Here are the latest statistics for <strong>{current_month}</strong>:</p>
        <table style="width: 100%; border-collapse: collapse; margin-top: 1.5rem; margin-bottom: 1.5rem;">
          <thead>
            <tr>
                <th style="background-color: #edf2f7; color: #4A5568; padding: 12px; text-align: left; border-bottom: 2px solid #cbd5e0; border-top-left-radius: 6px;">Metric</th>
                <th style="background-color: #edf2f7; color: #4A5568; padding: 12px; text-align: right; border-bottom: 2px solid #cbd5e0; border-top-right-radius: 6px;">Count</th>
            </tr>
          </thead>
          <tbody>
            <tr>
                <td style="padding: 12px; border-bottom: 1px solid #e2e8f0; color: #1A202C;">Total Treks</td>
                <td style="padding: 12px; border-bottom: 1px solid #e2e8f0; color: #1A202C; text-align: right; font-weight: bold;">{total_treks}</td>
            </tr>
            <tr>
                <td style="padding: 12px; border-bottom: 1px solid #e2e8f0; color: #1A202C;">Active Bookings</td>
                <td style="padding: 12px; border-bottom: 1px solid #e2e8f0; color: #1A202C; text-align: right; font-weight: bold;">{active_bookings}</td>
            </tr>
            <tr>
                <td style="padding: 12px; border-bottom: 1px solid #e2e8f0; color: #1A202C;">Total Trekkers</td>
                <td style="padding: 12px; border-bottom: 1px solid #e2e8f0; color: #1A202C; text-align: right; font-weight: bold;">{total_trekkers}</td>
            </tr>
            <tr>
                <td style="padding: 12px; border-bottom: 1px solid #e2e8f0; color: #1A202C;">Total Staff</td>
                <td style="padding: 12px; border-bottom: 1px solid #e2e8f0; color: #1A202C; text-align: right; font-weight: bold;">{total_staffs}</td>
            </tr>
          </tbody>
        </table>
        <hr style="border: none; border-top: 1px solid #e2e8f0; margin: 2rem 0;" />
        <p style="color: #718096; font-size: 12px; text-align: center;">This is an automated message from TrekAarohan-Nexus.</p>
      </div>
    </div>
    """
    
    # Send Email
    msg = Message("Monthly Platform Report", recipients=[admin.email])
    msg.html = html_body
    mail.send(msg)
    
    return f"Sent monthly report to admin ({admin.email})."


@shared_task(ignore_result=False)
def send_staff_welcome_email(staff_email, staff_name, staff_username, password):
    msg = Message("Welcome to TrekAarohan-Nexus Staff", recipients=[staff_email])
    
    html_body = f"""
    <div style="font-family: system-ui, -apple-system, sans-serif; background-color: #f7fafc; padding: 2rem;">
      <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; padding: 2rem; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
        <h2 style="color: #2C5E3B; margin-top: 0;">TrekAarohan-Nexus</h2>
        <h3 style="color: #1A202C;">Welcome to the Team!</h3>
        <p style="color: #4A5568; font-size: 16px; line-height: 1.5;">Hi <strong>{staff_name}</strong>,</p>
        <p style="color: #4A5568; font-size: 16px; line-height: 1.5;">Your staff account was successfully registered. Here are your login credentials:</p>
        <div style="background-color: #FFFBEB; border-left: 4px solid #D97706; padding: 1.5rem; border-radius: 6px; margin: 1.5rem 0;">
            <p style="margin: 0 0 10px 0; color: #1A202C; font-size: 15px;"><strong>Username:</strong> {staff_username}</p>
            <p style="margin: 0 0 10px 0; color: #1A202C; font-size: 15px;"><strong>Email:</strong> {staff_email}</p>
            <p style="margin: 0; color: #1A202C; font-size: 15px;"><strong>Password:</strong> <span style="font-family: monospace; background-color: #FDE68A; padding: 2px 6px; border-radius: 4px;">{password}</span></p>
        </div>
        <p style="color: #4A5568; font-size: 16px; line-height: 1.5;">Please log in as soon as possible and update your profile details if necessary.</p>
        <hr style="border: none; border-top: 1px solid #e2e8f0; margin: 2rem 0;" />
        <p style="color: #718096; font-size: 12px; text-align: center;">This is an automated message from TrekAarohan-Nexus.</p>
      </div>
    </div>
    """
    msg.html = html_body
    mail.send(msg)
    
    return f"Sent welcome email to new staff: {staff_email}"

