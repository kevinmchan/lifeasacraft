<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'
</script>

<template>
  <header>
    <div class="wrapper">
      <RouterLink to="/" class="logo">
        <div>lifeasacraft</div>
      </RouterLink>
      <nav>
        <RouterLink to="/" class="link">Home</RouterLink>
        <RouterLink to="/projects" class="link">Projects</RouterLink>
      </nav>
    </div>
  </header>

  <RouterView />
</template>

<style scoped>
.wrapper {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 0;
}

.logo {
  font-weight: light;
  font-family: 'roboto-mono', monospace;
  font-size: 1.5rem;
  margin: 0.5rem 0;
  color: inherit;
}

.logo:hover {
  cursor: pointer;
  background-color: inherit;
}

.link {
  padding: 0 1rem;
}
nav {
  display: flex;
}
</style>
