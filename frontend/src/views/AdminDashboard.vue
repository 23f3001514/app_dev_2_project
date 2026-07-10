<script setup>
import { onMounted, ref } from "vue"
import axios from "axios"
import { useRouter } from "vue-router"

const router = useRouter()
const API_BASE = "http://localhost:5000/api/admin"

const summary = ref(null)
const pendingCompanies = ref([])
const drives = ref([])
const interviews = ref([])
const placements = ref([])
const analytics = ref(null)

const searchQuery = ref("")
const searchResults = ref(null)

const activeTab = ref("dashboard")

const fetchData = async () => {
  try {
    const summaryRes = await axios.get(`${API_BASE}/dashboard`, { withCredentials: true })
    summary.value = summaryRes.data

    const companiesRes = await axios.get(`${API_BASE}/companies/pending`, { withCredentials: true })
    pendingCompanies.value = companiesRes.data

    const drivesRes = await axios.get(`${API_BASE}/drives`, { withCredentials: true })
    drives.value = drivesRes.data

    const interviewsRes = await axios.get(`${API_BASE}/interviews`, { withCredentials: true })
    interviews.value = interviewsRes.data

    const placementsRes = await axios.get(`${API_BASE}/placements`, { withCredentials: true })
    placements.value = placementsRes.data

    const analyticsRes = await axios.get(`${API_BASE}/analytics`, { withCredentials: true })
    analytics.value = analyticsRes.data

  } catch (err) {
    if (err.response?.status === 401) {
      console.log('Unauthorized - redirecting to login')
      await router.push("/login")
    } else {
      alert(err.response?.data?.error || "Failed to load admin data")
    }
  }
}

onMounted(fetchData)

const searchAdmin = async () => {
  if (!searchQuery.value.trim()) {
    searchResults.value = null
    return
  }

  try {
    const res = await axios.get(
      `${API_BASE}/search?q=${searchQuery.value}`,
      { withCredentials: true }
    )
    searchResults.value = res.data
  } catch (err) {
    if (err.response?.status === 401) {
      await router.push("/login")
    } else {
      alert(err.response?.data?.error || "Search failed")
    }
  }
}

const approveCompany = async (id) => {
  try {
    await axios.post(`${API_BASE}/companies/${id}/approve`, {}, { withCredentials: true })
    await fetchData()
  } catch (err) {
    if (err.response?.status === 401) {
      await router.push("/login")
    } else {
      alert("Failed to approve company")
    }
  }
}

const blacklistCompany = async (id) => {
  if (!confirm("Are you sure you want to blacklist this company?")) return

  try {
    await axios.post(`${API_BASE}/companies/${id}/blacklist`, {}, { withCredentials: true })
    alert("Company blacklisted")
    await fetchData()
  } catch (err) {
    if (err.response?.status === 401) {
      await router.push("/login")
    } else {
      alert("Failed to blacklist company")
    }
  }
}

const rejectDrive = async (id) => {
  try {
    await axios.post(`${API_BASE}/drives/${id}/reject`, {}, { withCredentials: true })
    await fetchData()
  } catch (err) {
    if (err.response?.status === 401) {
      await router.push("/login")
    } else {
      alert("Failed to reject drive")
    }
  }
}
</script>

<template>
<div class="container mt-4">
  <h2>Admin Dashboard</h2>

  <div class="card p-3 mb-4">
    <h4>Search</h4>

    <div class="input-group mb-3">
      <input v-model="searchQuery" class="form-control" placeholder="Search students, companies, drives..." />
      <button class="btn btn-primary" @click="searchAdmin">Search</button>
    </div>

    <div v-if="searchResults">

      <div v-if="searchResults.students?.length">
        <h5>Students</h5>
        <ul class="list-group mb-3">
          <li v-for="s in searchResults.students" :key="s.id" class="list-group-item">
            <table border="1" class="table table-sm">
              <thead>
                <tr>
                <th>Name</th>
                <th>Email</th>
                <th>Department</th>
                <th>CGPA</th>
                <th>Is Placed</th>
              </tr>
              </thead>
              <tbody>
                <tr>
                  <td><strong>{{ s.username }}</strong></td>
                  <td><strong>{{ s.email }}</strong></td>
                  <td><strong>{{ s.branch }}</strong></td>
                  <td><strong>{{ s.cgpa }}</strong></td>
                  <td><strong>{{  s.is_placed  }}</strong></td>
                </tr>
              </tbody>
            </table>
          </li>
        </ul>
      </div>

      <div v-if="searchResults.companies?.length">
        <h5>Companies</h5>
        <ul class="list-group mb-3">
          <li v-for="c in searchResults.companies" :key="c.id"
              class="list-group-item d-flex justify-content-between">
            <div>
              <strong>{{ c.name }}</strong> |
              <span :class="c.approved ? 'text-success' : 'text-warning'">
                {{ c.approved ? "Approved" : "Pending" }}
              </span>
              <span v-if="c.blacklisted" class="text-danger ms-2">
                (Blacklisted)
              </span>
            </div>
            <button class="btn btn-danger btn-sm"
                    @click="blacklistCompany(c.id)">
              Blacklist
            </button>
          </li>
        </ul>
      </div>

      <div v-if="searchResults.drives?.length">
        <h5>Drives</h5>
        <ul class="list-group">
          <li v-for="d in searchResults.drives"
              :key="d.id"
              class="list-group-item">
            {{ d.title }} |
            Company: {{ d.company_name }} |
            Status: {{ d.status }}
          </li>
        </ul>
      </div>

      <p v-if="!searchResults.students?.length &&
               !searchResults.companies?.length &&
               !searchResults.drives?.length">
        No results found.
      </p>

    </div>
  </div>

  <ul class="nav nav-tabs mb-3">
    <li class="nav-item">
      <a class="nav-link" :class="{ active: activeTab === 'dashboard' }" @click="activeTab = 'dashboard'" href="#">
        Dashboard
      </a>
    </li>
    <li class="nav-item">
      <a class="nav-link" :class="{ active: activeTab === 'companies' }" @click="activeTab = 'companies'" href="#">
        Companies ({{ pendingCompanies.length }} Pending)
      </a>
    </li>
    <li class="nav-item">
      <a class="nav-link" :class="{ active: activeTab === 'drives' }" @click="activeTab = 'drives'" href="#">
        Drives ({{ drives.length }})
      </a>
    </li>
    <li class="nav-item">
      <a class="nav-link" :class="{ active: activeTab === 'interviews' }" @click="activeTab = 'interviews'" href="#">
        Interviews ({{ interviews.length }})
      </a>
    </li>
    <li class="nav-item">
      <a class="nav-link" :class="{ active: activeTab === 'placements' }" @click="activeTab = 'placements'" href="#">
        Placements ({{ placements.length }})
      </a>
    </li>
    <li class="nav-item">
      <a class="nav-link" :class="{ active: activeTab === 'analytics' }" @click="activeTab = 'analytics'" href="#">
        Analytics
      </a>
    </li>
  </ul>

  <div v-if="activeTab === 'dashboard' && summary" class="card p-3 mb-4">
    <h4>System Summary</h4>
    <div class="row">
      <div class="col-md-4">
        <div class="card bg-primary text-white p-3 mb-2">
          <h5>{{ summary.total_students }}</h5>
          <p>Total Students</p>
        </div>
      </div>
      <div class="col-md-4">
        <div class="card bg-success text-white p-3 mb-2">
          <h5>{{ summary.students_placed }}</h5>
          <p>Students Placed</p>
        </div>
      </div>
      <div class="col-md-4">
        <div class="card bg-info text-white p-3 mb-2">
          <h5>{{ summary.total_companies }}</h5>
          <p>Total Companies</p>
        </div>
      </div>
      <div class="col-md-4">
        <div class="card bg-warning text-white p-3 mb-2">
          <h5>{{ summary.pending_companies }}</h5>
          <p>Pending Companies</p>
        </div>
      </div>
      <div class="col-md-4">
        <div class="card bg-danger text-white p-3 mb-2">
          <h5>{{ summary.blacklisted_companies }}</h5>
          <p>Blacklisted Companies</p>
        </div>
      </div>
      <div class="col-md-4">
        <div class="card bg-secondary text-white p-3 mb-2">
          <h5>{{ summary.total_drives }}</h5>
          <p>Total Drives</p>
        </div>
      </div>
      <div class="col-md-4">
        <div class="card bg-dark text-white p-3 mb-2">
          <h5>{{ summary.total_applications }}</h5>
          <p>Total Applications</p>
        </div>
      </div>
      <div class="col-md-4">
        <div class="card bg-primary text-white p-3 mb-2">
          <h5>{{ summary.total_interviews }}</h5>
          <p>Total Interviews</p>
        </div>
      </div>
      <div class="col-md-4">
        <div class="card bg-success text-white p-3 mb-2">
          <h5>{{ summary.total_placements }}</h5>
          <p>Total Placements</p>
        </div>
      </div>
    </div>
  </div>

  <div v-if="activeTab === 'companies'" class="card p-3 mb-4">
    <h4>Pending Companies</h4>

    <ul class="list-group">
      <li v-for="c in pendingCompanies"
          :key="c.id"
          class="list-group-item d-flex justify-content-between">

        <strong>{{ c.name }}</strong>

        <div>
          <button class="btn btn-success btn-sm me-2"
                  @click="approveCompany(c.id)">
            Approve
          </button>

          <button class="btn btn-danger btn-sm"
                  @click="blacklistCompany(c.id)">
            Blacklist
          </button>
        </div>
      </li>
    </ul>

    <p v-if="pendingCompanies.length === 0" class="mt-2">
      No pending companies
    </p>
  </div>

  <div v-if="activeTab === 'drives'" class="card p-3">
    <h4>All Drives</h4>

    <ul class="list-group">
      <li v-for="d in drives"
          :key="d.id"
          class="list-group-item d-flex justify-content-between">

        <div>
          <strong>{{ d.title }}</strong><br>
          Company: {{ d.company_name }}<br>
          CGPA ≥ {{ d.eligibility_cgpa }}<br>
          Deadline: {{ d.deadline }}<br>
          Status: <strong>{{ d.status }}</strong>
        </div>

        <button v-if="d.status === 'Pending'"
                class="btn btn-danger btn-sm"
                @click="rejectDrive(d.id)">
          Reject
        </button>

      </li>
    </ul>
  </div>

  <div v-if="activeTab === 'interviews'">
    <h4>All Interviews</h4>

    <div v-if="interviews.length === 0" class="text-muted">
      No interviews scheduled yet.
    </div>

    <table v-else class="table table-bordered">
      <thead>
        <tr>
          <th>Student</th>
          <th>Company</th>
          <th>Drive</th>
          <th>Date & Time</th>
          <th>Mode</th>
          <th>Status</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="interview in interviews" :key="interview.id">
          <td>{{ interview.student_name }}</td>
          <td>{{ interview.company_name }}</td>
          <td>{{ interview.drive_title }}</td>
          <td>{{ interview.interview_date }}</td>
          <td>{{ interview.interview_mode }}</td>
          <td>
            <span class="badge bg-warning">{{ interview.status }}</span>
          </td>
        </tr>
      </tbody>
    </table>
  </div>

  <div v-if="activeTab === 'placements'">
    <h4>All Placements</h4>

    <div v-if="placements.length === 0" class="text-muted">
      No placements yet.
    </div>

    <table v-else class="table table-bordered">
      <thead>
        <tr>
          <th>Student</th>
          <th>Company</th>
          <th>Drive</th>
          <th>Position</th>
          <th>Salary (LPA)</th>
          <th>Joining Date</th>
          <th>Status</th>
          <th>Placed On</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="placement in placements" :key="placement.id">
          <td>{{ placement.student_name }}</td>
          <td>{{ placement.company_name }}</td>
          <td>{{ placement.drive_title }}</td>
          <td>{{ placement.position }}</td>
          <td>₹{{ placement.salary }}</td>
          <td>{{ placement.joining_date }}</td>
          <td>
            <span 
              class="badge"
              :class="{
                'bg-primary': placement.status === 'Offer',
                'bg-info': placement.status === 'Accepted',
                'bg-success': placement.status === 'Joined',
                'bg-secondary': placement.status === 'Declined'
              }"
            >
              {{ placement.status }}
            </span>
          </td>
          <td>{{ placement.placed_on }}</td>
        </tr>
      </tbody>
    </table>
  </div>

  <div v-if="activeTab === 'analytics' && analytics">
    <h4>Analytics</h4>

    <div class="row">
      <div class="col-md-6 mb-3">
        <div class="card p-3">
          <h5>Application Status Breakdown</h5>
          <ul class="list-group">
            <li class="list-group-item d-flex justify-content-between">
              <span>Applied</span>
              <span class="badge bg-secondary">{{ analytics.application_status.Applied }}</span>
            </li>
            <li class="list-group-item d-flex justify-content-between">
              <span>Shortlisted</span>
              <span class="badge bg-info">{{ analytics.application_status.Shortlisted }}</span>
            </li>
            <li class="list-group-item d-flex justify-content-between">
              <span>Interview</span>
              <span class="badge bg-warning">{{ analytics.application_status.Interview }}</span>
            </li>
            <li class="list-group-item d-flex justify-content-between">
              <span>Offer</span>
              <span class="badge bg-primary">{{ analytics.application_status.Offer }}</span>
            </li>
            <li class="list-group-item d-flex justify-content-between">
              <span>Placed</span>
              <span class="badge bg-success">{{ analytics.application_status.Placed }}</span>
            </li>
            <li class="list-group-item d-flex justify-content-between">
              <span>Rejected</span>
              <span class="badge bg-danger">{{ analytics.application_status.Rejected }}</span>
            </li>
          </ul>
        </div>
      </div>

      <div class="col-md-6 mb-3">
        <div class="card p-3">
          <h5>Placement Status Breakdown</h5>
          <ul class="list-group">
            <li class="list-group-item d-flex justify-content-between">
              <span>Offer Sent</span>
              <span class="badge bg-primary">{{ analytics.placement_status.Offer }}</span>
            </li>
            <li class="list-group-item d-flex justify-content-between">
              <span>Accepted</span>
              <span class="badge bg-info">{{ analytics.placement_status.Accepted }}</span>
            </li>
            <li class="list-group-item d-flex justify-content-between">
              <span>Joined</span>
              <span class="badge bg-success">{{ analytics.placement_status.Joined }}</span>
            </li>
            <li class="list-group-item d-flex justify-content-between">
              <span>Declined</span>
              <span class="badge bg-secondary">{{ analytics.placement_status.Declined }}</span>
            </li>
          </ul>
        </div>
      </div>

      <div class="col-12">
        <div class="card p-3">
          <h5>Top Companies by Placements</h5>
          <table class="table table-striped">
            <thead>
              <tr>
                <th>Company</th>
                <th>Placements</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(company, index) in analytics.top_companies" :key="index">
                <td>{{ company.name }}</td>
                <td><span class="badge bg-success">{{ company.placements }}</span></td>
              </tr>
            </tbody>
          </table>
          <p v-if="analytics.top_companies.length === 0" class="text-muted">No placement data yet.</p>
        </div>
      </div>
    </div>
  </div>

</div>
</template>

<style scoped>
.nav-link {
  cursor: pointer;
}
</style>



