<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'
</script>

<template>
  <header>
    <div class="wrapper">
      <RouterLink to="/" class="logo">
        <div>/lifeasacraft</div>
      </RouterLink>
      <nav>
        <RouterLink to="/" class="link">Home</RouterLink>
        <RouterLink to="/projects" class="link">Projects</RouterLink>
      </nav>
    </div>
  </header>
  <div class="main">
    <RouterView />
  </div>
</template>

<style scoped>
.main {
  padding: 0.25rem;
  display: flex;
  height: 100%;
  overflow-y: hidden;
}
.wrapper {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 0;
}

.logo {
  font-weight: bold;
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
