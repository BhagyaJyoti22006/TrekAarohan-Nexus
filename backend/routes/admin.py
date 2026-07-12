import os
from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
from models import db, User, Trek

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
    return jsonify({
        "id": trek.id,
        "name": trek.name,
        "location": trek.location,
        "description": trek.description,
        "start_date": trek.start_date.isoformat(),
        "end_date": trek.end_date.isoformat(),
        "difficulty": trek.difficulty,
        "status": trek.status,
        "slots_available": trek.slots_available,
        "price": trek.price,
        "cover_image": trek.cover_image,
        "assigned_staff_id": trek.assigned_staff_id
    }), 200


@admin_bp.route("/treks/<int:trek_id>", methods=["PUT"])
@jwt_required()
def update_trek(trek_id):
    if not admin_required():
        return jsonify({"error": "Admin access required"}), 403
    
    trek = Trek.query.get_or_404(trek_id)
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
    trek.slots_available = int(slots_available)
    trek.price = float(price)
    trek.assigned_staff_id = int(assigned_staff_id)
    if status:
        trek.status = status
    
    db.session.commit()
    return jsonify({"message": "Trek updated successfully"}), 200

