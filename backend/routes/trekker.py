from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Trek, User, Booking

trekker_bp = Blueprint("trekker", __name__)


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
    if trek.slots_available <= 0:
        return jsonify({"message": "This trek is sold out."}), 400
    
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

