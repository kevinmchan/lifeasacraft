<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useProjectStore } from '@/stores/project'
import { type Project } from '@/types/project'

const router = useRouter()
const projectStore = useProjectStore()

const title = ref('')
const intention = ref('')
const parentProjectId = ref('')
const isLoading = ref(false)
const searchTerm = ref('')
const isShowingDropdown = ref(false)
const formError = ref('')

// Fetch projects for dropdown
onMounted(async () => {
  await projectStore.fetchProjects()
})

// Filter projects based on search term
const filteredProjects = ref<Project[]>([])
function updateFilteredProjects() {
  if (!searchTerm.value.trim()) {
    filteredProjects.value = projectStore.projects
    return
  }

  const term = searchTerm.value.toLowerCase()
  filteredProjects.value = projectStore.projects.filter((project) =>
    project.title.toLowerCase().includes(term),
  )
}

function selectProject(project: Project) {
  parentProjectId.value = project.id
  searchTerm.value = project.title
  isShowingDropdown.value = false
}

async function submitForm() {
  // Validate
  if (!title.value.trim()) {
    formError.value = 'Title is required'
    return
  }

  // Show loading state
  isLoading.value = true
  formError.value = ''

  try {
    // Create project
    const newProject = await projectStore.createProject({
      title: title.value,
      intention: intention.value,
      parentProjectId: parentProjectId.value || null,
    })

    // Navigate to the new project
    router.push(`/projects/${newProject.id}`)
  } catch (error) {
    console.error('Failed to create project:', error)
    formError.value = 'Failed to create project. Please try again.'
    isLoading.value = false
  }
}

function hideDropdown() {
  setTimeout(() => {
    isShowingDropdown.value = false
  }, 200) // Delay to allow click event to register
}

function showDropdown() {
  isShowingDropdown.value = true
  updateFilteredProjects()
}
</script>

<template>
  <div class="new-project-container">
    <h1>Create New Project</h1>

    <form @submit.prevent="submitForm" class="project-form">
      <div class="form-group">
        <label for="title">Title</label>
        <input
          id="title"
          v-model="title"
          type="text"
          placeholder="Project title"
          :disabled="isLoading"
          required
        />
      </div>

      <div class="form-group">
        <label for="intention">Intention</label>
        <textarea
          id="intention"
          v-model="intention"
          placeholder="What's the intention of this project?"
          :disabled="isLoading"
          rows="4"
          required
        ></textarea>
      </div>

      <div class="form-group">
        <label for="parent">Parent Project (optional)</label>
        <div class="dropdown-container">
          <input
            id="parent"
            v-model="searchTerm"
            type="text"
            placeholder="Search for a project"
            :disabled="isLoading"
            @input="updateFilteredProjects"
            @focus="showDropdown"
            @blur="hideDropdown"
          />
          <div v-if="isShowingDropdown && filteredProjects.length" class="dropdown">
            <div
              v-for="project in filteredProjects"
              :key="project.id"
              class="dropdown-item"
              @click="selectProject(project)"
            >
              <span>{{ project.title }}</span>
              <span>{{ project.id }}</span>
            </div>
          </div>
        </div>
      </div>

      <div v-if="formError" class="error-message">{{ formError }}</div>

      <button type="submit" :disabled="isLoading" class="submit-button">
        <span v-if="!isLoading">Create Project</span>
        <div v-else class="loader"></div>
      </button>
    </form>
  </div>
</template>

<style scoped>
.new-project-container {
  width: 100%;
  margin: 2rem auto;
  padding: 1rem;
}

h1 {
  margin-bottom: 1.5rem;
}

.project-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

label {
  font-weight: bold;
}

input,
textarea {
  padding: 0.75rem;
  border: 1px solid #444;
  border-radius: 4px;
  background-color: #222;
  color: #fff;
  width: 100%;
}

.dropdown-container {
  position: relative;
}

.dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background-color: #333;
  border: 1px solid #444;
  border-radius: 0 0 4px 4px;
  z-index: 10;
  max-height: 200px;
  overflow-y: auto;
}

.dropdown-item {
  display: flex;
  justify-content: space-between;
  padding: 0.75rem;
  cursor: pointer;
}

.dropdown-item:hover {
  background-color: #444;
}

.error-message {
  color: #ff6b6b;
  font-size: 0.9rem;
}

.submit-button {
  padding: 0.75rem;
  background-color: var(--vt-c-green);
  color: #000;
  border: none;
  border-radius: 4px;
  font-weight: bold;
  cursor: pointer;
  display: flex;
  justify-content: center;
  align-items: center;
  height: 48px;
}

.submit-button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.loader {
  width: 24px;
  height: 24px;
  border: 3px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top-color: #fff;
  animation: spin 1s ease-in-out infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
