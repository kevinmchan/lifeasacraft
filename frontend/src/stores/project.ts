import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Project } from '@/types'

export const useProjectStore = defineStore('projects', () => {
  const projects = ref<Project[]>([])
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // Fetch all projects
  // TODO: Update data model on server and client to only fetch project metadata
  // and not the entire project; we can't rely on cached project data e.g. the
  // project may have received new messages since the initial fetchProjects and
  // so we should fetch the entire project by id every time we call getProject
  async function fetchProjects() {
    isLoading.value = true
    error.value = null

    try {
      const response = await fetch('http://localhost:8000/project/all')
      if (!response.ok) throw new Error(`HTTP error: ${response.status}`)
      projects.value = await response.json()
      return projects.value
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Unknown error'
      console.error('Failed to fetch projects:', err)
      return []
    } finally {
      isLoading.value = false
    }
  }

  // Get a project by ID
  async function getProject(id: string): Promise<Project | null> {
    // TODO: Stop getting all projects every time we want to get a project
    // and instead just get the project by id
    await fetchProjects()
    return projects.value.find((p) => p.id === id) || null
  }

  async function createProject(projectData: {
    title: string
    intention: string
    parentProjectId: string | null
  }) {
    isLoading.value = true
    error.value = null

    try {
      const response = await fetch('http://localhost:8000/project/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          title: projectData.title,
          intention: projectData.intention,
          parent_project_id: projectData.parentProjectId,
        }),
      })
      if (!response.ok) throw new Error(`HTTP error: ${response.status}`)
      const newProject = await response.json()
      projects.value.push(newProject)
      return newProject
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Unknown error'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  return {
    projects,
    isLoading,
    error,
    fetchProjects,
    getProject,
    createProject,
  }
})
