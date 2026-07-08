# backend/routes/placement.py

from flask import Blueprint, jsonify, session, request
from utils.auth_guard import require_role
from models import Placement, Application, Student, Drive, Company
from database import db
from datetime import datetime

placement_bp = Blueprint("placement", __name__, url_prefix="/api/placements")


# -------------------------------
# COMPANY: Create Placement (Send Offer)
# -------------------------------
@placement_bp.route("/create", methods=["POST"])
@require_role("company")
def create_placement():
    user_id = session.get("user_id")
    company = Company.query.filter_by(user_id=user_id).first()
    
    if not company:
        return jsonify({"error": "Company not found"}), 404

    data = request.get_json()
    
    # Validate application
    application = Application.query.get(data.get("application_id"))
    if not application:
        return jsonify({"error": "Application not found"}), 404
    
    if application.drive.company_id != company.id:
        return jsonify({"error": "Unauthorized"}), 403

    # Check if placement already exists
    existing = Placement.query.filter_by(
        student_id=application.student_id,
        drive_id=application.drive_id
    ).first()
    
    if existing:
        return jsonify({"error": "Placement already exists for this student"}), 400

    try:
        joining_date = datetime.strptime(data["joining_date"], "%Y-%m-%d").date()
    except:
        return jsonify({"error": "Invalid date format"}), 400

    # Create placement
    placement = Placement(
        student_id=application.student_id,
        company_id=company.id,
        drive_id=application.drive_id,
        position=data.get("position", application.drive.title),
        salary=data.get("salary", application.drive.salary),
        joining_date=joining_date,
        status="Offer"
    )

    db.session.add(placement)
    
    # Update application status to Offer
    application.status = "Offer"
    
    db.session.commit()

    return jsonify({"message": "Offer sent successfully"}), 201


# -------------------------------
# COMPANY: Get All Placements
# -------------------------------
@placement_bp.route("/company", methods=["GET"])
@require_role("company")
def get_company_placements():
    user_id = session.get("user_id")
    company = Company.query.filter_by(user_id=user_id).first()
    
    if not company:
        return jsonify({"error": "Company not found"}), 404

    placements = (
        Placement.query
        .filter_by(company_id=company.id)
        .join(Student)
        .join(Drive)
        .all()
    )

    result = []
    for placement in placements:
        result.append({
            "id": placement.id,
            "student_name": placement.student.user.username if placement.student and placement.student.user else "N/A",
            "student_email": placement.student.user.email if placement.student and placement.student.user else "N/A",
            "drive_title": placement.drive.title if placement.drive else "N/A",
            "position": placement.position,
            "salary": placement.salary,
            "joining_date": placement.joining_date.strftime("%Y-%m-%d"),
            "status": placement.status,
            "placed_on": placement.placed_on.strftime("%Y-%m-%d")
        })

    return jsonify(result)


# -------------------------------
# COMPANY: Update Placement Status
# -------------------------------
@placement_bp.route("/<int:placement_id>/status", methods=["PUT"])
@require_role("company")
def update_placement_status(placement_id):
    user_id = session.get("user_id")
    company = Company.query.filter_by(user_id=user_id).first()
    
    if not company:
        return jsonify({"error": "Company not found"}), 404

    placement = Placement.query.get(placement_id)
    if not placement or placement.company_id != company.id:
        return jsonify({"error": "Placement not found or unauthorized"}), 404

    data = request.get_json()
    new_status = data.get("status")
    
    if new_status not in ["Offer", "Accepted", "Joined", "Declined"]:
        return jsonify({"error": "Invalid status"}), 400

    placement.status = new_status
    
    # If marked as Joined, update application and student
    if new_status == "Joined":
        application = Application.query.filter_by(
            student_id=placement.student_id,
            drive_id=placement.drive_id
        ).first()
        
        if application:
            application.status = "Placed"
        
        student = Student.query.get(placement.student_id)
        if student:
            student.is_placed = True
    
    db.session.commit()

    return jsonify({"message": "Placement status updated successfully"})


# -------------------------------
# STUDENT: Get My Placements
# -------------------------------
@placement_bp.route("/student", methods=["GET"])
@require_role("student")
def get_student_placements():
    user_id = session.get("user_id")
    student = Student.query.filter_by(user_id=user_id).first()
    
    if not student:
        return jsonify({"error": "Student not found"}), 404

    placements = (
        Placement.query
        .filter_by(student_id=student.id)
        .join(Company)
        .join(Drive)
        .all()
    )

    result = []
    for placement in placements:
        result.append({
            "id": placement.id,
            "company_name": placement.company.name if placement.company else "N/A",
            "drive_title": placement.drive.title if placement.drive else "N/A",
            "position": placement.position,
            "salary": placement.salary,
            "joining_date": placement.joining_date.strftime("%Y-%m-%d"),
            "status": placement.status,
            "placed_on": placement.placed_on.strftime("%Y-%m-%d"),
            "offer_letter_path": placement.offer_letter_path
        })

    return jsonify(result)


# -------------------------------
# STUDENT: Accept/Decline Offer
# -------------------------------
@placement_bp.route("/<int:placement_id>/respond", methods=["PUT"])
@require_role("student")
def respond_to_offer(placement_id):
    user_id = session.get("user_id")
    student = Student.query.filter_by(user_id=user_id).first()
    
    if not student:
        return jsonify({"error": "Student not found"}), 404

    placement = Placement.query.get(placement_id)
    if not placement or placement.student_id != student.id:
        return jsonify({"error": "Placement not found or unauthorized"}), 404

    data = request.get_json()
    response = data.get("response")  # "accept" or "decline"
    
    if response == "accept":
        placement.status = "Accepted"
        student.is_placed = True
        
        # Update application status
        application = Application.query.filter_by(
            student_id=student.id,
            drive_id=placement.drive_id
        ).first()
        
        if application:
            application.status = "Placed"
            
    elif response == "decline":
        placement.status = "Declined"
    else:
        return jsonify({"error": "Invalid response"}), 400
    
    db.session.commit()

    return jsonify({"message": f"Offer {response}ed successfully"})
