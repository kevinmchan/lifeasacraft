export type AgentRole = 'user' | 'assistant'
export type AgentModel = 'user' | 'o3-mini'

export interface Agent {
  id: string
  role: AgentRole
  model: AgentModel
  name: string
  params?: object
}
