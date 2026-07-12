from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from werkzeug.security import generate_password_hash
from models import db, User

admin_bp = Blueprint("admin", __name__)

def admin_required():
    claims = get_jwt()
    if claims.get("role") != 2:
        return False
    return True


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
    password = data.get("password")
    experience = data.get("experience", "")
    
    if not all([username, name, email, phone, password]):
        return jsonify({"error": "All fields are required"}), 400
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

