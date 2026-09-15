# 🎓 Placement Preparation App — V2

> **A full-stack placement management platform designed to connect students, companies, and administrators in one place.**

🚀 **Built as part of the IIT Madras BS Degree in Data Science and Applications — App Development II**

---

## 🌟 Overview

The **Placement Preparation App — V2** is a full-stack web application that streamlines the campus placement process for **Students, Companies, and Administrators**.

The platform provides dedicated dashboards and workflows for managing placement drives, applications, interviews, and placement outcomes.

---

## 👥 User Roles

### 👨‍🎓 Student

* Create and manage profile
* Browse available placement drives
* Apply for suitable opportunities
* Track application status
* Manage interview information
* View placement status

### 🏢 Company

* Create and manage company profile
* Create placement drives
* View student applications
* Manage recruitment process
* Schedule and manage interviews
* Track selected candidates

### 🛡️ Admin

* Manage students and companies
* Monitor placement drives
* Manage applications
* Oversee interviews
* Track placement records
* Manage the overall platform

---

## ✨ Key Features

* 🔐 **Role-based authentication**
* 👨‍🎓 **Student dashboard**
* 🏢 **Company dashboard**
* 🛡️ **Admin dashboard**
* 📢 **Placement drive management**
* 📝 **Student applications**
* 📄 **Resume upload & management**
* 🎤 **Interview management**
* 🎯 **Placement tracking**
* 🗄️ **SQLite database**
* 🔄 **RESTful API architecture**
* 📱 **Responsive user interface**

---

## 🛠️ Tech Stack

| Layer                 | Technology                   |
| --------------------- | ---------------------------- |
| 🎨 Frontend           | Vue.js                       |
| 🖥️ Backend           | Flask                        |
| 🗄️ Database          | SQLite                       |
| 🎨 UI                 | Bootstrap                    |
| 🔌 API                | REST API                     |
| 🔐 Authentication     | Session-based Authentication |
| 📦 Package Management | npm / pip                    |
| 🌿 Version Control    | Git & GitHub                 |

---

## 🏗️ Architecture

```text
                 ┌─────────────────────┐
                 │       Users         │
                 │ Student / Company   │
                 │       / Admin       │
                 └──────────┬──────────┘
                            │
                            ▼
                 ┌─────────────────────┐
                 │    Vue.js Frontend  │
                 │      + Bootstrap     │
                 └──────────┬──────────┘
                            │
                         REST API
                            │
                            ▼
                 ┌─────────────────────┐
                 │    Flask Backend    │
                 │ Authentication      │
                 │ Business Logic      │
                 │ API Routes          │
                 └──────────┬──────────┘
                            │
                            ▼
                 ┌─────────────────────┐
                 │   SQLite Database   │
                 └─────────────────────┘
```

---

## 📂 Project Structure

```text
Placement-Preparation-App/
│
├── backend/
│   ├── app/
│   ├── models/
│   ├── routes/
│   ├── uploads/
│   ├── config.py
│   └── ...
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── views/
│   │   ├── router/
│   │   └── ...
│   ├── package.json
│   └── ...
│
├── README.md
└── ...
```

---

## 🔑 Core Modules

### 🔐 Authentication

Secure session-based authentication with role-specific access control.

### 📢 Placement Drives

Companies can create placement opportunities with relevant drive details and eligibility requirements.

### 📝 Applications

Students can discover drives and submit applications directly through the platform.

### 🎤 Interviews

Interview information can be created and managed as candidates progress through the recruitment process.

### 🏆 Placements

The system maintains placement information and helps administrators monitor recruitment outcomes.

---

## 💻 Getting Started

### Clone the repository

### Backend Setup

```bash
cd backend
pip install -r requirements.txt
```

Run the Flask server:

```bash
python app.py
```

### Frontend Setup

Open another terminal:

```bash
cd frontend
npm install
npm run dev
```

The application will then be available through the local development server.

---

## 🎯 What I Learned

Building this project helped me gain practical experience with:

* Full-stack web application development
* Flask REST APIs
* Vue.js frontend development
* Role-based access control
* Session-based authentication
* Database design and CRUD operations
* File uploads
* API–frontend integration
* Git & GitHub
* Building a complete application from requirements to implementation

---

## 📸 Screenshots



> Add screenshots of the **Student, Company, and Admin dashboards** here to make the repository visually stronger.

```text
📌 Student Dashboard
📌 Company Dashboard
📌 Admin Dashboard
📌 Placement Drive
📌 Application Management
```

---

## 🚀 Future Enhancements

Some potential improvements include:

* 📊 Advanced placement analytics
* 🔔 Real-time notifications
* 📧 Automated email notifications
* 📈 Student performance insights
* 🔎 Advanced drive filtering
* 📱 Improved mobile experience

---

## 👨‍💻 Developer

### Rohan Kumar

🎓 **BS in Data Science and Applications — IIT Madras**

**Interests:**
`Data Science` • `Machine Learning` • `AI` • `Backend Development` • `Full-Stack Development`

---

## ⭐ Project

If you find this project interesting, feel free to explore the repository and give it a ⭐.

