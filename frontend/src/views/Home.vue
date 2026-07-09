
<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

</script>

<template>
<div class="home-page">
  <!-- Hero Section -->
  <section class="hero-section text-white text-center py-5">
    <div class="container">
      <div class="row align-items-center">
        <div class="col-lg-6 text-lg-start mb-4 mb-lg-0">
          <h1 class="display-3 fw-bold mb-4 animate-fadeInUp">
            Welcome to<br>
            <span class="text-warning">Placement Portal</span>
          </h1>
          <div class="d-flex gap-3 justify-content-lg-start justify-content-center animate-fadeInUp" 
               style="animation-delay: 0.4s">
            <button @click="router.push('/register')" class="btn btn-warning btn-lg px-4">
              Get Started
            </button>
            <button @click="router.push('/login')" class="btn btn-outline-primary btn-lg px-4">
              Login
            </button>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- Footer -->
  <footer class="footer bg-dark text-white py-4">
    <div class="container text-center">
      <p class="mb-0">© 2026 Placement Portal. All Rights Reserved.</p>
      <p class="small text-muted mt-2">Made with ❤️ for College Placements</p>
    </div>
  </footer>
</div>
</template>

