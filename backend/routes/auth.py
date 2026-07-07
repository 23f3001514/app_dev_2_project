# backend/routes/auth.py

from flask import Blueprint, request, jsonify, session
from models import User, Student, Company
from database import db

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register/student", methods=["POST"])
def register_student():
    data = request.json

    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"error": "Email already exists"}), 400

    user = User(
        username=data["username"],
        email=data["email"],
        password=data["password"],
        role="student"
    )
    db.session.add(user)
    db.session.commit()

    student = Student(
        user_id=user.id,
        branch=data.get("branch"),
        cgpa=data.get("cgpa"),
        year=data.get("year"),
        # 🆕 NEW FIELDS
        education=data.get("education"),
        skills=data.get("skills"),
        phone=data.get("phone"),
        experience=data.get("experience")
    )
    db.session.add(student)
    db.session.commit()

    return jsonify({"message": "Student registered"}), 201


@auth_bp.route("/register/company", methods=["POST"])
def register_company():
    data = request.json

    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"error": "Email already exists"}), 400

    user = User(
        username=data["username"],
        email=data["email"],
        password=data["password"],
        role="company"
    )
    db.session.add(user)
    db.session.commit()

    company = Company(
        user_id=user.id,
        name=data.get("name"),
        # 🆕 NEW FIELDS
        industry=data.get("industry"),
        location=data.get("location"),
        website=data.get("website"),
        description=data.get("description"),
        approved=False
    )
    db.session.add(company)
    db.session.commit()

    return jsonify({"message": "Company registered, waiting for admin approval"}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json

    user = User.query.filter_by(
        email=data["email"],
        password=data["password"]
    ).first()

    if not user:
        return jsonify({"error": "Invalid credentials"}), 401

    session["user_id"] = user.id
    session["role"] = user.role

    return jsonify({"message": "Login successful", "role": user.role})


@auth_bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"message": "Logged out"})


















# --------------> newly added

@auth_bp.route("/check", methods=["GET"])
def check_auth():
    if "user_id" not in session:
        return jsonify({"error": "Not authenticated"}), 401
    
    user_id = session.get("user_id")
    role = session.get("role")
    
    user = User.query.get(user_id)
    
    return jsonify({
        "role": role,
        "username": user.username if user else "User"
    })

