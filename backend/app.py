from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from celery import Celery, Task
from celery.schedules import crontab
from models import db
from cache import cache
from mail import mail


def create_app():
    app = Flask(__name__)
    
    # Core Configurations
    app.config["SECRET_KEY"] = "tan-super-secret-key"
    app.config["ROLE_MAP"] = {0: "trekker", 1: "staff", 2: "admin"}
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///tan.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["JWT_SECRET_KEY"] = "super-secret-tan-jwt"
    
    # Cache Configurations
    app.config["CACHE_TYPE"] = "RedisCache"
    app.config["CACHE_REDIS_URL"] = "redis://127.0.0.1:6379/0"
    app.config["CACHE_DEFAULT_TIMEOUT"] = 60
    
    # Celery Configurations
    app.config["CELERY_BROKER_URL"] = "redis://127.0.0.1:6379/0"
    app.config["CELERY_RESULT_BACKEND"] = "redis://127.0.0.1:6379/0"
    app.config["CELERY_TIMEZONE"] = "UTC"
    app.config["CELERY_IMPORTS"] = ["tasks"]
    
    # MailHog Configurations
    app.config["MAIL_SERVER"] = "127.0.0.1"
    app.config["MAIL_PORT"] = 1025
    app.config["MAIL_USE_TLS"] = False
    app.config["MAIL_USE_SSL"] = False
    app.config["MAIL_DEFAULT_SENDER"] = "system@tan.com"
    
    # Initialize Application
    CORS(app)
    jwt = JWTManager(app)
    db.init_app(app)
    cache.init_app(app)
    mail.init_app(app)
    
    # Initialize Celery
    class FlaskTask(Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    celery_app = Celery(app.name, task_cls=FlaskTask)
    celery_app.config_from_object(app.config, namespace="CELERY")
    celery_app.set_default()
    app.extensions["celery"] = celery_app
    
    # Celery Beat Schedule
    celery_app.conf.beat_schedule = {
        "daily-trek-reminders": {
            "task": "tasks.send_daily_reminders",
            #"schedule": crontab(hour=8, minute=0), 
            "schedule": crontab(minute="*"), 
        },
        "monthly-admin-reports": {
            "task": "tasks.send_monthly_reports",
            #"schedule": crontab(hour=6, minute=0, day_of_month="1"), 
            "schedule": crontab(minute="*/2"),
        }
    }
    
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

