from datetime import datetime
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.security import check_password_hash, generate_password_hash
from models import db, Trek, User, Booking
from tasks import export_booking_history_csv

trekker_bp = Blueprint("trekker", __name__)


@trekker_bp.route("/dashboard", methods=["GET"])
@jwt_required()
def get_dashboard():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user or user.role != 0:
        return jsonify({"message": "Forbidden"}), 403
    
    all_bookings = Booking.query.filter_by(user_id=user.id).all()
    valid_bookings = [b for b in all_bookings if b.status in ["booked", "completed"]]
    upcoming_treks = [b for b in valid_bookings if b.trek.status in ["open", "full", "ongoing"]]
    completed_treks = [b for b in valid_bookings if b.trek.status == "completed"]
    
    return jsonify({
        "upcoming_count": len(upcoming_treks),
        "completed_count": len(completed_treks),
        "total_count": len(valid_bookings),
        "trekker_name": user.name
    }), 200


@trekker_bp.route("/profile", methods=["GET"])
@jwt_required()
def get_profile():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user or user.role != 0:
        return jsonify({"message": "Forbidden"}), 403
    
    return jsonify({
        "username": user.username,
        "email": user.email,
        "name": user.name,
        "phone": user.phone,
        "emergency_phone": user.emergency_phone,
        "emergency_relation": user.emergency_relation,
        "is_blacklisted": user.is_blacklisted
    }), 200


@trekker_bp.route("/profile", methods=["PUT"])
@jwt_required()
def update_profile():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user or user.role != 0:
        return jsonify({"message": "Forbidden"}), 403
    
    data = request.json
    if not data:
        return jsonify({"message": "No data provided."}), 400
    
    name = data.get("name")
    email = data.get("email")
    phone = data.get("phone")
    emergency_phone = data.get("emergency_phone")
    emergency_relation = data.get("emergency_relation")
    old_password = data.get("old_password")
    new_password = data.get("new_password")
    
    if new_password:
        if not old_password:
            return jsonify({"message": "Old password is required to change password."}), 400
        if not check_password_hash(user.password, old_password):
            return jsonify({"message": "Incorrect old password."}), 400
    
    if not emergency_phone:
        emergency_phone = None
    if not emergency_relation:
        emergency_relation = None
    if not name or not phone or not email:
        return jsonify({"message": "Name, Email, and Phone number are required."}), 400
    try:
        int(phone)
        if emergency_phone:
            int(emergency_phone)
    except (ValueError, TypeError):
        return jsonify({"message": "Phone numbers must be valid numbers."}), 400
    
    existing_user = User.query.filter(User.email == email, User.id != current_user_id).first()
    if existing_user:
        return jsonify({"message": "Email is already registered by another user."}), 400
    
    user.name = name
    user.email = email
    user.phone = phone
    user.emergency_phone = emergency_phone
    user.emergency_relation = emergency_relation
    if new_password:
        user.password = generate_password_hash(new_password)
    
    db.session.commit()
    
    return jsonify({"message": "Profile updated successfully."}), 200


@trekker_bp.route("/treks/<int:trek_id>/book", methods=["POST"])
@jwt_required()
def book_trek(trek_id):
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user or user.role != 0:
        return jsonify({"message": "Forbidden. Only trekkers can book treks."}), 403
    if user.is_blacklisted:
        return jsonify({"message": "Your account is suspended. You cannot book new treks."}), 403
    
    trek = Trek.query.get_or_404(trek_id)
    if trek.status != "open":
        return jsonify({"message": "This trek is no longer open for booking."}), 400
    if not user.name or not user.phone or not user.email:
        return jsonify({"message": "Name, Email, and Phone number are required."}), 400
    
    existing_booking = Booking.query.filter_by(user_id=user.id, trek_id=trek.id, status="booked").first()
    if existing_booking:
        return jsonify({"message": "You have already booked this trek."}), 400
    
    trek.slots_available -= 1
    if trek.slots_available == 0:
        trek.status = "full"
    new_booking = Booking(
        user_id=user.id,
        trek_id=trek.id,
        status="booked"
    )
    
    db.session.add(new_booking)
    db.session.commit()
    
    return jsonify({"message": "Trek booked successfully!"}), 201


@trekker_bp.route("/bookings", methods=["GET"])
@jwt_required()
def get_bookings():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user or user.role != 0:
        return jsonify({"message": "Forbidden"}), 403
    
    bookings = Booking.query.filter_by(user_id=user.id, status="booked").order_by(Booking.id.desc()).all()
    result = []
    for b in bookings:
        result.append({
            "id": b.id,
            "booking_date": b.booking_date.isoformat(),
            "trek": {
                "id": b.trek.id,
                "name": b.trek.name,
                "location": b.trek.location,
                "start_date": b.trek.start_date.isoformat(),
                "end_date": b.trek.end_date.isoformat(),
                "duration": (b.trek.end_date - b.trek.start_date).days + 1,
                "difficulty": b.trek.difficulty,
                "cover_image": b.trek.cover_image
            }
        })
    return jsonify(result), 200


@trekker_bp.route("/bookings/<int:booking_id>/cancel", methods=["POST"])
@jwt_required()
def cancel_booking(booking_id):
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user or user.role != 0:
        return jsonify({"message": "Forbidden"}), 403
    
    booking = Booking.query.get_or_404(booking_id)
    trek = booking.trek
    
    if booking.user_id != user.id:
        return jsonify({"message": "You do not have permission to cancel this booking."}), 403
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
    
    return jsonify({"message": f"Your booking for '{trek.name}' has been successfully cancelled."}), 200


@trekker_bp.route("/history", methods=["GET"])
@jwt_required()
def get_history():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user or user.role != 0:
        return jsonify({"message": "Forbidden"}), 403
    
    historical_bookings = Booking.query.filter(
        Booking.user_id == user.id,
        Booking.status.in_(["completed", "cancelled"])
    ).order_by(Booking.booking_date.desc()).all()
    
    result = []
    for b in historical_bookings:
        result.append({
            "id": b.id,
            "status": b.status,
            "booking_date": b.booking_date.isoformat(),
            "cancelled_date": b.cancelled_date.isoformat() if b.cancelled_date else None,
            "trek": {
                "id": b.trek.id,
                "name": b.trek.name,
                "location": b.trek.location,
                "start_date": b.trek.start_date.isoformat(),
                "end_date": b.trek.end_date.isoformat()
            }
        })
    return jsonify(result), 200


@trekker_bp.route("/available_treks", methods=["GET"])
@jwt_required()
def get_available_treks():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user or user.role != 0:
        return jsonify({"message": "Forbidden"}), 403
    
    open_treks = Trek.query.filter_by(status="open").order_by(Trek.start_date.asc()).all()
    booked_trek_ids = [b.trek_id for b in user.bookings if b.status == "booked"]
    unbooked = [t for t in open_treks if t.id not in booked_trek_ids]
    
    result = []
    for t in unbooked:
        result.append({
            "id": t.id,
            "name": t.name,
            "location": t.location,
            "start_date": t.start_date.isoformat(),
            "end_date": t.end_date.isoformat(),
            "duration": (t.end_date - t.start_date).days + 1,
            "difficulty": t.difficulty,
            "price": t.price,
            "cover_image": t.cover_image
        })
    return jsonify(result), 200


@trekker_bp.route("/export_history", methods=["POST"])
@jwt_required()
def export_history():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user or user.role != 0:
        return jsonify({"message": "Forbidden"}), 403
    
    export_booking_history_csv.delay(current_user_id, user.email)
    return jsonify({"message": "Export initiated. You will receive an email shortly with the CSV file attached."}), 202

