<script setup>
import { onMounted, ref } from "vue";
import axios from "axios";
import { useRouter } from "vue-router";

const router = useRouter();
const API_BASE = "http://localhost:5000/api/company";

const dashboard = ref(null);
const drives = ref([]);
const applications = ref([]);
const interviews = ref([]);
const placements = ref([]);
const loading = ref(true);

const activeTab = ref("drives");

const newDrive = ref({
  title: "",
  description: "",
  required_skills: "",
  experience_required: "",
  salary: "",
  benefits: "",
  eligibility_cgpa: "",
  deadline: ""
});

const showInterviewModal = ref(false);
const interviewForm = ref({
  application_id: null,
  interview_date: "",
  interview_mode: "Online",
  location: "",
  notes: ""
});

const showOfferModal = ref(false);
const offerForm = ref({
  application_id: null,
  position: "",
  salary: "",
  joining_date: ""
});

const fetchAll = async () => {
  try {
    loading.value = true;

    const dash = await axios.get(`${API_BASE}/dashboard`, {
      withCredentials: true,
    });
    dashboard.value = dash.data;

    const d = await axios.get(`${API_BASE}/drives`, {
      withCredentials: true,
    });
    drives.value = d.data || [];

    const a = await axios.get(`${API_BASE}/applications`, {
      withCredentials: true,
    });
    applications.value = a.data || [];

    const i = await axios.get("http://localhost:5000/api/interviews/company", {
      withCredentials: true,
    });
    interviews.value = i.data || [];

    const p = await axios.get("http://localhost:5000/api/placements/company", {
      withCredentials: true,
    });
    placements.value = p.data || [];

  } catch (err) {
    if (err.response?.status === 401) {
      await router.push("/login");
    } else {
      alert("Failed to load dashboard");
    }
  } finally {
    loading.value = false;
  }
};

const createDrive = async () => {
  try {
    await axios.post(`${API_BASE}/drives`, newDrive.value, {
      withCredentials: true,
    });

    alert("Drive created successfully!");

    newDrive.value = {
      title: "",
      description: "",
      required_skills: "",
      experience_required: "",
      salary: "",
      benefits: "",
      eligibility_cgpa: "",
      deadline: ""
    };

    await fetchAll();

  } catch (err) {
    alert(err.response?.data?.error || "Failed to create drive");
  }
};

const updateJobStatus = async (id, status) => {
  try {
    await axios.put(
      `${API_BASE}/drives/${id}/status`,
      { job_status: status },
      { withCredentials: true }
    );
    await fetchAll();
  } catch (err) {
    alert(err.response?.data?.error || "Failed to update status");
  }
};

const deleteDrive = async (id) => {
  if (!confirm("Delete this drive?")) return;

  try {
    await axios.delete(`${API_BASE}/drives/${id}`, {
      withCredentials: true,
    });

    await fetchAll();
  } catch (err) {
    alert(err.response?.data?.error || "Failed to delete drive");
  }
};

const updateStatus = async (appId, status) => {
  const feedback = status === "Rejected" 
    ? prompt("Enter feedback for the candidate (optional):")
    : "";

  try {
    await axios.put(
      `${API_BASE}/applications/${appId}/status`,
      { status, feedback },
      { withCredentials: true }
    );

    await fetchAll();
  } catch (err) {
    alert(err.response?.data?.error || "Failed to update status");
  }
};

const openInterviewModal = (app) => {
  interviewForm.value = {
    application_id: app.application_id,
    interview_date: "",
    interview_mode: "Online",
    location: "",
    notes: ""
  };
  showInterviewModal.value = true;
};

const scheduleInterview = async () => {
  try {
    await axios.post(
      "http://localhost:5000/api/interviews/schedule",
      interviewForm.value,
      { withCredentials: true }
    );

    alert("Interview scheduled successfully!");
    showInterviewModal.value = false;
    await fetchAll();

  } catch (err) {
    alert(err.response?.data?.error || "Failed to schedule interview");
  }
};

const openOfferModal = (app) => {
  offerForm.value = {
    application_id: app.application_id,
    position: app.drive_title,
    salary: "",
    joining_date: ""
  };
  showOfferModal.value = true;
};

const sendOffer = async () => {
  try {
    await axios.post(
      "http://localhost:5000/api/placements/create",
      offerForm.value,
      { withCredentials: true }
    );

    alert("Offer sent successfully!");
    showOfferModal.value = false;
    await fetchAll();

  } catch (err) {
    alert(err.response?.data?.error || "Failed to send offer");
  }
};

const updatePlacementStatus = async (placementId, status) => {
  try {
    await axios.put(
      `http://localhost:5000/api/placements/${placementId}/status`,
      { status },
      { withCredentials: true }
    );

    await fetchAll();
  } catch (err) {
    alert(err.response?.data?.error || "Failed to update placement status");
  }
};

onMounted(fetchAll);
</script>

<template>
<div class="container mt-4">
  <h2>Company Dashboard</h2>

  <div v-if="loading" class="text-center mt-3">
    Loading...
  </div>

  <div v-else>

    <div v-if="dashboard" class="card p-3 mb-4 shadow-sm">
      <p><strong>Company:</strong> {{ dashboard.company_name }}</p>
      <p><strong>Username:</strong> {{ dashboard.username }}</p>
      <p><strong>Industry:</strong> {{ dashboard.industry || 'Not set' }}</p>
      <p><strong>Location:</strong> {{ dashboard.location || 'Not set' }}</p>
      <p><strong>Website:</strong> 
        <a v-if="dashboard.website" :href="dashboard.website" target="_blank">{{ dashboard.website }}</a>
        <span v-else>Not set</span>
      </p>

      <p v-if="dashboard.blacklisted" class="text-danger fw-bold">
        ⚠ Your company has been blacklisted by admin.
      </p>

      <p><strong>Total Drives:</strong> {{ dashboard.total_drives }}</p>
      <p><strong>Total Applicants:</strong> {{ dashboard.total_applicants }}</p>
    </div>

    <ul class="nav nav-tabs mb-3">
      <li class="nav-item">
        <a class="nav-link" :class="{ active: activeTab === 'drives' }" @click="activeTab = 'drives'" href="#">
          Drives
        </a>
      </li>
      <li class="nav-item">
        <a class="nav-link" :class="{ active: activeTab === 'applications' }" @click="activeTab = 'applications'" href="#">
          Applications ({{ applications.length }})
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
    </ul>

    <div v-if="activeTab === 'drives'">
      <div v-if="dashboard && !dashboard.blacklisted"
           class="card p-3 mb-4 shadow-sm">

        <h4>Create New Drive</h4>

        <form @submit.prevent="createDrive">
          <div class="mb-2">
            <label class="form-label">Job Title *</label>
            <input v-model="newDrive.title"
                   class="form-control"
                   placeholder="e.g., Software Engineer"
                   required />
          </div>

          <div class="mb-2">
            <label class="form-label">Description</label>
            <textarea v-model="newDrive.description"
                      class="form-control"
                      rows="3"
                      placeholder="Job description..."></textarea>
          </div>

          <div class="mb-2">
            <label class="form-label">Required Skills</label>
            <textarea v-model="newDrive.required_skills"
                      class="form-control"
                      rows="2"
                      placeholder="e.g., Python, React, SQL"></textarea>
          </div>

          <div class="mb-2">
            <label class="form-label">Experience Required</label>
            <input v-model="newDrive.experience_required"
                   class="form-control"
                   placeholder="e.g., 0-1 years, 2-5 years" />
          </div>

          <div class="mb-2">
            <label class="form-label">Salary (CTC in LPA)</label>
            <input type="number"
                   step="0.1"
                   v-model="newDrive.salary"
                   class="form-control"
                   placeholder="e.g., 12.5" />
          </div>

          <div class="mb-2">
            <label class="form-label">Benefits</label>
            <textarea v-model="newDrive.benefits"
                      class="form-control"
                      rows="2"
                      placeholder="e.g., Health insurance, WFH"></textarea>
          </div>

          <div class="mb-2">
            <label class="form-label">Minimum CGPA *</label>
            <input type="number"
                   step="0.1"
                   v-model="newDrive.eligibility_cgpa"
                   class="form-control"
                   required />
          </div>

          <div class="mb-2">
            <label class="form-label">Deadline *</label>
            <input type="date"
                   v-model="newDrive.deadline"
                   class="form-control"
                   required />
          </div>

          <button class="btn btn-primary mt-2">
            Create Drive
          </button>
        </form>
      </div>

      <h3>Your Drives</h3>

      <div v-if="drives.length === 0" class="text-muted">
        No drives created yet.
      </div>

      <div v-else class="row">
        <div v-for="drive in drives"
             :key="drive.id"
             class="col-md-6 mb-3">

          <div class="card">
            <div class="card-body">
              <h5 class="card-title">{{ drive.title }}</h5>

              <p class="mb-1"><strong>Skills:</strong> {{ drive.required_skills || 'N/A' }}</p>
              <p class="mb-1"><strong>Experience:</strong> {{ drive.experience_required || 'N/A' }}</p>
              <p class="mb-1"><strong>Salary:</strong> {{ drive.salary ? `₹${drive.salary} LPA` : 'N/A' }}</p>
              <p class="mb-1"><strong>Benefits:</strong> {{ drive.benefits || 'N/A' }}</p>
              <p class="mb-1"><strong>CGPA ≥</strong> {{ drive.eligibility_cgpa }}</p>
              <p class="mb-1"><strong>Deadline:</strong> {{ drive.deadline }}</p>

              <div class="mt-2">
                <span
                  class="badge me-2"
                  :class="{
                    'bg-warning': drive.status === 'Pending',
                    'bg-success': drive.status === 'Approved',
                    'bg-danger': drive.status === 'Rejected'
                  }"
                >
                  {{ drive.status }}
                </span>

                <span
                  class="badge"
                  :class="{
                    'bg-success': drive.job_status === 'Active',
                    'bg-secondary': drive.job_status === 'Closed'
                  }"
                >
                  {{ drive.job_status }}
                </span>
              </div>

              <div class="mt-3">
                <button
                  v-if="drive.job_status === 'Active'"
                  class="btn btn-sm btn-warning me-2"
                  @click="updateJobStatus(drive.id, 'Closed')">
                  Mark as Closed
                </button>

                <button
                  v-else
                  class="btn btn-sm btn-success me-2"
                  @click="updateJobStatus(drive.id, 'Active')">
                  Reopen
                </button>

                <button
                  class="btn btn-danger btn-sm"
                  @click="deleteDrive(drive.id)">
                  Delete
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="activeTab === 'applications'">
      <h3>Applications</h3>

      <div v-if="applications.length === 0" class="text-muted">
        No applications yet.
      </div>

      <table v-else class="table table-bordered table-hover">
        <thead>
          <tr>
            <th>Drive</th>
            <th>Student</th>
            <th>Email</th>
            <th>Branch</th>
            <th>CGPA</th>
            <th>Skills</th>
            <th>Phone</th>
            <th>Status</th>
            <th>Applied On</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="app in applications"
              :key="app.application_id">

            <td>{{ app.drive_title }}</td>
            <td>{{ app.student_username }}</td>
            <td>{{ app.student_email }}</td>
            <td>{{ app.student_branch }}</td>
            <td>{{ app.student_cgpa }}</td>
            <td>{{ app.student_skills || 'N/A' }}</td>
            <td>{{ app.student_phone || 'N/A' }}</td>

            <td>
              <span 
                class="badge"
                :class="{
                  'bg-secondary': app.status === 'Applied',
                  'bg-info': app.status === 'Shortlisted',
                  'bg-warning': app.status === 'Interview',
                  'bg-primary': app.status === 'Offer',
                  'bg-success': app.status === 'Placed',
                  'bg-danger': app.status === 'Rejected'
                }"
              >
                {{ app.status }}
              </span>
            </td>

            <td>{{ app.applied_on }}</td>

            <td>
              <div v-if="app.status === 'Applied'" class="btn-group-vertical btn-group-sm">
                <button
                  class="btn btn-info btn-sm mb-1"
                  @click="updateStatus(app.application_id, 'Shortlisted')">
                  Shortlist
                </button>
                <button
                  class="btn btn-danger btn-sm"
                  @click="updateStatus(app.application_id, 'Rejected')">
                  Reject
                </button>
              </div>

              <div v-else-if="app.status === 'Shortlisted'" class="btn-group-vertical btn-group-sm">
                <button
                  class="btn btn-warning btn-sm mb-1"
                  @click="openInterviewModal(app)">
                  Schedule Interview
                </button>
                <button
                  class="btn btn-danger btn-sm"
                  @click="updateStatus(app.application_id, 'Rejected')">
                  Reject
                </button>
              </div>

              <div v-else-if="app.status === 'Interview'" class="btn-group-vertical btn-group-sm">
                <button
                  class="btn btn-primary btn-sm mb-1"
                  @click="openOfferModal(app)">
                  Send Offer
                </button>
                <button
                  class="btn btn-danger btn-sm"
                  @click="updateStatus(app.application_id, 'Rejected')">
                  Reject
                </button>
              </div>

              <div v-else-if="app.status === 'Offer'" class="btn-group-vertical btn-group-sm">
                <button
                  class="btn btn-success btn-sm"
                  @click="updateStatus(app.application_id, 'Placed')">
                  Mark as Placed
                </button>
              </div>

              <span v-else class="text-muted">-</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="activeTab === 'interviews'">
      <h3>Scheduled Interviews</h3>

      <div v-if="interviews.length === 0" class="text-muted">
        No interviews scheduled yet.
      </div>

      <table v-else class="table table-bordered">
        <thead>
          <tr>
            <th>Student</th>
            <th>Email</th>
            <th>Drive</th>
            <th>Date & Time</th>
            <th>Mode</th>
            <th>Location</th>
            <th>Status</th>
            <th>Notes</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="interview in interviews" :key="interview.id">
            <td>{{ interview.student_name }}</td>
            <td>{{ interview.student_email }}</td>
            <td>{{ interview.drive_title }}</td>
            <td>{{ interview.interview_date }}</td>
            <td>{{ interview.interview_mode }}</td>
            <td>{{ interview.location || 'N/A' }}</td>
            <td>
              <span class="badge bg-warning">{{ interview.status }}</span>
            </td>
            <td>{{ interview.notes || '-' }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="activeTab === 'placements'">
      <h3>Placements & Offers</h3>

      <div v-if="placements.length === 0" class="text-muted">
        No placements yet.
      </div>

      <table v-else class="table table-bordered">
        <thead>
          <tr>
            <th>Student</th>
            <th>Email</th>
            <th>Drive</th>
            <th>Position</th>
            <th>Salary (LPA)</th>
            <th>Joining Date</th>
            <th>Status</th>
            <th>Placed On</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="placement in placements" :key="placement.id">
            <td>{{ placement.student_name }}</td>
            <td>{{ placement.student_email }}</td>
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
            <td>
              <div v-if="placement.status === 'Accepted'" class="btn-group-sm">
                <button
                  class="btn btn-success btn-sm"
                  @click="updatePlacementStatus(placement.id, 'Joined')">
                  Mark as Joined
                </button>
              </div>
              <span v-else class="text-muted">-</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

  </div>

  <div v-if="showInterviewModal" class="modal-overlay" @click="showInterviewModal = false">
    <div class="modal-content" @click.stop>
      <h4>Schedule Interview</h4>
      
      <div class="mb-2">
        <label class="form-label">Interview Date & Time *</label>
        <input v-model="interviewForm.interview_date" type="datetime-local" class="form-control" required />
      </div>

      <div class="mb-2">
        <label class="form-label">Mode *</label>
        <select v-model="interviewForm.interview_mode" class="form-select">
          <option value="Online">Online</option>
          <option value="Offline">Offline</option>
          <option value="Phone">Phone</option>
        </select>
      </div>

      <div class="mb-2">
        <label class="form-label">Location (Meeting Link or Address)</label>
        <input v-model="interviewForm.location" class="form-control" placeholder="e.g., https://meet.google.com/..." />
      </div>

      <div class="mb-2">
        <label class="form-label">Notes</label>
        <textarea v-model="interviewForm.notes" class="form-control" rows="2"></textarea>
      </div>

      <div class="mt-3">
        <button class="btn btn-primary me-2" @click="scheduleInterview">Schedule</button>
        <button class="btn btn-secondary" @click="showInterviewModal = false">Cancel</button>
      </div>
    </div>
  </div>

  <div v-if="showOfferModal" class="modal-overlay" @click="showOfferModal = false">
    <div class="modal-content" @click.stop>
      <h4>Send Offer</h4>
      
      <div class="mb-2">
        <label class="form-label">Position *</label>
        <input v-model="offerForm.position" class="form-control" required />
      </div>

      <div class="mb-2">
        <label class="form-label">Salary (CTC in LPA) *</label>
        <input v-model="offerForm.salary" type="number" step="0.1" class="form-control" required />
      </div>

      <div class="mb-2">
        <label class="form-label">Joining Date *</label>
        <input v-model="offerForm.joining_date" type="date" class="form-control" required />
      </div>

      <div class="mt-3">
        <button class="btn btn-primary me-2" @click="sendOffer">Send Offer</button>
        <button class="btn btn-secondary" @click="showOfferModal = false">Cancel</button>
      </div>
    </div>
  </div>
</div>
</template>

<style scoped>
.card {
  border-radius: 8px;
}

.nav-link {
  cursor: pointer;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  padding: 20px;
  border-radius: 8px;
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
}
</style>

