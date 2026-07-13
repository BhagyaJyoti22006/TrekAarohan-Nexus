from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from models import db

def create_app():
    app = Flask(__name__)
    
    # Core Configurations
    app.config["SECRET_KEY"] = "tan-super-secret-key"
    app.config["ROLE_MAP"] = {0: "trekker", 1: "staff", 2: "admin"}
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///tan.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["JWT_SECRET_KEY"] = "super-secret-tan-jwt"
    
    # Initialize Application
    CORS(app)
    db.init_app(app)
    
    jwt = JWTManager(app)
    
    # Register Blueprints
    from routes.auth import auth_bp
    from routes.admin import admin_bp
    from routes.staff import staff_bp
    from routes.trekker import trekker_bp
    from routes.public import public_bp
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")
    app.register_blueprint(staff_bp, url_prefix="/api/staff")
    app.register_blueprint(trekker_bp, url_prefix="/api/trekker")
    app.register_blueprint(public_bp, url_prefix="/api")
    
    # Ping Route
    @app.route("/api/ping", methods=["GET"])
    def ping():
        return jsonify({
            "status": "success", 
            "message": "TAN Backend API is running!"
        }), 200
    
    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5000)

