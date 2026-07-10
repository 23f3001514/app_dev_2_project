<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()

const currentPath = computed(() => router.currentRoute.value.path)

const isLoggedIn = computed(() => {
  return currentPath.value.includes('/admin') || 
         currentPath.value.includes('/company') || 
         currentPath.value.includes('/student')
})

const userRole = computed(() => {
  if (currentPath.value.includes('/admin')) return 'Admin'
  if (currentPath.value.includes('/company')) return 'Company'
  if (currentPath.value.includes('/student')) return 'Student'
  return ''
})

const logout = async () => {
  if (!confirm('Are you sure you want to logout?')) return
  
  try {
    await axios.post('http://localhost:5000/api/auth/logout', {}, { 
      withCredentials: true 
    })
    
    await router.push('/login')
    
    setTimeout(() => {
      alert('Logged out successfully!')
    }, 100)
    
  } catch (err) {
    console.error('Logout failed', err)
    alert('Logout failed. Please try again.')
  }
}
</script>

<template>
<nav class="navbar navbar-expand-lg navbar-dark shadow-sm sticky-top navbar-custom">
  <div class="container-fluid px-4">
    <router-link to="/" class="navbar-brand fw-bold d-flex align-items-center">
      <i class="bi bi-mortarboard-fill me-2" style="font-size: 1.8rem;"></i>
      <span style="font-size: 1.4rem; letter-spacing: 1px;">Placement Portal</span>
    </router-link>
    
    <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
      <span class="navbar-toggler-icon"></span>
    </button>
    
    <div class="collapse navbar-collapse" id="navbarNav">
      <ul class="navbar-nav ms-auto align-items-lg-center gap-2">
        
        <!-- Not Logged In -->
        <template v-if="!isLoggedIn">
          <li class="nav-item">
            <router-link to="/" class="nav-link px-3 py-2">
              <i class="bi bi-house-door me-1"></i> Home
            </router-link>
          </li>
          <li class="nav-item">
            <router-link to="/login" class="nav-link px-3 py-2">
              <i class="bi bi-box-arrow-in-right me-1"></i> Login
            </router-link>
          </li>
          <li class="nav-item">
            <router-link to="/register" class="btn btn-light btn-sm px-4 py-2">
              <i class="bi bi-person-plus me-1"></i> Register
            </router-link>
          </li>
        </template>

        <!-- Logged In -->
        <template v-else>
          <li class="nav-item">
            <span class="badge bg-white text-dark px-4 py-2 fs-6">
              <i class="bi bi-person-circle me-2"></i>
              <strong>{{ userRole }}</strong>
            </span>
          </li>
          
          <li class="nav-item">
            <router-link 
              :to="`/${userRole.toLowerCase()}`"
              class="nav-link px-3 py-2">
              <i class="bi bi-speedometer2 me-1"></i> Dashboard
            </router-link>
          </li>
          
          <li class="nav-item">
            <button @click="logout" class="btn btn-danger px-4 py-2 logout-btn">
              <i class="bi bi-box-arrow-right me-2"></i>
              <strong>LOGOUT</strong>
            </button>
          </li>
        </template>

      </ul>
    </div>
  </div>
</nav>
</template>

<style scoped>
.navbar-custom {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
  min-height: 75px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.navbar-brand {
  transition: transform 0.3s ease;
}

.navbar-brand:hover {
  transform: scale(1.05);
}

.nav-link {
  font-weight: 500;
  font-size: 1.05rem;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.nav-link:hover {
  background-color: rgba(255, 255, 255, 0.15);
  transform: translateY(-2px);
}

.badge {
  border-radius: 25px;
  font-weight: 500;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.logout-btn {
  background: linear-gradient(135deg, #f5576c 0%, #f093fb 100%) !important;
  border: none;
  font-size: 1rem;
  font-weight: 700;
  border-radius: 25px;
  box-shadow: 0 4px 15px rgba(245, 87, 108, 0.4);
  transition: all 0.3s ease;
  letter-spacing: 0.5px;
}

.logout-btn:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 20px rgba(245, 87, 108, 0.5);
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%) !important;
}

.btn-light {
  font-weight: 600;
  border-radius: 25px;
  border: 2px solid white;
  transition: all 0.3s ease;
}

.btn-light:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(255, 255, 255, 0.3);
  background: white !important;
}

@media (max-width: 991px) {
  .navbar-nav {
    padding: 1rem 0;
  }
  
  .nav-item {
    margin: 0.5rem 0 !important;
  }
  
  .btn, .badge {
    width: 100%;
    text-align: center;
  }
}
</style>

