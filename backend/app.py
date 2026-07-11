from flask import Flask, jsonify
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    CORS(app)
    
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

