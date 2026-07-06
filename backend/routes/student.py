# backend/routes/student.py

from flask import Blueprint, jsonify, session, request, send_file
from utils.auth_guard import require_role
from models import Student, Drive, Application, Company, get_upload_folder
from database import db
from datetime import date
from werkzeug.utils import secure_filename
import os

student_bp = Blueprint("student", __name__, url_prefix="/api/student")


# ====================================================
# STUDENT DASHBOARD
# ====================================================
@student_bp.route("/dashboard", methods=["GET"])
@require_role("student")
def student_dashboard():
    user_id = session.get("user_id")

    student = Student.query.filter_by(user_id=user_id).first()
    if not student:
        return jsonify({"error": "Student profile not found"}), 404

    total_applications = Application.query.filter_by(student_id=student.id).count()

    return jsonify({
        #"name" : student.user.username,
        "branch": student.branch,
        "cgpa": student.cgpa,
        "year": student.year,
        "education": student.education,
        "skills": student.skills,
        "phone": student.phone,
        "experience": student.experience,
        "resume_path": student.resume_path,
        "is_placed": student.is_placed,
        "total_applications": total_applications
    })


# ====================================================
# UPDATE STUDENT PROFILE
# ====================================================
@student_bp.route("/profile", methods=["PUT"])
@require_role("student")
def update_profile():
    user_id = session.get("user_id")
    student = Student.query.filter_by(user_id=user_id).first()

    if not student:
        return jsonify({"error": "Student not found"}), 404

    data = request.get_json()

    student.branch = data.get("branch", student.branch)
    student.cgpa = data.get("cgpa", student.cgpa)
    student.year = data.get("year", student.year)
    student.education = data.get("education", student.education)
    student.skills = data.get("skills", student.skills)
    student.phone = data.get("phone", student.phone)
    student.experience = data.get("experience", student.experience)

    db.session.commit()

    return jsonify({"message": "Profile updated successfully"})


# ====================================================
# VIEW APPROVED DRIVES (with Search)
# ====================================================
@student_bp.route("/drives", methods=["GET"])
@require_role("student")
def view_drives():
    user_id = session.get("user_id")
    student = Student.query.filter_by(user_id=user_id).first()
    if not student:
        return jsonify({"error": "Student profile not found"}), 404

    today = date.today()
    search_query = request.args.get("q", "").strip()

    query = (
        db.session.query(Drive)
        .join(Company)
        .filter(
            Drive.status == "Approved",
            Company.approved == True,
            Company.blacklisted == False,
            Drive.deadline >= today,
            Drive.job_status == "Active"
        )
    )

    if search_query:
        query = query.filter(
            db.or_(
                Drive.title.ilike(f"%{search_query}%"),
                Company.name.ilike(f"%{search_query}%")
            )
        )

    drives = query.all()

    result = []
    for d in drives:
        if student.cgpa >= d.eligibility_cgpa:
            app = Application.query.filter_by(
                student_id=student.id,
                drive_id=d.id
            ).first()

            status_msg = None
            application_status = None

            if app:
                application_status = app.status
                if app.status == "Placed":
                    status_msg = f"Congratulations! You've been placed at {d.company.name} 🎉"
                elif app.status == "Offer":
                    status_msg = f"You have an offer from {d.company.name}! 🎊"
                elif app.status == "Rejected":
                    status_msg = f"Sorry! You've been rejected by {d.company.name} 😔"

            result.append({
                "drive_id": d.id,
                "title": d.title,
                "company": d.company.name,
                "description": d.description,
                "required_skills": d.required_skills,
                "experience_required": d.experience_required,
                "salary": d.salary,
                "benefits": d.benefits,
                "eligibility_cgpa": d.eligibility_cgpa,
                "deadline": d.deadline.strftime("%Y-%m-%d"),
                "application_status": application_status,
                "status_msg": status_msg
            })

    return jsonify(result)


# ====================================================
# APPLY FOR A DRIVE
# ====================================================
@student_bp.route("/apply/<int:drive_id>", methods=["POST"])
@require_role("student")
def apply_drive(drive_id):
    user_id = session.get("user_id")
    student = Student.query.filter_by(user_id=user_id).first()
    if not student:
        return jsonify({"error": "Student not found"}), 404

    if student.is_placed:
        return jsonify({"error": "You are already placed and cannot apply"}), 400

    drive = Drive.query.get(drive_id)
    if not drive:
        return jsonify({"error": "Drive not found"}), 404

    if drive.status != "Approved":
        return jsonify({"error": "Drive not approved"}), 400

    if drive.job_status != "Active":
        return jsonify({"error": "This job is closed"}), 400

    existing = Application.query.filter_by(
        student_id=student.id,
        drive_id=drive.id
    ).first()
    if existing:
        return jsonify({"error": "Already applied"}), 400

    application = Application(
        student_id=student.id,
        drive_id=drive.id,
        status="Applied"
    )
    db.session.add(application)
    db.session.commit()

    return jsonify({"message": "Application successful"}), 201


# ====================================================
# VIEW MY APPLICATIONS
# ====================================================
@student_bp.route("/applications", methods=["GET"])
@require_role("student")
def view_applications():
    user_id = session.get("user_id")
    student = Student.query.filter_by(user_id=user_id).first()
    if not student:
        return jsonify({"error": "Student not found"}), 404

    applications = (
        db.session.query(Application)
        .join(Drive)
        .filter(Application.student_id == student.id)
        .all()
    )

    result = []
    for app in applications:
        result.append({
            "application_id": app.id,
            "drive_id": app.drive.id,
            "drive_title": app.drive.title,
            "company": app.drive.company.name,
            "status": app.status,
            "feedback": app.feedback,
            "applied_on": app.applied_on.strftime("%Y-%m-%d %H:%M")
        })

    return jsonify(result)


# ====================================================
# UPLOAD RESUME
# ====================================================
@student_bp.route("/resume/upload", methods=["POST"])
@require_role("student")
def upload_resume():
    user_id = session.get("user_id")
    student = Student.query.filter_by(user_id=user_id).first()

    if not student:
        return jsonify({"error": "Student not found"}), 404

    if "resume" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["resume"]

    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    # Validate file extension
    allowed_extensions = {"pdf", "doc", "docx"}
    if not (
        "." in file.filename and
        file.filename.rsplit(".", 1)[1].lower() in allowed_extensions
    ):
        return jsonify({"error": "Only PDF, DOC, and DOCX files are allowed"}), 400

    # Validate file size (max 5MB)
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)
    if file_size > 5 * 1024 * 1024:
        return jsonify({"error": "File size must be under 5MB"}), 400

    # Create safe unique filename
    filename = secure_filename(file.filename)
    name, ext = os.path.splitext(filename)
    unique_filename = f"student_{student.id}_{name}{ext}"

    # Save file to uploads folder
    upload_folder = get_upload_folder()
    filepath = os.path.join(upload_folder, unique_filename)

    # Delete old resume file if exists
    if student.resume_path:
        old_filepath = os.path.join(upload_folder, student.resume_path)
        if os.path.exists(old_filepath):
            os.remove(old_filepath)

    file.save(filepath)

    # Update student record
    student.resume_path = unique_filename
    db.session.commit()

    return jsonify({
        "message": "Resume uploaded successfully",
        "filename": unique_filename
    }), 200


# ====================================================
#  DOWNLOAD RESUME
# ====================================================
@student_bp.route("/resume/download", methods=["GET"])
@require_role("student")
def download_resume():
    user_id = session.get("user_id")
    student = Student.query.filter_by(user_id=user_id).first()

    if not student:
        return jsonify({"error": "Student not found"}), 404

    if not student.resume_path:
        return jsonify({"error": "No resume uploaded yet"}), 404

    upload_folder = get_upload_folder()
    filepath = os.path.join(upload_folder, student.resume_path)

    if not os.path.exists(filepath):
        # Clean up stale DB entry
        student.resume_path = None
        db.session.commit()
        return jsonify({"error": "Resume file not found on server"}), 404

    return send_file(filepath, as_attachment=True)


# ====================================================
# DELETE RESUME
# ====================================================
@student_bp.route("/resume/delete", methods=["DELETE"])
@require_role("student")
def delete_resume():
    user_id = session.get("user_id")
    student = Student.query.filter_by(user_id=user_id).first()

    if not student:
        return jsonify({"error": "Student not found"}), 404

    if not student.resume_path:
        return jsonify({"error": "No resume to delete"}), 404

    upload_folder = get_upload_folder()
    filepath = os.path.join(upload_folder, student.resume_path)

    # Delete physical file if it exists
    if os.path.exists(filepath):
        os.remove(filepath)

    # Clear resume path in DB
    student.resume_path = None
    db.session.commit()

    return jsonify({"message": "Resume deleted successfully"}), 200

