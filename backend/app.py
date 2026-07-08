from flask import Flask
from flask_cors import CORS
from config import Config  # Loads app configuration , such as URI , db , sqlalchemy etc.
from database import init_db # initialize the sqlalchemy database 
from routes.auth import auth_bp  # bp :  blueprint --> A way to organize Flask routes into separate modules/folders.
from routes.admin import admin_bp
from routes.company import company_bp
from routes.student import student_bp
from routes.drives import drive_bp
from routes.interview import interview_bp
from routes.placement import placement_bp


def create_app():
    app = Flask(__name__)  # create flask app
    app.config.from_object(Config)  #  Loads configuration from Config class such as key , db

    # SESSION CONFIG FOR LOCAL DEVELOPMENT
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"   #  Allows cookies in cross-site requests
    app.config["SESSION_COOKIE_SECURE"] = False

    # Allow specific frontend origins only
    CORS(
        app,
        supports_credentials=True,
        origins=[
            "http://127.0.0.1:5173",
            "http://127.0.0.1:5180",
            "http://127.0.0.1:5181",
            "http://localhost:5173",
            "http://localhost:5180",
            "http://localhost:5181",
        ]
    )

    init_db(app)

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")
    app.register_blueprint(company_bp, url_prefix="/api/company")
    app.register_blueprint(student_bp, url_prefix="/api/student")
    app.register_blueprint(drive_bp, url_prefix="/api/drives")
    app.register_blueprint(interview_bp) 
    app.register_blueprint(placement_bp)

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)

