import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Project } from '@/types'

export const useProjectStore = defineStore('projects', () => {
  const projects = ref<Project[]>([])
  const isLoading = ref(false)
  const hasLoadedAll = ref(false)
  const error = ref<string | null>(null)

  // Fetch all projects
  async function fetchProjects() {
    // Skip if we've already loaded all projects
    if (hasLoadedAll.value) return projects.value

    isLoading.value = true
    error.value = null

    try {
      const response = await fetch('http://localhost:8000/project/all')
      if (!response.ok) throw new Error(`HTTP error: ${response.status}`)
      projects.value = await response.json()
      hasLoadedAll.value = true
      return projects.value
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Unknown error'
      console.error('Failed to fetch projects:', err)
      return []
    } finally {
      isLoading.value = false
    }
  }

  // Get a project by ID (with optional fetch if not found)
  async function getProject(id: string): Promise<Project | null> {
    // First check if we already have it
    const existingProject = projects.value.find((p) => p.id === id)
    if (existingProject) return existingProject

    // If we haven't loaded all projects yet, do that now
    if (!hasLoadedAll.value) {
      await fetchProjects()
      return projects.value.find((p) => p.id === id) || null
    }

    // We've loaded all projects but didn't find this one
    return null
  }

  return {
    projects,
    isLoading,
    error,
    fetchProjects,
    getProject,
    hasLoadedAll,
  }
})
