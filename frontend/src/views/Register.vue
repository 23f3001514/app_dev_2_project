
<script setup>
import { ref } from "vue"
import { useRouter } from "vue-router"
import axios from "axios"

const router = useRouter()
const API_BASE = "http://localhost:5000/api/auth"

const role = ref("student")

const username = ref("")
const name = ref("")
const email = ref("")
const password = ref("")

const branch = ref("")
const cgpa = ref(null)
const year = ref(null)
const education = ref("")
const skills = ref("")
const phone = ref("")
const experience = ref("")

const industry = ref("")
const location = ref("")
const website = ref("")
const description = ref("")

const register = async () => {
  try {
    if (!username.value || !email.value || !password.value) {
      alert("Username, Email and Password are required")
      return
    }

    if (role.value === "student") {
      await axios.post(`${API_BASE}/register/student`, {
        username: username.value,
        email: email.value,
        password: password.value,
        branch: branch.value,
        cgpa: cgpa.value,
        year: year.value,
        education: education.value,
        skills: skills.value,
        phone: phone.value,
        experience: experience.value,
      })

      alert("Student registered successfully!")
    }

    if (role.value === "company") {
      if (!name.value) {
        alert("Company name is required")
        return
      }

      await axios.post(`${API_BASE}/register/company`, {
        username: username.value,
        name: name.value,
        email: email.value,
        password: password.value,
        industry: industry.value,
        location: location.value,
        website: website.value,
        description: description.value,
      })

      alert("Company registered! Waiting for admin approval.")
    }

    router.push("/login")

  } catch (err) {
    alert(err.response?.data?.error || "Registration failed")
  }
}
</script>

<template>
<div class="container mt-5">
  <h2 class="text-center mb-4">Register</h2>

  <div class="card p-4 shadow">

    <div class="mb-3">
      <label class="form-label">Register As</label>
      <select v-model="role" class="form-select">
        <option value="student">Student</option>
        <option value="company">Company</option>
      </select>
    </div>

    <div class="mb-3">
      <label class="form-label">Username</label>
      <input v-model="username" type="text" class="form-control" required />
    </div>

    <div v-if="role === 'company'" class="mb-3">
      <label class="form-label">Company Name</label>
      <input v-model="name" type="text" class="form-control" required />
    </div>

    <div class="mb-3">
      <label class="form-label">Email</label>
      <input v-model="email" type="email" class="form-control" required />
    </div>

    <div class="mb-3">
      <label class="form-label">Password</label>
      <input v-model="password" type="password" class="form-control" required />
    </div>

    <div v-if="role === 'student'">
      <div class="mb-3">
        <label class="form-label">Branch</label>
        <input v-model="branch" type="text" class="form-control" placeholder="e.g., Computer Science" />
      </div>

      <div class="mb-3">
        <label class="form-label">CGPA</label>
        <input v-model="cgpa" type="number" step="0.1" class="form-control" placeholder="e.g., 8.5" />
      </div>

      <div class="mb-3">
        <label class="form-label">Year</label>
        <input v-model="year" type="number" class="form-control" placeholder="e.g., 3" />
      </div>

      <div class="mb-3">
        <label class="form-label">Education</label>
        <textarea v-model="education" class="form-control" rows="2" placeholder="e.g., B.Tech in CSE, IIT Madras, 2024"></textarea>
      </div>

      <div class="mb-3">
        <label class="form-label">Skills</label>
        <textarea v-model="skills" class="form-control" rows="2" placeholder="e.g., Python, Java, React, SQL"></textarea>
      </div>

      <div class="mb-3">
        <label class="form-label">Phone</label>
        <input v-model="phone" type="text" class="form-control" placeholder="e.g., +91 9876543210" />
      </div>

      <div class="mb-3">
        <label class="form-label">Experience (Optional)</label>
        <textarea v-model="experience" class="form-control" rows="2" placeholder="e.g., Intern at XYZ Corp (6 months)"></textarea>
      </div>
    </div>

    <div v-if="role === 'company'">
      <div class="mb-3">
        <label class="form-label">Industry</label>
        <input v-model="industry" type="text" class="form-control" placeholder="e.g., IT, Finance, Healthcare" />
      </div>

      <div class="mb-3">
        <label class="form-label">Location</label>
        <input v-model="location" type="text" class="form-control" placeholder="e.g., Bangalore, India" />
      </div>

      <div class="mb-3">
        <label class="form-label">Website</label>
        <input v-model="website" type="text" class="form-control" placeholder="e.g., https://company.com" />
      </div>

      <div class="mb-3">
        <label class="form-label">Description</label>
        <textarea v-model="description" class="form-control" rows="3" placeholder="Brief company description"></textarea>
      </div>
    </div>

    <button @click="register" class="btn btn-primary w-100 mt-3">
      Register
    </button>

  </div>
</div>
</template>


<style scoped>
.card {
  border-radius: 10px;
  max-width: 600px;
  margin: 0 auto;
}
</style>