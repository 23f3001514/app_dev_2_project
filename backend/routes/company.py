
# backend/routes/company.py

from flask import Blueprint, jsonify, session, request, send_file
from utils.auth_guard import require_role
from models import Company, Drive, Application, Student, User, get_upload_folder
from database import db
from datetime import datetime
import os

company_bp = Blueprint("company", __name__, url_prefix="/api/company")


# ====================================================
# DASHBOARD
# ====================================================
@company_bp.route("/dashboard", methods=["GET"])
@require_role("company")
def company_dashboard():
    user_id = session.get("user_id")
    company = Company.query.filter_by(user_id=user_id).first()
    if not company:
        return jsonify({"error": "Company not found"}), 404

    drives = Drive.query.filter_by(company_id=company.id).all()
    drive_ids = [d.id for d in drives]

    total_applicants = (
        Application.query.filter(Application.drive_id.in_(drive_ids)).count()
        if drive_ids else 0
    )

    return jsonify({
        "company_name": company.name,
        "username": company.user.username if company.user else "N/A",
        "industry": company.industry,
        "location": company.location,
        "website": company.website,
        "description": company.description,
        "approved": company.approved,
        "blacklisted": company.blacklisted,
        "total_drives": len(drives),
        "total_applicants": total_applicants
    })


# ====================================================
# GET DRIVES
# ====================================================
@company_bp.route("/drives", methods=["GET"])
@require_role("company")
def get_drives():
    user_id = session.get("user_id")
    company = Company.query.filter_by(user_id=user_id).first()
    if not company:
        return jsonify({"error": "Company not found"}), 404

    drives = Drive.query.filter_by(company_id=company.id).all()
    return jsonify([
        {
            "id": d.id,
            "title": d.title,
            "description": d.description,
            "required_skills": d.required_skills,
            "experience_required": d.experience_required,
            "salary": d.salary,
            "benefits": d.benefits,
            "eligibility_cgpa": d.eligibility_cgpa,
            "deadline": d.deadline.strftime("%Y-%m-%d"),
            "job_status": d.job_status,
            "status": d.status
        }
        for d in drives
    ])


# ====================================================
# CREATE DRIVE
# ====================================================
@company_bp.route("/drives", methods=["POST"])
@require_role("company")
def create_drive():
    user_id = session.get("user_id")
    data = request.get_json()
    company = Company.query.filter_by(user_id=user_id).first()
    if not company:
        return jsonify({"error": "Company not found"}), 404

    if company.blacklisted:
        return jsonify({"error": "Company is blacklisted"}), 403

    try:
        deadline = datetime.strptime(data["deadline"], "%Y-%m-%d").date()
    except:
        return jsonify({"error": "Invalid date format"}), 400

    drive = Drive(
        company_id=company.id,
        title=data["title"],
        description=data.get("description"),
        required_skills=data.get("required_skills"),
        experience_required=data.get("experience_required"),
        salary=data.get("salary"),
        benefits=data.get("benefits"),
        eligibility_cgpa=data["eligibility_cgpa"],
        deadline=deadline,
        job_status="Active",
        status="Approved" if company.approved else "Pending"
    )

    db.session.add(drive)
    db.session.commit()
    return jsonify({"message": "Drive created"}), 201


# ====================================================
# UPDATE JOB STATUS
# ====================================================
@company_bp.route("/drives/<int:drive_id>/status", methods=["PUT"])
@require_role("company")
def update_job_status(drive_id):
    user_id = session.get("user_id")
    company = Company.query.filter_by(user_id=user_id).first()
    if not company:
        return jsonify({"error": "Company not found"}), 404

    drive = Drive.query.get(drive_id)
    if not drive or drive.company_id != company.id:
        return jsonify({"error": "Drive not found or unauthorized"}), 404

    data = request.get_json()
    new_status = data.get("job_status")

    if new_status not in ["Active", "Closed"]:
        return jsonify({"error": "Invalid status"}), 400

    drive.job_status = new_status
    db.session.commit()

    return jsonify({"message": f"Job status updated to {new_status}"})


# ====================================================
# DELETE DRIVE
# ====================================================
@company_bp.route("/drives/<int:drive_id>", methods=["DELETE"])
@require_role("company")
def delete_drive(drive_id):
    user_id = session.get("user_id")
    company = Company.query.filter_by(user_id=user_id).first()
    if not company:
        return jsonify({"error": "Company not found"}), 404

    drive = Drive.query.get(drive_id)
    if not drive or drive.company_id != company.id:
        return jsonify({"error": "Drive not found or unauthorized"}), 404

    db.session.delete(drive)
    db.session.commit()
    return jsonify({"message": "Drive deleted"})


# ====================================================
# VIEW APPLICATIONS
# ====================================================
@company_bp.route("/applications", methods=["GET"])
@require_role("company")
def view_applications():
    user_id = session.get("user_id")
    company = Company.query.filter_by(user_id=user_id).first()
    if not company:
        return jsonify({"error": "Company not found"}), 404

    applications = (
        db.session.query(Application)
        .join(Application.drive)
        .join(Application.student)
        .join(Student.user)
        .filter(Drive.company_id == company.id)
        .all()
    )

    result = []
    for app in applications:
        result.append({
            "application_id": app.id,
            "drive_title": app.drive.title if app.drive else "N/A",
            "drive_id": app.drive_id,
            "student_username": app.student.user.username if app.student and app.student.user else "N/A",
            "student_email": app.student.user.email if app.student and app.student.user else "N/A",
            "student_branch": app.student.branch if app.student else "N/A",
            "student_cgpa": app.student.cgpa if app.student else "N/A",
            "student_skills": app.student.skills if app.student else "N/A",
            "student_phone": app.student.phone if app.student else "N/A",
            "has_resume": bool(app.student.resume_path) if app.student else False,
            "status": app.status,
            "feedback": app.feedback or "",
            "applied_on": app.applied_on.strftime("%Y-%m-%d %H:%M")
        })

    return jsonify(result)


# ====================================================
# UPDATE APPLICATION STATUS
# ====================================================
@company_bp.route("/applications/<int:app_id>/status", methods=["PUT"])
@require_role("company")
def update_application_status(app_id):
    user_id = session.get("user_id")
    company = Company.query.filter_by(user_id=user_id).first()
    if not company:
        return jsonify({"error": "Company not found"}), 404

    application = Application.query.get(app_id)
    if not application:
        return jsonify({"error": "Application not found"}), 404

    if not application.drive or application.drive.company_id != company.id:
        return jsonify({"error": "Unauthorized"}), 403

    data = request.get_json()
    new_status = data.get("status")
    feedback = data.get("feedback", "")

    valid_statuses = ["Applied", "Shortlisted", "Interview", "Offer", "Placed", "Rejected"]
    if new_status not in valid_statuses:
        return jsonify({"error": "Invalid status"}), 400

    application.status = new_status
    application.feedback = feedback

    # If placed, update student's is_placed flag
    if new_status == "Placed":
        student = Student.query.get(application.student_id)
        if student:
            student.is_placed = True

    db.session.commit()
    return jsonify({"message": "Status updated successfully"})