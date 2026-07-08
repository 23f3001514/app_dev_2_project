# backend/routes/drives.py

from flask import Blueprint, jsonify, request
from models import Drive, Company

drive_bp = Blueprint("drives", __name__, url_prefix="/api/drives")


# --------------------------------
# GET APPROVED DRIVES + SEARCH
# --------------------------------
@drive_bp.route("/", methods=["GET"])
def all_drives():
    query = request.args.get("q", "")

    drives = Drive.query.filter_by(status="Approved").all()

    result = []

    for d in drives:
        company = Company.query.get(d.company_id)

        if not company or not company.approved:
            continue

        # Search filter
        if query:
            if query.lower() not in d.title.lower() and \
               query.lower() not in company.name.lower():
                continue

        result.append({
            "drive_id": d.id,
            "title": d.title,
            "company": company.name,
            "eligibility_cgpa": d.eligibility_cgpa,
            "deadline": d.deadline.strftime("%Y-%m-%d"),
        })

    return jsonify(result)