import os
import random
import string
from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
from models import db, User, Trek, Booking
from tasks import send_staff_welcome_email

admin_bp = Blueprint("admin", __name__)

def admin_required():
    claims = get_jwt()
    if claims.get("role") != 2:
        return False
    return True


@admin_bp.route("/dashboard", methods=["GET"])
@jwt_required()
def get_dashboard():
    if not admin_required():
        return jsonify({"error": "Admin access required"}), 403
    
    total_treks = Trek.query.count()
    active_bookings = Booking.query.filter_by(status="booked").count()
    total_trekkers = User.query.filter_by(role=0).count()
    total_staffs = User.query.filter_by(role=1).count()
    users = User.query.order_by(User.id.desc()).all()
    
    serialized_users = []
    for u in users:
        serialized_users.append({
            "id": u.id,
            "role": u.role,
            "username": u.username,
            "name": u.name,
            "email": u.email,
            "phone": u.phone,
            "emergency_phone": u.emergency_phone,
            "emergency_relation": u.emergency_relation,
            "is_blacklisted": u.is_blacklisted
        })
    
    return jsonify({
        "total_treks": total_treks,
        "active_bookings": active_bookings,
        "total_trekkers": total_trekkers,
        "total_staffs": total_staffs,
        "admin_name": get_jwt().get("name", "Admin"),
        "users": serialized_users
    }), 200


@admin_bp.route("/staffs", methods=["GET"])
@jwt_required()
def get_staffs():
    if not admin_required():
        return jsonify({"error": "Admin access required"}), 403
    
    staffs = User.query.filter_by(role=1).all()
    staff_list = []
    for s in staffs:
        staff_list.append({
            "id": s.id,
            "username": s.username,
            "name": s.name,
            "email": s.email,
            "phone": s.phone,
            "experience": s.experience,
            "total_treks": len(s.assigned_treks),
            "is_blacklisted": s.is_blacklisted
        })
    return jsonify(staff_list), 200


@admin_bp.route("/staffs", methods=["POST"])
@jwt_required()
def create_staff():
    if not admin_required():
        return jsonify({"error": "Admin access required"}), 403
    
    data = request.get_json()
    if not data:
        return jsonify({"error": "No input data provided"}), 400
    
    username = data.get("username")
    name = data.get("name")
    email = data.get("email")
    phone = data.get("phone")
    experience = data.get("experience", "")
    
    # Generate secure random password
    chars = string.ascii_letters + string.digits + "!@#$%"
    password = "".join(random.choice(chars) for _ in range(12))
    
    if not username or not email or not name or not phone:
        return jsonify({"message": "Missing required fields"}), 400
    try:
        int(phone)
    except (ValueError, TypeError):
        return jsonify({"message": "Phone number must be a valid number."}), 400
    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Username already exists"}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already registered"}), 400
    
    new_staff = User(
        username=username,
        password=generate_password_hash(password),
        name=name,
        email=email,
        phone=phone,
        role=1,
        experience=experience
    )
    db.session.add(new_staff)
    db.session.commit()
    
    # Dispatch async email to staff
    send_staff_welcome_email.delay(email, name, username, password)
    
    return jsonify({"message": "Staff created successfully"}), 201


@admin_bp.route("/staffs/<int:staff_id>/blacklist", methods=["PUT"])
@jwt_required()
def toggle_blacklist(staff_id):
    if not admin_required():
        return jsonify({"error": "Admin access required"}), 403
    
    staff = User.query.get_or_404(staff_id)
    if staff.role != 1:
        return jsonify({"error": "User is not a staff member"}), 400
    
    staff.is_blacklisted = not staff.is_blacklisted
    db.session.commit()
    
    status = "blacklisted" if staff.is_blacklisted else "unblacklisted"
    return jsonify({"message": f"Staff {status} successfully"}), 200


@admin_bp.route("/trekkers", methods=["GET"])
@jwt_required()
def get_trekkers():
    if not admin_required():
        return jsonify({"error": "Admin access required"}), 403
    
    trekkers = User.query.filter_by(role=0).all()
    trekker_list = []
    for t in trekkers:
        trekker_list.append({
            "id": t.id,
            "username": t.username,
            "name": t.name,
            "email": t.email,
            "phone": t.phone,
            "emergency_phone": t.emergency_phone,
            "emergency_relation": t.emergency_relation,
            "total_bookings": len(t.bookings),
            "is_blacklisted": t.is_blacklisted
        })
    return jsonify(trekker_list), 200


@admin_bp.route("/trekkers/<int:trekker_id>/blacklist", methods=["PUT"])
@jwt_required()
def toggle_trekker_blacklist(trekker_id):
    if not admin_required():
        return jsonify({"error": "Admin access required"}), 403
    
    trekker = User.query.get_or_404(trekker_id)
    if trekker.role != 0:
        return jsonify({"error": "User is not a trekker"}), 400
    
    trekker.is_blacklisted = not trekker.is_blacklisted
    db.session.commit()
    
    status = "blacklisted" if trekker.is_blacklisted else "unblacklisted"
    return jsonify({"message": f"Trekker {status} successfully"}), 200


@admin_bp.route("/treks", methods=["GET"])
@jwt_required()
def get_treks():
    if not admin_required():
        return jsonify({"error": "Admin access required"}), 403
    
    treks = Trek.query.order_by(Trek.id.desc()).all()
    trek_list = []
    for t in treks:
        duration = (t.end_date - t.start_date).days + 1
        trek_list.append({
            "id": t.id,
            "name": t.name,
            "location": t.location,
            "start_date": t.start_date.isoformat(),
            "end_date": t.end_date.isoformat(),
            "duration": duration,
            "difficulty": t.difficulty,
            "status": t.status,
            "slots_available": t.slots_available,
            "price": t.price,
            "cover_image": t.cover_image
        })
    return jsonify(trek_list), 200


@admin_bp.route("/treks", methods=["POST"])
@jwt_required()
def create_trek():
    if not admin_required():
        return jsonify({"error": "Admin access required"}), 403
    
    data = request.form
    name = data.get("name")
    location = data.get("location")
    description = data.get("description", "")
    difficulty = data.get("difficulty")
    start_date_str = data.get("start_date")
    end_date_str = data.get("end_date")
    slots_available = data.get("slots_available")
    price = data.get("price")
    assigned_staff_id = data.get("assigned_staff_id")
    
    if not all([name, location, difficulty, start_date_str, end_date_str, slots_available, price, assigned_staff_id]):
        return jsonify({"error": "All required fields must be provided"}), 400
    try:
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400
    if start_date > end_date:
        return jsonify({"error": "Start date must be before or equal to end date"}), 400
    staff = User.query.get(assigned_staff_id)
    if not staff or staff.role != 1 or staff.is_blacklisted:
        return jsonify({"error": "Invalid or blacklisted staff member selected"}), 400
    
    cover_image_path = None
    if "cover_image" in request.files:
        file = request.files["cover_image"]
        if file.filename != "":
            filename = secure_filename(file.filename)
            filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
            upload_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "uploads")
            os.makedirs(upload_folder, exist_ok=True)
            file_path = os.path.join(upload_folder, filename)
            file.save(file_path)
            cover_image_path = f"/static/uploads/{filename}"
    
    new_trek = Trek(
        name=name,
        location=location,
        description=description,
        difficulty=difficulty,
        start_date=start_date,
        end_date=end_date,
        slots_available=int(slots_available),
        price=float(price),
        assigned_staff_id=int(assigned_staff_id),
        cover_image=cover_image_path
    )
    
    db.session.add(new_trek)
    db.session.commit()
    
    return jsonify({"message": "Trek created successfully", "trek_id": new_trek.id}), 201


@admin_bp.route("/treks/<int:trek_id>", methods=["GET"])
@jwt_required()
def get_trek(trek_id):
    if not admin_required():
        return jsonify({"error": "Admin access required"}), 403
    
    trek = Trek.query.get_or_404(trek_id)
    staff = trek.staff
    staff_completed_treks = Trek.query.filter_by(assigned_staff_id=staff.id, status="completed").count() if staff else 0
    
    bookings = Booking.query.filter_by(trek_id=trek.id).order_by(Booking.booking_date.desc()).all()
    serialized_bookings = []
    for b in bookings:
        serialized_bookings.append({
            "id": b.id,
            "status": b.status,
            "booking_date": b.booking_date.isoformat(),
            "user": {
                "username": b.user.username,
                "name": b.user.name,
                "email": b.user.email,
                "phone": b.user.phone,
                "emergency_relation": b.user.emergency_relation,
                "emergency_phone": b.user.emergency_phone
            }
        })
    
    return jsonify({
        "id": trek.id,
        "name": trek.name,
        "location": trek.location,
        "description": trek.description,
        "start_date": trek.start_date.isoformat(),
        "end_date": trek.end_date.isoformat(),
        "duration": (trek.end_date - trek.start_date).days + 1,
        "difficulty": trek.difficulty,
        "status": trek.status,
        "slots_available": trek.slots_available,
        "price": trek.price,
        "cover_image": trek.cover_image,
        "assigned_staff_id": trek.assigned_staff_id,
        "staff_name": staff.name if staff else "Unassigned",
        "staff_experience": staff.experience if staff else "",
        "staff_completed_treks": staff_completed_treks,
        "bookings": serialized_bookings
    }), 200


@admin_bp.route("/treks/<int:trek_id>", methods=["PUT"])
@jwt_required()
def update_trek(trek_id):
    if not admin_required():
        return jsonify({"error": "Admin access required"}), 403
    
    trek = Trek.query.get_or_404(trek_id)
    if trek.status in ["completed", "cancelled"]:
        return jsonify({"error": "This trek has concluded and cannot be edited."}), 400
    
    data = request.form
    name = data.get("name")
    location = data.get("location")
    description = data.get("description", "")
    difficulty = data.get("difficulty")
    start_date_str = data.get("start_date")
    end_date_str = data.get("end_date")
    slots_available = data.get("slots_available")
    price = data.get("price")
    assigned_staff_id = data.get("assigned_staff_id")
    status = data.get("status")
    
    if not all([name, location, difficulty, start_date_str, end_date_str, slots_available, price, assigned_staff_id]):
        return jsonify({"error": "All required fields must be provided"}), 400
    try:
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400
    if start_date > end_date:
        return jsonify({"error": "Start date must be before or equal to end date"}), 400
    staff = User.query.get(assigned_staff_id)
    if not staff or staff.role != 1:
        return jsonify({"error": "Invalid staff member selected"}), 400
    
    if "cover_image" in request.files:
        file = request.files["cover_image"]
        if file.filename != "":
            filename = secure_filename(file.filename)
            filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
            upload_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "uploads")
            os.makedirs(upload_folder, exist_ok=True)
            file_path = os.path.join(upload_folder, filename)
            file.save(file_path)
            trek.cover_image = f"/static/uploads/{filename}"
    
    trek.name = name
    trek.location = location
    trek.description = description
    trek.difficulty = difficulty
    trek.start_date = start_date
    trek.end_date = end_date
    trek.price = float(price)
    trek.assigned_staff_id = int(assigned_staff_id)
    
    slots = int(slots_available)
    new_status = status
    if new_status:
        if new_status == "full" or (new_status == "open" and slots <= 0):
            new_status = "full"
            slots = 0
        if new_status in ["completed", "cancelled"] and trek.status not in ["completed", "cancelled"]:
            bookings = Booking.query.filter_by(trek_id=trek.id, status="booked").all()
            for b in bookings:
                b.status = new_status
                if new_status == "cancelled":
                    b.cancelled_date = datetime.utcnow()
        trek.status = new_status
    trek.slots_available = slots
    
    db.session.commit()
    return jsonify({"message": "Trek updated successfully"}), 200


@admin_bp.route("/bookings", methods=["GET"])
@jwt_required()
def get_bookings():
    if not admin_required():
        return jsonify({"error": "Admin access required"}), 403
    
    bookings = Booking.query.order_by(Booking.id.desc()).all()
    result = []
    for b in bookings:
        result.append({
            "id": b.id,
            "status": b.status,
            "booking_date": b.booking_date.isoformat(),
            "cancelled_date": b.cancelled_date.isoformat() if b.cancelled_date else None,
            "trek": {
                "id": b.trek.id,
                "name": b.trek.name,
                "start_date": b.trek.start_date.isoformat(),
                "status": b.trek.status
            },
            "user": {
                "username": b.user.username,
                "name": b.user.name,
                "email": b.user.email,
                "phone": b.user.phone,
                "emergency_relation": b.user.emergency_relation,
                "emergency_phone": b.user.emergency_phone
            }
        })
    return jsonify(result), 200


@admin_bp.route("/cancel_booking/<int:booking_id>", methods=["POST"])
@jwt_required()
def cancel_booking(booking_id):
    if not admin_required():
        return jsonify({"error": "Admin access required"}), 403
    
    booking = Booking.query.get_or_404(booking_id)
    trek = booking.trek
    
    if booking.status != "booked":
        return jsonify({"message": "This booking cannot be cancelled."}), 400
    if trek.status in ["completed", "cancelled"]:
        return jsonify({"message": "You cannot cancel a booking for a trek that has already concluded."}), 400
    
    booking.status = "cancelled"
    booking.cancelled_date = datetime.utcnow()
    trek.slots_available += 1
    if trek.status == "full":
        trek.status = "open"
    
    db.session.commit()
    
    return jsonify({"message": "Booking cancelled successfully. Slot reopened."}), 200

