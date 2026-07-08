
# backend/routes/interview.py

from flask import Blueprint, jsonify, session, request
from utils.auth_guard import require_role
from models import Interview, Application, Student, Drive, Company , Placement
from database import db
from datetime import datetime

interview_bp = Blueprint("interview", __name__, url_prefix="/api/interviews")


# -------------------------------
# COMPANY: Schedule Interview
# -------------------------------
@interview_bp.route("/schedule", methods=["POST"])
@require_role("company")
def schedule_interview():
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

    try:
        interview_date = datetime.strptime(data["interview_date"], "%Y-%m-%dT%H:%M")
    except:
        return jsonify({"error": "Invalid date format"}), 400

    # Create interview
    interview = Interview(
        student_id=application.student_id,
        drive_id=application.drive_id,
        company_id=company.id,
        interview_date=interview_date,
        interview_mode=data.get("interview_mode", "Online"),
        location=data.get("location", ""),
        notes=data.get("notes", "")
    )

    db.session.add(interview)
    
    # Update application status to Interview
    application.status = "Interview"
    
    db.session.commit()

    return jsonify({"message": "Interview scheduled successfully"}), 201


# -------------------------------
# COMPANY: Get All Interviews
# -------------------------------
@interview_bp.route("/company", methods=["GET"])
@require_role("company")
def get_company_interviews():
    user_id = session.get("user_id")
    company = Company.query.filter_by(user_id=user_id).first()
    
    if not company:
        return jsonify({"error": "Company not found"}), 404

    interviews = (
        Interview.query
        .filter_by(company_id=company.id)
        .join(Student)
        .join(Drive)
        .all()
    )

    result = []
    for interview in interviews:
        result.append({
            "id": interview.id,
            "student_name": interview.student.user.username if interview.student and interview.student.user else "N/A",
            "student_email": interview.student.user.email if interview.student and interview.student.user else "N/A",
            "drive_title": interview.drive.title if interview.drive else "N/A",
            "interview_date": interview.interview_date.strftime("%Y-%m-%d %H:%M"),
            "interview_mode": interview.interview_mode,
            "location": interview.location,
            "status": interview.status,
            "notes": interview.notes,
            "feedback": interview.feedback
        })

    return jsonify(result)


# -------------------------------
# COMPANY: Update Interview (Add Feedback)
# -------------------------------
@interview_bp.route("/<int:interview_id>/feedback", methods=["PUT"])
@require_role("company")
def update_interview_feedback(interview_id):
    user_id = session.get("user_id")
    company = Company.query.filter_by(user_id=user_id).first()
    
    if not company:
        return jsonify({"error": "Company not found"}), 404

    interview = Interview.query.get(interview_id)
    if not interview or interview.company_id != company.id:
        return jsonify({"error": "Interview not found or unauthorized"}), 404

    data = request.get_json()
    
    interview.feedback = data.get("feedback", "")
    interview.status = data.get("status", interview.status)
    
    db.session.commit()

    return jsonify({"message": "Interview updated successfully"})


# -------------------------------
# STUDENT: Get My Interviews
# -------------------------------
# @interview_bp.route("/student", methods=["GET"])
# @require_role("student")
# def get_student_interviews():
#     user_id = session.get("user_id")
#     student = Student.query.filter_by(user_id=user_id).first()
    
#     if not student:
#         return jsonify({"error": "Student not found"}), 404

#     interviews = (
#         Interview.query
#         .filter_by(student_id=student.id)
#         .join(Drive)
#         .join(Company)
#         .all()
#     )

    
#     result = []
#     for interview in interviews:
#         result.append({
#             "id": interview.id,
#             "company_name": interview.drive.company.name if interview.drive and interview.drive.company else "N/A",
#             "drive_title": interview.drive.title if interview.drive else "N/A",
#             "interview_date": interview.interview_date.strftime("%Y-%m-%d %H:%M"),
#             "interview_mode": interview.interview_mode,
#             "location": interview.location,
#             "status": interview.status,
#             "notes": interview.notes,
#             "feedback": interview.feedback
#         })

#     return jsonify(result)



@interview_bp.route("/student", methods=["GET"])
@require_role("student")
def get_student_interviews():
    user_id = session.get("user_id")
    student = Student.query.filter_by(user_id=user_id).first()

    if not student:
        return jsonify({"error": "Student not found"}), 404

    interviews = (
        Interview.query
        .filter_by(student_id=student.id)
        .join(Drive)
        .join(Company)
        .all()
    )

    result = []

    for interview in interviews:

        status = interview.status

        placement = Placement.query.filter_by(
            student_id=student.id,
            drive_id=interview.drive_id
        ).first()

        if placement and placement.status in ["Accepted", "Joined"]:
            status = "Already Placed"

        result.append({
            "id": interview.id,
            "company_name": interview.drive.company.name if interview.drive and interview.drive.company else "N/A",
            "drive_title": interview.drive.title if interview.drive else "N/A",
            "interview_date": interview.interview_date.strftime("%Y-%m-%d %H:%M"),
            "interview_mode": interview.interview_mode,
            "location": interview.location,
            "status": status,
            "notes": interview.notes,
            "feedback": interview.feedback
        })

    return jsonify(result)