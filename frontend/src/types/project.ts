import { type Agent } from './agent'
import { type Message } from './message'

export interface Project {
  id: string
  title: string
  intention: string
  parent_project_id: string | null
  child_projects: Project[] | null
  messages: Message[]
  current_agent: Agent | null
}
