# backend/config.py

class Config:
    SECRET_KEY = "placement-portal-secret"
    SQLALCHEMY_DATABASE_URI = "sqlite:///placement_portal.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = True
