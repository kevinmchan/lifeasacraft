import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Agent } from '@/types'

export const useAgentStore = defineStore('agents', () => {
  const agents = ref<Agent[]>([])
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // Fetch all agents
  async function fetchAgents(): Promise<Agent[]> {
    isLoading.value = true
    error.value = null

    try {
      const response = await fetch('http://localhost:8000/agent/all')
      if (!response.ok) throw new Error(`HTTP error: ${response.status}`)
      agents.value = await response.json()
      return agents.value
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Unknown error'
      console.error('Failed to fetch agents:', err)
      return []
    } finally {
      isLoading.value = false
    }
  }

  // Get an agent by ID
  async function getAgent(id: string): Promise<Agent | null> {
    // TODO: Future performance opportunity - don't need to fetch all agents
    await fetchAgents()
    return agents.value.find((a) => a.id === id) || null
  }

  // Create an agent
  async function createAgent(agentData: { name: string; description: string; projectId: string }) {
    isLoading.value = true
    error.value = null

    try {
      const response = await fetch('http://localhost:8000/agent/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: agentData.name,
          description: agentData.description,
          project_id: agentData.projectId,
        }),
      })
      if (!response.ok) throw new Error(`HTTP error: ${response.status}`)
      const newAgent = await response.json()
      agents.value.push(newAgent)
      return newAgent
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Unknown error'
      console.error('Failed to create agent:', err)
      return null
    } finally {
      isLoading.value = false
    }
  }

  // Update an agent
  async function updateAgent(agentId: string, agentData: Partial<Agent>) {
    isLoading.value = true
    error.value = null

    try {
      const response = await fetch(`http://localhost:8000/agent/${agentId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(agentData),
      })
      if (!response.ok) throw new Error(`HTTP error: ${response.status}`)
      const updatedAgent = await response.json()
      const index = agents.value.findIndex((a) => a.id === agentId)
      if (index !== -1) {
        agents.value[index] = updatedAgent
      }
      return updatedAgent
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Unknown error'
      console.error('Failed to update agent:', err)
      return null
    } finally {
      isLoading.value = false
    }
  }

  return {
    agents,
    isLoading,
    error,
    fetchAgents,
    getAgent,
    createAgent,
    updateAgent,
  }
})
