from datetime import datetime
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Trek, User, Booking

staff_bp = Blueprint("staff", __name__)


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

