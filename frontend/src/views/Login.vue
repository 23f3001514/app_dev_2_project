
<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const email = ref('')
const password = ref('')
const router = useRouter()

const login = async () => {
  try {
    const res = await axios.post(
      'http://localhost:5000/api/auth/login', 
      { email: email.value, password: password.value },
      { withCredentials: true }
    )

    alert(res.data.message)

    if (res.data.role === 'admin') router.push('/admin')
    else if (res.data.role === 'company') router.push('/company')
    else if (res.data.role === 'student') router.push('/student')

  } catch (err) {
    alert(err.response?.data?.error || 'Login failed')
  }
}
</script>

<template>
<div class="login-page">
  <div class="container">
    <div class="row justify-content-center align-items-center min-vh-100">
      <div class="col-md-5">
        <div class="card shadow-lg border-0">
          <div class="card-body p-5">
            <h2 class="text-center mb-4 fw-bold">Welcome Back</h2>
            <p class="text-center text-muted mb-4">Login to your account</p>
            
            <form @submit.prevent="login">
              <div class="mb-3">
                <label class="form-label fw-semibold">Email</label>
                <input 
                  v-model="email" 
                  type="email" 
                  class="form-control form-control-lg" 
                  placeholder="Enter your email"
                  required
                />
              </div>
              
              <div class="mb-4">
                <label class="form-label fw-semibold">Password</label>
                <input 
                  v-model="password" 
                  type="password" 
                  class="form-control form-control-lg" 
                  placeholder="Enter your password"
                  required
                />
              </div>
              
              <button type="submit" class="btn btn-primary btn-lg w-100 mb-3">
                <i class="bi bi-box-arrow-in-right me-2"></i>
                Login
              </button>
            </form>
            
            <div class="text-center">
              <p class="mb-0">Don't have an account? 
                <router-link to="/register" class="text-primary fw-semibold">Register here</router-link>
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>
</template>

