from datetime import datetime
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Trek, User, Booking

staff_bp = Blueprint("staff", __name__)


@staff_bp.route("/dashboard", methods=["GET"])
@jwt_required()
def get_dashboard():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user or user.role != 1:
        return jsonify({"message": "Forbidden."}), 403
    
    assigned_treks = Trek.query.filter_by(assigned_staff_id=user.id).all()
    total_treks = len(assigned_treks)
    
    active_trek_ids = [t.id for t in assigned_treks if t.status not in ["completed", "cancelled"]]
    active_participants = 0
    if active_trek_ids:
        active_participants = Booking.query.filter(Booking.trek_id.in_(active_trek_ids), Booking.status == "booked").count()
    
    all_trek_ids = [t.id for t in assigned_treks]
    unique_trekkers = 0
    if all_trek_ids:
        unique_trekkers = db.session.query(Booking.user_id).filter(Booking.trek_id.in_(all_trek_ids), Booking.status == "booked").distinct().count()
    
    ongoing_treks = [t for t in assigned_treks if t.status == "ongoing"]
    serialized_ongoing = []
    for t in ongoing_treks:
        serialized_ongoing.append({
            "id": t.id,
            "name": t.name,
            "location": t.location,
            "start_date": t.start_date.isoformat(),
            "end_date": t.end_date.isoformat(),
            "cover_image": t.cover_image
        })
    
    return jsonify({
        "total_treks": total_treks,
        "active_participants": active_participants,
        "unique_trekkers": unique_trekkers,
        "ongoing_treks": serialized_ongoing
    }), 200


@staff_bp.route("/profile", methods=["GET"])
@jwt_required()
def get_profile():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user or user.role != 1:
        return jsonify({"message": "Forbidden."}), 403
    
    return jsonify({
        "username": user.username,
        "email": user.email,
        "name": user.name,
        "phone": user.phone,
        "emergency_phone": user.emergency_phone,
        "emergency_relation": user.emergency_relation,
        "experience": user.experience,
        "is_blacklisted": user.is_blacklisted
    }), 200


@staff_bp.route("/profile", methods=["PUT"])
@jwt_required()
def update_profile():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user or user.role != 1:
        return jsonify({"message": "Forbidden."}), 403
    
    data = request.json
    if not data:
        return jsonify({"message": "No data provided."}), 400
    
    name = data.get("name")
    email = data.get("email")
    phone = data.get("phone")
    emergency_phone = data.get("emergency_phone")
    emergency_relation = data.get("emergency_relation")
    experience = data.get("experience")
    
    if not name or not phone or not email:
        return jsonify({"message": "Name, Email, and Phone number are required."}), 400
    
    existing_user = User.query.filter(User.email == email, User.id != current_user_id).first()
    if existing_user:
        return jsonify({"message": "Email is already registered by another user."}), 400
    
    user.name = name
    user.email = email
    user.phone = phone
    user.emergency_phone = emergency_phone
    user.emergency_relation = emergency_relation
    user.experience = experience
    
    db.session.commit()
    
    return jsonify({"message": "Profile updated successfully."}), 200


@staff_bp.route("/participants", methods=["GET"])
@jwt_required()
def get_participants():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user or user.role != 1:
        return jsonify({"message": "Forbidden. Staff access only."}), 403
    
    assigned_treks = Trek.query.filter_by(assigned_staff_id=user.id).all()
    trek_ids = [t.id for t in assigned_treks]
    if not trek_ids:
        return jsonify([]), 200
    bookings = Booking.query.filter(Booking.trek_id.in_(trek_ids)).order_by(Booking.booking_date.desc()).all()
    
    result = []
    for b in bookings:
        result.append({
            "id": b.id,
            "status": b.status,
            "booking_date": b.booking_date.isoformat(),
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


@staff_bp.route("/cancel_booking/<int:booking_id>", methods=["POST"])
@jwt_required()
def cancel_booking(booking_id):
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user or user.role != 1:
        return jsonify({"message": "Forbidden. Staff access only."}), 403
    
    booking = Booking.query.get_or_404(booking_id)
    trek = booking.trek
    
    if trek.assigned_staff_id != user.id:
        return jsonify({"message": "You do not have permission to manage this booking."}), 403
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


@staff_bp.route("/treks", methods=["GET"])
@jwt_required()
def get_treks():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user or user.role != 1:
        return jsonify({"message": "Forbidden."}), 403
    
    treks = Trek.query.filter_by(assigned_staff_id=user.id).all()
    result = []
    for trek in treks:
        result.append({
            "id": trek.id,
            "name": trek.name,
            "start_date": trek.start_date.isoformat(),
            "end_date": trek.end_date.isoformat(),
            "status": trek.status,
            "slots_available": trek.slots_available,
            "active_participants": len([b for b in trek.bookings if b.status in ["booked", "completed"]])
        })
    return jsonify(result), 200


@staff_bp.route("/treks/<int:trek_id>", methods=["GET"])
@jwt_required()
def get_trek(trek_id):
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user or user.role != 1:
        return jsonify({"message": "Forbidden."}), 403
    
    trek = Trek.query.get_or_404(trek_id)
    if trek.assigned_staff_id != user.id:
        return jsonify({"message": "You do not have permission to manage this trek."}), 403
    
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
        "price": trek.price,
        "difficulty": trek.difficulty,
        "status": trek.status,
        "slots_available": trek.slots_available,
        "start_date": trek.start_date.isoformat(),
        "end_date": trek.end_date.isoformat(),
        "duration": (trek.end_date - trek.start_date).days + 1,
        "cover_image": trek.cover_image,
        "description": trek.description,
        "bookings": serialized_bookings
    }), 200


@staff_bp.route("/treks/<int:trek_id>", methods=["POST"])
@jwt_required()
def update_trek(trek_id):
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user or user.role != 1:
        return jsonify({"message": "Forbidden."}), 403
    
    trek = Trek.query.get_or_404(trek_id)
    if trek.assigned_staff_id != user.id:
        return jsonify({"message": "You do not have permission to manage this trek."}), 403
    if trek.status in ["completed", "cancelled"]:
        return jsonify({"message": "This trek has concluded and cannot be managed."}), 400
    data = request.json
    if not data:
        return jsonify({"message": "No data provided."}), 400
    
    new_status = data.get("status")
    new_slots = data.get("slots_available")
    if new_status in ["open", "full", "ongoing", "completed", "cancelled"]:
        trek.status = new_status
    if new_slots is not None:
        try:
            trek.slots_available = int(new_slots)
        except ValueError:
            pass
    
    db.session.commit()
    
    return jsonify({"message": "Trek updated successfully."}), 200

