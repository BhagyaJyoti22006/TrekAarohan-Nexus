from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import Trek, User, Booking
from cache import cache

public_bp = Blueprint("public", __name__)


@public_bp.route("/treks", methods=["GET"])
@cache.cached(timeout=10, query_string=True)
def get_all_open_treks():
    treks = Trek.query.filter_by(status="open").order_by(Trek.id.desc()).all()
    result = []
    for trek in treks:
        result.append({
            "id": trek.id,
            "name": trek.name,
            "location": trek.location,
            "price": trek.price,
            "start_date": trek.start_date.isoformat(),
            "end_date": trek.end_date.isoformat(),
            "duration": (trek.end_date - trek.start_date).days + 1,
            "difficulty": trek.difficulty,
            "cover_image": trek.cover_image,
            "description": trek.description
        })
    return jsonify(result), 200


@public_bp.route("/treks/featured", methods=["GET"])
@cache.cached(timeout=10, query_string=True)
def get_featured_treks():
    treks = Trek.query.filter_by(status="open").order_by(Trek.id.desc()).limit(3).all()
    result = []
    for trek in treks:
        result.append({
            "id": trek.id,
            "name": trek.name,
            "location": trek.location,
            "price": trek.price,
            "start_date": trek.start_date.isoformat(),
            "end_date": trek.end_date.isoformat(),
            "duration": (trek.end_date - trek.start_date).days + 1,
            "difficulty": trek.difficulty,
            "cover_image": trek.cover_image,
            "description": trek.description
        })
    return jsonify(result), 200


@public_bp.route("/treks/<int:trek_id>", methods=["GET"])
@jwt_required(optional=True)
def get_public_trek(trek_id):
    cache_key = f"trek_details_{trek_id}"
    trek_data = cache.get(cache_key)
    
    if not trek_data:
        trek = Trek.query.get_or_404(trek_id)
        staff = trek.staff
        staff_completed_treks = Trek.query.filter_by(assigned_staff_id=staff.id, status="completed").count() if staff else 0
        
        trek_data = {
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
            "staff_completed_treks": staff_completed_treks
        }
        cache.set(cache_key, trek_data, timeout=10)
    
    booking_status = None
    current_user_id = get_jwt_identity()
    if current_user_id:
        user = User.query.get(current_user_id)
        if user and user.role == 0:
            booking = Booking.query.filter_by(user_id=user.id, trek_id=trek_id).order_by(Booking.id.desc()).first()
            if booking:
                booking_status = booking.status
    
    response_data = trek_data.copy()
    response_data["booking_status"] = booking_status
    
    return jsonify(response_data), 200

