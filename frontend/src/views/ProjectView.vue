<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { useRoute } from 'vue-router'
import { useProjectStore } from '@/stores/project'
import { type Agent, type Message, type Project } from '@/types'
import Conversation from '@/components/Conversation.vue'

// TODO: Refactor to extract components and socket logic
// TODO: Add additional logging

const projectStore = useProjectStore()
const user: Agent = {
  // TODO: dynamically set user
  id: 'kevin',
  name: 'kevin',
  role: 'user',
  model: 'user',
}

const currentProject = ref<Project | null>(null)
const newMessage = ref<string>('')
const socket = ref<WebSocket | null>(null)
const connectionStatus = ref<'connected' | 'disconnected' | 'connecting' | 'reconnecting'>(
  'disconnected',
)
const maxReconnectAttempts = ref(5)
const currentReconnectAttempt = ref(0)
const reconnectTimer = ref<number | null>(null)

function scrollToBottom() {
  setTimeout(() => {
    const messagesDiv = document.querySelector('.messages')
    if (messagesDiv) {
      messagesDiv.scrollTop = messagesDiv.scrollHeight
    }
  }, 50)
}

function handleReconnect() {
  if (currentReconnectAttempt.value < maxReconnectAttempts.value) {
    const delay = Math.min(1000 * Math.pow(2, currentReconnectAttempt.value), 30000)
    console.log(`Attempting to reconnect in ${delay / 1000} seconds...`)

    // Clear any existing timer
    if (reconnectTimer.value) window.clearTimeout(reconnectTimer.value)

    // Set new reconnect timer with exponential backoff
    reconnectTimer.value = window.setTimeout(() => {
      currentReconnectAttempt.value++
      connectWebSocket(true)
    }, delay)
  }
}

function connectWebSocket(isReconnect = false) {
  if (isReconnect) {
    connectionStatus.value = 'reconnecting'
  } else {
    connectionStatus.value = 'connecting'
    // Reset reconnect attempts on fresh connects
    currentReconnectAttempt.value = 0
  }

  socket.value = new WebSocket(`ws://localhost:8000/chat/${currentProject.value?.id}/ws`)

  socket.value.onopen = () => {
    console.log('WebSocket connected')
    connectionStatus.value = 'connected'
  }

  socket.value.onmessage = (event) => {
    const data = JSON.parse(event.data)
    console.log('Message received by server:', data)

    // Check if it's a receipt/acknowledgment message
    if (data.type === 'receipt' || data.status === 'received') {
      // Handle receipt
      // TODO: Update some UI state to show the message was delivered
      console.log('Sent message has been acknowledged')
    }
    // Check if it's a conversation message to be added to the chat
    else if (data.agent_role && data.content) {
      // Ensure it has the correct structure before adding to conversation
      // TODO: Handle full message validation and error handling
      if (data.agent_role === 'assistant' || data.agent_role === 'user') {
        // It's a valid message, add it to the conversation
        const message: Message = {
          content: data.content,
          agent_name: data.agent_name,
          agent_role: data.agent_role,
          agent_model: data.agent_model,
          agent_params: data.agent_params,
          timestamp: data.timestamp,
        }
        currentProject.value?.messages.push(message)

        // You might want to scroll to the new message
        scrollToBottom()
      }
    }
    // Handle any other message types
    else {
      console.warn('Received unknown message format:', data)
    }
  }

  socket.value.onerror = (error) => {
    console.error('WebSocket error:', error)
    connectionStatus.value = 'disconnected'
    handleReconnect()
  }

  socket.value.onclose = (event) => {
    console.log('WebSocket connection closed', event)
    connectionStatus.value = 'disconnected'
  }
}

function sendMessage() {
  if (!newMessage.value.trim() || !socket.value || socket.value.readyState !== WebSocket.OPEN)
    return

  const message: Message = {
    content: newMessage.value,
    agent_role: user.role,
    agent_model: user.model,
    agent_name: user.name,
    timestamp: new Date().toISOString(),
  }

  // Add to local conversation immediately
  currentProject.value?.messages.push(message)

  // Send to server
  // TODO: BUG - user submitted messages doesn't get broadcasted to other clients, but the other clients receive the server (assistant) response
  socket.value.send(JSON.stringify(message))

  // Clear input
  newMessage.value = ''

  // Scroll to the new message
  setTimeout(() => {
    const messagesDiv = document.querySelector('.messages')
    if (messagesDiv) {
      messagesDiv.scrollTop = messagesDiv.scrollHeight
    }
  }, 50)
}

onMounted(async () => {
  const route = useRoute()
  const projectId = route.params.id as string
  const project = await projectStore.getProject(projectId)

  if (project) {
    currentProject.value = project
    connectWebSocket()
    scrollToBottom()
  } else {
    // Handle not found case
    console.error(`Project with ID ${projectId} not found`)
  }
})

onBeforeUnmount(() => {
  if (socket.value) {
    socket.value.close()
  }
})
</script>

<template>
  <div class="project-container" v-if="currentProject">
    <Conversation
      :title="currentProject?.title || ''"
      :connectionStatus="connectionStatus"
      :messages="currentProject?.messages"
      :isLoading="projectStore.isLoading"
      :error="projectStore.error"
      :onSendMessage="sendMessage"
      v-model:newMessage="newMessage"
    />
  </div>
  <div v-else>
    <p>Could not find project.</p>
  </div>
</template>

<style>
.project-container {
  width: 100%;
}
</style>
