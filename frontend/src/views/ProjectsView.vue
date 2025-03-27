<script setup lang="ts">
import { onMounted } from 'vue'

import { useProjectStore } from '@/stores/project'

const projectStore = useProjectStore()

onMounted(async () => {
  projectStore.fetchProjects()
})
</script>

<template>
  <div>
    <h1>Projects</h1>
    <div v-if="projectStore.isLoading" class="loading">Loading projects...</div>
    <div v-else-if="projectStore.error" class="error">Error: {{ projectStore.error }}</div>
    <div v-else class="project-grid">
      <div v-for="(project, index) in projectStore.projects" :key="index" class="project-container">
        <router-link :to="`/projects/${project.id}`" custom v-slot="{ navigate }">
          <div
            class="project"
            @click="navigate"
            @keyup.enter="() => navigate()"
            role="link"
            tabindex="0"
          >
            <div class="project-title">{{ project.title }}</div>
            <div class="project-intention">{{ project.intention }}</div>
          </div>
        </router-link>
      </div>
    </div>
  </div>
</template>

<style scoped>
.project-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 1rem;
}

.project-container {
  padding: 1rem;
  border-radius: 0.5rem;
  border: 1px solid var(--vt-c-green);
  color: inherit;
  cursor: pointer;
}

.project-container:hover {
  background-color: var(--vt-c-green);
  color: white;
}

.project-title {
  font-size: large;
  font-weight: bold;
}

.project-intention {
  font-size: small;
}
</style>
