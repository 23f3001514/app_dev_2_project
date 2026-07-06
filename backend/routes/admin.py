# backend/routes/admin.py

from flask import Blueprint, jsonify, request
from models import Company, Drive, Student, Application, User, Interview, Placement
from database import db
from utils.auth_guard import require_role

admin_bp = Blueprint("admin", __name__) # ------> url prefix!!


# ====================================================
# ADMIN DASHBOARD SUMMARY (ENHANCED)
# ====================================================
@admin_bp.route("/dashboard", methods=["GET"])
@require_role("admin")
def admin_dashboard():
    #  Enhanced with interviews and placements
    total_interviews = Interview.query.count()
    total_placements = Placement.query.count()
    students_placed = Student.query.filter_by(is_placed=True).count()
    
    return jsonify({
        "total_students": Student.query.count(),
        "total_companies": Company.query.count(),
        "pending_companies": Company.query.filter_by(approved=False).count(),
        "blacklisted_companies": Company.query.filter_by(blacklisted=True).count(),
        "total_drives": Drive.query.count(),
        "total_applications": Application.query.count(),
        "total_interviews": total_interviews,
        "total_placements": total_placements,
        "students_placed": students_placed
    })

    


# ====================================================
# VIEW PENDING COMPANIES
# ====================================================
@admin_bp.route("/companies/pending", methods=["GET"])
@require_role("admin")
def pending_companies():
    companies = Company.query.filter_by(approved=False).all()

    return jsonify([
        {
            "id": c.id,
            "name": c.name,
            "approved": c.approved,
            "blacklisted": c.blacklisted
        }
        for c in companies
    ])


# ====================================================
# APPROVE COMPANY (AUTO-APPROVE ALL DRIVES)
# ====================================================
@admin_bp.route("/companies/<int:company_id>/approve", methods=["POST"])
@require_role("admin")
def approve_company(company_id):
    company = Company.query.get(company_id)

    if not company:
        return jsonify({"error": "Company not found"}), 404

    if company.blacklisted:
        return jsonify({"error": "Cannot approve blacklisted company"}), 400

    company.approved = True

    # 🔥 Automatically approve all existing drives
    drives = Drive.query.filter_by(company_id=company.id).all()
    for drive in drives:
        drive.status = "Approved"

    db.session.commit()

    return jsonify({
        "message": "Company approved and all its drives automatically approved"
    })


# ====================================================
# BLACKLIST COMPANY (REJECT ALL DRIVES)
# ====================================================
@admin_bp.route("/companies/<int:company_id>/blacklist", methods=["POST"])
@require_role("admin")
def blacklist_company(company_id):
    company = Company.query.get(company_id)

    if not company:
        return jsonify({"error": "Company not found"}), 404

    company.blacklisted = True
    company.approved = False

    # 🔥 Reject all drives of this company
    drives = Drive.query.filter_by(company_id=company.id).all()
    for drive in drives:
        drive.status = "Rejected"

    db.session.commit()

    return jsonify({
        "message": "Company blacklisted and all drives rejected"
    })


# ====================================================
# VIEW ALL DRIVES
# ====================================================
@admin_bp.route("/drives", methods=["GET"])
@require_role("admin")
def view_all_drives():
    drives = Drive.query.all()

    result = []

    for d in drives:
        company = Company.query.get(d.company_id)

        result.append({
            "id": d.id,
            "title": d.title,
            "company_name": company.name if company else None,
            "eligibility_cgpa": d.eligibility_cgpa,
            "deadline": d.deadline.strftime("%Y-%m-%d") if d.deadline else None,
            "status": d.status
        })

    return jsonify(result)


# ====================================================
# REJECT DRIVE (Manual Control if Needed)
# ====================================================
@admin_bp.route("/drives/<int:drive_id>/reject", methods=["POST"])
@require_role("admin")
def reject_drive(drive_id):
    drive = Drive.query.get(drive_id)

    if not drive:
        return jsonify({"error": "Drive not found"}), 404

    drive.status = "Rejected"
    db.session.commit()

    return jsonify({"message": "Drive rejected successfully"})


# ====================================================
#  VIEW ALL INTERVIEWS
# ====================================================
@admin_bp.route("/interviews", methods=["GET"])
@require_role("admin")
def view_all_interviews():
    interviews = (
        Interview.query
        .join(Student)
        .join(Drive)
        .join(Company)
        .all()
    )

    result = []
    for interview in interviews:
        result.append({
            "id": interview.id,
            "student_name": interview.student.user.username if interview.student and interview.student.user else "N/A",
            "company_name": interview.drive.company.name if interview.drive and interview.drive.company else "N/A",
            "drive_title": interview.drive.title if interview.drive else "N/A",
            "interview_date": interview.interview_date.strftime("%Y-%m-%d %H:%M"),
            "interview_mode": interview.interview_mode,
            "status": interview.status
        })

    return jsonify(result)


# ====================================================
#  VIEW ALL PLACEMENTS
# ====================================================
@admin_bp.route("/placements", methods=["GET"])
@require_role("admin")
def view_all_placements():
    placements = (
        Placement.query
        .join(Student)
        .join(Company)
        .join(Drive)
        .all()
    )

    result = []
    for placement in placements:
        result.append({
            "id": placement.id,
            "student_name": placement.student.user.username if placement.student and placement.student.user else "N/A",
            "company_name": placement.company.name if placement.company else "N/A",
            "drive_title": placement.drive.title if placement.drive else "N/A",
            "position": placement.position,
            "salary": placement.salary,
            "joining_date": placement.joining_date.strftime("%Y-%m-%d"),
            "status": placement.status,
            "placed_on": placement.placed_on.strftime("%Y-%m-%d")
        })

    return jsonify(result)


# ====================================================
#  ANALYTICS
# ====================================================
@admin_bp.route("/analytics", methods=["GET"])
@require_role("admin")
def admin_analytics():
    # Application status breakdown
    application_stats = {
        "Applied": Application.query.filter_by(status="Applied").count(),
        "Shortlisted": Application.query.filter_by(status="Shortlisted").count(),
        "Interview": Application.query.filter_by(status="Interview").count(),
        "Offer": Application.query.filter_by(status="Offer").count(),
        "Placed": Application.query.filter_by(status="Placed").count(),
        "Rejected": Application.query.filter_by(status="Rejected").count()
    }

    # Top companies by placements
    top_companies = (
        db.session.query(
            Company.name,
            db.func.count(Placement.id).label('placement_count')
        )
        .join(Placement)
        .group_by(Company.id)
        .order_by(db.desc('placement_count'))
        .limit(5)
        .all()
    )

    # Placement status breakdown
    placement_stats = {
        "Offer": Placement.query.filter_by(status="Offer").count(),
        "Accepted": Placement.query.filter_by(status="Accepted").count(),
        "Joined": Placement.query.filter_by(status="Joined").count(),
        "Declined": Placement.query.filter_by(status="Declined").count()
    }

    return jsonify({
        "application_status": application_stats,
        "placement_status": placement_stats,
        "top_companies": [{"name": name, "placements": count} for name, count in top_companies]
    })


# ====================================================
# ADMIN SEARCH (Students / Companies / Drives / Interviews / Placements)
# ====================================================
@admin_bp.route("/search", methods=["GET"])
@require_role("admin")
def admin_search():
    query = request.args.get("q", "").strip()

    if not query:
        return jsonify({
            "students": [],
            "companies": [],
            "drives": []
        })

    students = Student.query.join(User).filter(
        User.username.ilike(f"%{query}%")
    ).all()

    companies = Company.query.filter(
        Company.name.ilike(f"%{query}%")
    ).all()

    drives = Drive.query.filter(
        Drive.title.ilike(f"%{query}%")
    ).all()

    return jsonify({
        "students": [
            {
                "id": s.id,
                "username": s.user.username,
                "email": s.user.email,
                "branch": s.branch,
                "cgpa": s.cgpa,
                "is_placed" : s.is_placed
            }
            for s in students
        ],
        "companies": [
            {
                "id": c.id,
                "name": c.name,
                "approved": c.approved,
                "blacklisted": c.blacklisted
            }
            for c in companies
        ],
        "drives": [
            {
                "id": d.id,
                "title": d.title,
                "company_name": d.company.name if d.company else None,
                "status": d.status
            }
            for d in drives
        ]
    })

