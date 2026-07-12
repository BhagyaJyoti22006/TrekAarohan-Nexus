from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import Trek, User, Booking

public_bp = Blueprint("public", __name__)

@public_bp.route("/treks/<int:trek_id>", methods=["GET"])
@jwt_required(optional=True)
def get_public_trek(trek_id):
    trek = Trek.query.get_or_404(trek_id)
    staff = trek.staff
    staff_completed_treks = Trek.query.filter_by(assigned_staff_id=staff.id, status='completed').count() if staff else 0
    
    booking_status = None
    current_user_id = get_jwt_identity()
    if current_user_id:
        user = User.query.get(current_user_id)
        if user and user.role == 0:
            booking = Booking.query.filter_by(user_id=user.id, trek_id=trek.id).first()
            if booking:
                booking_status = booking.status
    
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
        "staff_name": staff.name if staff else "Unassigned",
        "staff_experience": staff.experience if staff else "",
        "staff_completed_treks": staff_completed_treks,
        "booking_status": booking_status
    }), 200

