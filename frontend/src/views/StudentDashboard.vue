
<script setup>
import { onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import axios from "axios";

const router = useRouter();
const API_BASE = "http://localhost:5000/api/student";

const student = ref(null);
const drives = ref([]);
const applications = ref([]);
const interviews = ref([]);
const placements = ref([]);
const searchQuery = ref("");

const activeTab = ref("drives");

const isEditingProfile = ref(false);
const profileForm = ref({
  branch: "",
  cgpa: 0,
  year: 0,
  education: "",
  skills: "",
  phone: "",
  experience: ""
});

const resumeFile = ref(null);
const uploadingResume = ref(false);

const fetchDashboard = async () => {
  try {
    const res = await axios.get(`${API_BASE}/dashboard`, { withCredentials: true });
    student.value = res.data;

    profileForm.value = {
      branch: res.data.branch || "",
      cgpa: res.data.cgpa || 0,
      year: res.data.year || 0,
      education: res.data.education || "",
      skills: res.data.skills || "",
      phone: res.data.phone || "",
      experience: res.data.experience || ""
    };
  } catch (err) {
    if (err.response?.status === 401) {
      console.log('Unauthorized - redirecting to login')
      await router.push("/login");
      throw err;
    }
  }
};

const updateProfile = async () => {
  try {
    await axios.put(`${API_BASE}/profile`, profileForm.value, { withCredentials: true });
    alert("Profile updated successfully!");
    isEditingProfile.value = false;
    await fetchDashboard();
  } catch (err) {
    if (err.response?.status === 401) {
      await router.push("/login");
    } else {
      alert(err.response?.data?.error || "Failed to update profile");
    }
  }
};

const handleResumeSelect = (event) => {
  const target = event.target;
  if (target.files && target.files.length > 0) {
    resumeFile.value = target.files[0];
  }
};

const uploadResume = async () => {
  if (!resumeFile.value) {
    alert("Please select a file first");
    return;
  }

  const formData = new FormData();
  formData.append("resume", resumeFile.value);

  try {
    uploadingResume.value = true;
    await axios.post(`${API_BASE}/resume/upload`, formData, {
      withCredentials: true,
      headers: { "Content-Type": "multipart/form-data" }
    });

    alert("Resume uploaded successfully!");
    resumeFile.value = null;
    await fetchDashboard();
  } catch (err) {
    if (err.response?.status === 401) {
      await router.push("/login");
    } else {
      alert(err.response?.data?.error || "Failed to upload resume");
    }
  } finally {
    uploadingResume.value = false;
  }
};

const downloadResume = async () => {
  try {
    const response = await axios.get(`${API_BASE}/resume/download`, {
      withCredentials: true,
      responseType: "blob"
    });

    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", student.value.resume_path || "resume.pdf");
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
  } catch (err) {
    if (err.response?.status === 401) {
      await router.push("/login");
    } else {
      alert(err.response?.data?.error || "Failed to download resume");
    }
  }
};

const deleteResume = async () => {
  if (!confirm("Are you sure you want to delete your resume?")) return;

  try {
    await axios.delete(`${API_BASE}/resume/delete`, { withCredentials: true });
    alert("Resume deleted successfully");
    await fetchDashboard();
  } catch (err) {
    if (err.response?.status === 401) {
      await router.push("/login");
    } else {
      alert(err.response?.data?.error || "Failed to delete resume");
    }
  }
};

const fetchDrives = async () => {
  try {
    const res = await axios.get(`${API_BASE}/drives`, {
      params: { q: searchQuery.value },
      withCredentials: true
    });
    drives.value = res.data || [];
  } catch (err) {
    if (err.response?.status === 401) {
      await router.push("/login");
    } else {
      console.log("Error loading drives");
    }
  }
};

const fetchApplications = async () => {
  try {
    const res = await axios.get(`${API_BASE}/applications`, { withCredentials: true });
    applications.value = res.data || [];
  } catch (err) {
    if (err.response?.status === 401) {
      await router.push("/login");
    } else {
      console.log("Error loading applications");
    }
  }
};

const fetchInterviews = async () => {
  try {
    const res = await axios.get("http://localhost:5000/api/interviews/student", { withCredentials: true });
    interviews.value = res.data || [];
  } catch (err) {
    if (err.response?.status === 401) {
      await router.push("/login");
    } else {
      console.log("Error loading interviews");
    }
  }
};

const fetchPlacements = async () => {
  try {
    const res = await axios.get("http://localhost:5000/api/placements/student", { withCredentials: true });
    placements.value = res.data || [];
  } catch (err) {
    if (err.response?.status === 401) {
      await router.push("/login");
    } else {
      console.log("Error loading placements");
    }
  }
};

const applyToDrive = async (driveId) => {
  try {
    await axios.post(`${API_BASE}/apply/${driveId}`, {}, { withCredentials: true });
    await fetchApplications();
    await fetchDrives();
    alert("Applied successfully!");
  } catch (err) {
    if (err.response?.status === 401) {
      await router.push("/login");
    } else {
      alert(err.response?.data?.error || "Application failed");
    }
  }
};

const respondToOffer = async (placementId, response) => {
  if (!confirm(`Are you sure you want to ${response} this offer?`)) return;

  try {
    await axios.put(
      `http://localhost:5000/api/placements/${placementId}/respond`,
      { response },
      { withCredentials: true }
    );

    alert(`Offer ${response}ed successfully!`);
    await fetchPlacements();
    await fetchDashboard();
  } catch (err) {
    if (err.response?.status === 401) {
      await router.push("/login");
    } else {
      alert(err.response?.data?.error || "Failed to respond to offer");
    }
  }
};

onMounted(async () => {
  try {
    await fetchDashboard();
    
    if (student.value) {
      await Promise.all([
        fetchApplications(),
        fetchDrives(),
        fetchInterviews(),
        fetchPlacements()
      ]);
    }
  } catch (err) {
    console.log('Component mount failed - user not authenticated');
  }
});
</script>

<template>
<div class="container mt-4">
  <h2>Student Dashboard</h2>

  <div v-if="student?.is_placed" class="alert alert-success">
    <strong>🎉 Congratulations! You have been placed!</strong>
  </div>

  <div v-if="student" class="card p-3 mb-4">
    <div class="d-flex justify-content-between align-items-center mb-3">
      <h4>My Profile</h4>
      <button
        class="btn btn-sm btn-primary"
        @click="isEditingProfile = !isEditingProfile">
        {{ isEditingProfile ? 'Cancel' : 'Edit Profile' }}
      </button>
    </div>

    <div v-if="!isEditingProfile">
      <p><strong>Branch:</strong> {{ student.branch || 'Not set' }}</p>
      <p><strong>CGPA:</strong> {{ student.cgpa || 'Not set' }}</p>
      <p><strong>Year:</strong> {{ student.year || 'Not set' }}</p>
      <p><strong>Education:</strong> {{ student.education || 'Not set' }}</p>
      <p><strong>Skills:</strong> {{ student.skills || 'Not set' }}</p>
      <p><strong>Phone:</strong> {{ student.phone || 'Not set' }}</p>
      <p><strong>Experience:</strong> {{ student.experience || 'Not set' }}</p>

      <div class="mt-3 p-3 border rounded">
        <strong>📄 Resume</strong>

        <div v-if="student.resume_path" class="mt-2">
          <span class="badge bg-success me-2">✓ Resume Uploaded</span>
          <div class="mt-2">
            <button class="btn btn-sm btn-info me-2" @click="downloadResume">
              ⬇️ Download Resume
            </button>
            <button class="btn btn-sm btn-danger" @click="deleteResume">
              🗑️ Delete Resume
            </button>
          </div>
        </div>

        <div v-else class="mt-2">
          <span class="badge bg-warning text-dark me-2">⚠ No Resume Uploaded</span>
          <div class="mt-2 d-flex align-items-center gap-2 flex-wrap">
            <input
              type="file"
              accept=".pdf,.doc,.docx"
              @change="handleResumeSelect"
              class="form-control form-control-sm"
              style="max-width: 300px;"
            />
            <button
              class="btn btn-sm btn-success"
              @click="uploadResume"
              :disabled="!resumeFile || uploadingResume">
              {{ uploadingResume ? '⏳ Uploading...' : '📤 Upload Resume' }}
            </button>
          </div>
          <small class="text-muted d-block mt-1">
            Accepted: PDF, DOC, DOCX
          </small>
        </div>
      </div>

      <p class="mt-3"><strong>Total Applications:</strong> {{ student.total_applications }}</p>
    </div>

    <div v-else>
      <div class="mb-2">
        <label class="form-label">Branch</label>
        <input v-model="profileForm.branch" class="form-control" />
      </div>
      <div class="mb-2">
        <label class="form-label">CGPA</label>
        <input v-model="profileForm.cgpa" type="number" step="0.1" class="form-control" />
      </div>
      <div class="mb-2">
        <label class="form-label">Year</label>
        <input v-model="profileForm.year" type="number" class="form-control" />
      </div>
      <div class="mb-2">
        <label class="form-label">Education</label>
        <textarea v-model="profileForm.education" class="form-control" rows="2"></textarea>
      </div>
      <div class="mb-2">
        <label class="form-label">Skills</label>
        <textarea v-model="profileForm.skills" class="form-control" rows="2"></textarea>
      </div>
      <div class="mb-2">
        <label class="form-label">Phone</label>
        <input v-model="profileForm.phone" class="form-control" />
      </div>
      <div class="mb-2">
        <label class="form-label">Experience</label>
        <textarea v-model="profileForm.experience" class="form-control" rows="2"></textarea>
      </div>
      <button class="btn btn-success mt-2" @click="updateProfile">
        Save Changes
      </button>
    </div>
  </div>

  <ul class="nav nav-tabs mb-3">
    <li class="nav-item">
      <a class="nav-link" :class="{ active: activeTab === 'drives' }"
         @click="activeTab = 'drives'" href="#">
        Available Drives
      </a>
    </li>
    <li class="nav-item">
      <a class="nav-link" :class="{ active: activeTab === 'applications' }"
         @click="activeTab = 'applications'" href="#">
        My Applications ({{ applications.length }})
      </a>
    </li>
    <li class="nav-item">
      <a class="nav-link" :class="{ active: activeTab === 'interviews' }"
         @click="activeTab = 'interviews'" href="#">
        Interviews ({{ interviews.length }})
      </a>
    </li>
    <li class="nav-item">
      <a class="nav-link" :class="{ active: activeTab === 'placements' }"
         @click="activeTab = 'placements'" href="#">
        Offers & Placements ({{ placements.length }})
      </a>
    </li>
  </ul>

  <div v-if="activeTab === 'drives'">
    <div class="mb-3">
      <input
        v-model="searchQuery"
        @input="fetchDrives"
        class="form-control"
        placeholder="Search by drive or company..."
      />
    </div>

    <h3>Available Drives</h3>

    <div v-if="drives.length === 0">
      <p>No approved drives found.</p>
    </div>

    <div v-else class="row">
      <div
        v-for="drive in drives"
        :key="drive.drive_id"
        class="col-md-6 mb-3">
        <div class="card h-100">
          <div class="card-body">
            <h5 class="card-title">{{ drive.title }}</h5>
            <h6 class="card-subtitle mb-2 text-muted">{{ drive.company }}</h6>
            <p class="mb-1"><strong>Skills:</strong> {{ drive.required_skills || 'N/A' }}</p>
            <p class="mb-1"><strong>Experience:</strong> {{ drive.experience_required || 'N/A' }}</p>
            <p class="mb-1"><strong>Salary:</strong> {{ drive.salary ? `₹${drive.salary} LPA` : 'N/A' }}</p>
            <p class="mb-1"><strong>Benefits:</strong> {{ drive.benefits || 'N/A' }}</p>
            <p class="mb-1"><strong>CGPA Required:</strong> {{ drive.eligibility_cgpa }}</p>
            <p class="mb-1"><strong>Deadline:</strong> {{ drive.deadline }}</p>

            <div class="mt-3">
              <button
                v-if="!drive.application_status"
                class="btn btn-sm btn-success"
                @click="applyToDrive(drive.drive_id)"
                :disabled="student?.is_placed">
                {{ student?.is_placed ? 'Already Placed' : 'Apply' }}
              </button>

              <span v-else-if="drive.application_status === 'Applied'"
                    class="badge bg-secondary">Applied</span>
              <span v-else-if="drive.application_status === 'Shortlisted'"
                    class="badge bg-info">Shortlisted</span>
              <span v-else-if="drive.application_status === 'Interview'"
                    class="badge bg-warning">Interview Scheduled</span>
              <span v-else-if="drive.application_status === 'Offer'"
                    class="badge bg-primary">Offer Received 🎊</span>
              <span v-else-if="drive.application_status === 'Placed'"
                    class="badge bg-success">Placed 🎉</span>
              <span v-else-if="drive.application_status === 'Rejected'"
                    class="badge bg-danger">Rejected</span>
            </div>

            <div v-if="drive.status_msg" class="alert alert-info mt-2 mb-0">
              {{ drive.status_msg }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <div v-if="activeTab === 'applications'">
    <h3>My Applications</h3>

    <div v-if="applications.length === 0">
      <p>No applications yet.</p>
    </div>

    <table v-else class="table table-bordered">
      <thead>
        <tr>
          <th>Drive</th>
          <th>Company</th>
          <th>Status</th>
          <th>Feedback</th>
          <th>Applied On</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="app in applications" :key="app.application_id">
          <td>{{ app.drive_title }}</td>
          <td>{{ app.company }}</td>
          <td>
            <span class="badge"
              :class="{
                'bg-secondary': app.status === 'Applied',
                'bg-info': app.status === 'Shortlisted',
                'bg-warning': app.status === 'Interview',
                'bg-primary': app.status === 'Offer',
                'bg-success': app.status === 'Placed',
                'bg-danger': app.status === 'Rejected'
              }">
              {{ app.status }}
            </span>
          </td>
          <td>{{ app.feedback || '-' }}</td>
          <td>{{ app.applied_on }}</td>
        </tr>
      </tbody>
    </table>
  </div>

  <div v-if="activeTab === 'interviews'">
    <h3>My Interviews</h3>

    <div v-if="interviews.length === 0">
      <p>No interviews scheduled yet.</p>
    </div>

    <div v-else class="row">
      <div v-for="interview in interviews" :key="interview.id" class="col-md-6 mb-3">
        <div class="card">
          <div class="card-body">
            <h5 class="card-title">{{ interview.company_name }}</h5>
            <h6 class="card-subtitle mb-2 text-muted">{{ interview.drive_title }}</h6>
            <p class="mb-1"><strong>Date & Time:</strong> {{ interview.interview_date }}</p>
            <p class="mb-1"><strong>Mode:</strong> {{ interview.interview_mode }}</p>
            <p class="mb-1"><strong>Location:</strong> {{ interview.location || 'TBD' }}</p>
            <p class="mb-1">
              <strong>Status:</strong>
              <span class="badge bg-warning ms-1">{{ interview.status }}</span>
            </p>
            <div v-if="interview.notes" class="alert alert-info mt-2 mb-0">
              <strong>Notes:</strong> {{ interview.notes }}
            </div>
            <div v-if="interview.feedback" class="alert alert-secondary mt-2 mb-0">
              <strong>Feedback:</strong> {{ interview.feedback }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <div v-if="activeTab === 'placements'">
    <h3>Offers & Placements</h3>

    <div v-if="placements.length === 0">
      <p>No offers or placements yet.</p>
    </div>

    <div v-else class="row">
      <div v-for="placement in placements" :key="placement.id" class="col-md-6 mb-3">
        <div class="card">
          <div class="card-body">
            <h5 class="card-title">{{ placement.company_name }}</h5>
            <h6 class="card-subtitle mb-2 text-muted">{{ placement.drive_title }}</h6>
            <p class="mb-1"><strong>Position:</strong> {{ placement.position }}</p>
            <p class="mb-1"><strong>Salary:</strong> ₹{{ placement.salary }} LPA</p>
            <p class="mb-1"><strong>Joining Date:</strong> {{ placement.joining_date }}</p>
            <p class="mb-1"><strong>Placed On:</strong> {{ placement.placed_on }}</p>
            <p class="mb-1">
              <strong>Status:</strong>
              <span class="badge ms-1"
                :class="{
                  'bg-primary': placement.status === 'Offer',
                  'bg-info': placement.status === 'Accepted',
                  'bg-success': placement.status === 'Joined',
                  'bg-secondary': placement.status === 'Declined'
                }">
                {{ placement.status }}
              </span>
            </p>

            <div v-if="placement.status === 'Offer'" class="mt-3">
              <button class="btn btn-success btn-sm me-2"
                      @click="respondToOffer(placement.id, 'accept')">
                Accept Offer
              </button>
              <button class="btn btn-danger btn-sm"
                      @click="respondToOffer(placement.id, 'decline')">
                Decline Offer
              </button>
            </div>

            <div v-else-if="placement.status === 'Accepted'"
                 class="alert alert-success mt-2 mb-0">
              🎉 You have accepted this offer!
            </div>

            <div v-else-if="placement.status === 'Joined'"
                 class="alert alert-success mt-2 mb-0">
              🎊 Congratulations on joining!
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

</div>
</template>

<style scoped>
.card {
  border-radius: 8px;
}
.badge {
  font-size: 0.9rem;
  padding: 6px 10px;
}
.nav-link {
  cursor: pointer;
}
.gap-2 {
  gap: 0.5rem;
}
</style>
