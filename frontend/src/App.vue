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
        <RouterLink to="/">Home</RouterLink>
        <RouterLink to="/convo">Conversations</RouterLink>
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
  padding: 0 1rem;
}

.logo {
  font-weight: 100;
  font-size: 1.5rem;
  padding: 0.25rem 1rem;
  margin: 0.5rem 0;
  border-radius: 0.5rem;
  border: 1px solid var(--vt-c-green);
  color: inherit;
}

.logo:hover {
  background-color: var(--vt-c-green);
  color: white;
  cursor: pointer;
}

nav {
  display: flex;
  gap: 1rem;
  padding: 0.5rem;
}
</style>
