from database import db
from datetime import datetime
import os


# Helper function for upload folder
def get_upload_folder():
    upload_folder = os.path.join(os.path.dirname(__file__), 'uploads', 'resumes')
    os.makedirs(upload_folder, exist_ok=True)
    return upload_folder


# -------------------------------
# User Model
# -------------------------------
class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

    role = db.Column(db.String(20), nullable=False)  # admin/student/company

    # Relationships
    student = db.relationship("Student", back_populates="user", uselist=False)
    company = db.relationship("Company", back_populates="user", uselist=False)

    def __repr__(self):
        return f"<User {self.username}>"


# -------------------------------
# Student Model 
# -------------------------------
class Student(db.Model):
    __tablename__ = "student"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    # Basic Info
    branch = db.Column(db.String(50))
    cgpa = db.Column(db.Float)
    year = db.Column(db.Integer)

    # NEW FIELDS
    education = db.Column(db.Text)
    skills = db.Column(db.Text)
    resume_path = db.Column(db.String(255))
    experience = db.Column(db.Text)
    phone = db.Column(db.String(15))

    # Placement Status
    is_placed = db.Column(db.Boolean, default=False)

    # Relationships
    user = db.relationship("User", back_populates="student")
    applications = db.relationship("Application", back_populates="student")
    placements = db.relationship("Placement", back_populates="student")
    interviews = db.relationship("Interview", back_populates="student")


# -------------------------------
# Company Model
# -------------------------------
class Company(db.Model):
    __tablename__ = "company"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    name = db.Column(db.String(100))

    # NEW FIELDS
    industry = db.Column(db.String(100))
    location = db.Column(db.String(100))
    website = db.Column(db.String(255))
    description = db.Column(db.Text)

    approved = db.Column(db.Boolean, default=False)
    blacklisted = db.Column(db.Boolean, default=False)

    # Relationships
    user = db.relationship("User", back_populates="company")
    drives = db.relationship("Drive", back_populates="company")
    placements = db.relationship("Placement", back_populates="company")


# -------------------------------
# Drive Model 
# -------------------------------
class Drive(db.Model):
    __tablename__ = "drive"

    id = db.Column(db.Integer, primary_key=True)

    company_id = db.Column(db.Integer, db.ForeignKey("company.id"))

    title = db.Column(db.String(100))

    # NEW FIELDS
    description = db.Column(db.Text)
    required_skills = db.Column(db.Text)
    experience_required = db.Column(db.String(50))
    salary = db.Column(db.Float)
    benefits = db.Column(db.Text)

    eligibility_cgpa = db.Column(db.Float)
    deadline = db.Column(db.Date)

    job_status = db.Column(db.String(20), default="Active")  # Active / Closed
    status = db.Column(db.String(20), default="Pending")     # Pending / Approved / Rejected

    # Relationships
    company = db.relationship("Company", back_populates="drives")
    applications = db.relationship("Application", back_populates="drive")
    interviews = db.relationship("Interview", back_populates="drive")
    placements = db.relationship("Placement", back_populates="drive")


# -------------------------------
# Application Model
# -------------------------------
class Application(db.Model):
    __tablename__ = "application"

    id = db.Column(db.Integer, primary_key=True)

    student_id = db.Column(db.Integer, db.ForeignKey("student.id"))
    drive_id = db.Column(db.Integer, db.ForeignKey("drive.id"))

    # Applied -> Shortlisted -> Interview -> Offer -> Placed / Rejected
    status = db.Column(db.String(20), default="Applied")

    applied_on = db.Column(db.DateTime, default=datetime.utcnow)

    feedback = db.Column(db.Text)

    # Relationships
    student = db.relationship("Student", back_populates="applications")
    drive = db.relationship("Drive", back_populates="applications")


# -------------------------------
# Interview Model
# -------------------------------
class Interview(db.Model):
    __tablename__ = "interview"

    id = db.Column(db.Integer, primary_key=True)

    student_id = db.Column(db.Integer, db.ForeignKey("student.id"))
    drive_id = db.Column(db.Integer, db.ForeignKey("drive.id"))
    company_id = db.Column(db.Integer, db.ForeignKey("company.id"))

    interview_date = db.Column(db.DateTime)
    interview_mode = db.Column(db.String(50))   # Online / Offline / Phone
    location = db.Column(db.String(255))        # Meeting link or address

    status = db.Column(db.String(20), default="Scheduled")  # Scheduled / Completed / Cancelled

    feedback = db.Column(db.Text)
    notes = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    student = db.relationship("Student", back_populates="interviews")
    drive = db.relationship("Drive", back_populates="interviews")


# -------------------------------
# Placement Model
# -------------------------------
class Placement(db.Model):
    __tablename__ = "placement"

    id = db.Column(db.Integer, primary_key=True)

    student_id = db.Column(db.Integer, db.ForeignKey("student.id"))
    company_id = db.Column(db.Integer, db.ForeignKey("company.id"))
    drive_id = db.Column(db.Integer, db.ForeignKey("drive.id"))

    position = db.Column(db.String(100))
    salary = db.Column(db.Float)
    joining_date = db.Column(db.Date)

    status = db.Column(db.String(20), default="Offer")  # Offer / Accepted / Joined / Declined

    offer_letter_path = db.Column(db.String(255))

    placed_on = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    student = db.relationship("Student", back_populates="placements")
    company = db.relationship("Company", back_populates="placements")
    drive = db.relationship("Drive", back_populates="placements")

