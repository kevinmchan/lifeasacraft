import { type AgentRole, type AgentModel } from './agent'

export interface Message {
  content: string
  agent_name: string
  agent_role: AgentRole
  agent_model: AgentModel
  agent_params?: object
  timestamp: string
}
