<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, computed } from 'vue'
import { useRoute } from 'vue-router'
import { useProjectStore } from '@/stores/project'
import { type Agent, type Message, type Project } from '@/types'

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

function formatTimestamp(timestamp: string): string {
  // Ensure timestamp is treated as UTC if it doesn't have timezone info
  const utcTimestamp = timestamp.endsWith('Z') ? timestamp : timestamp + 'Z'

  // If timestamp is current day in local time zone, format it as 'HH:mm'
  const currentDate = new Date()
  const messageDate = new Date(utcTimestamp)
  if (
    messageDate.getUTCFullYear() === currentDate.getUTCFullYear() &&
    messageDate.getUTCMonth() === currentDate.getUTCMonth() &&
    messageDate.getUTCDate() === currentDate.getUTCDate()
  ) {
    return new Date(utcTimestamp).toLocaleString('en-GB', {
      timeStyle: 'short',
      hour12: true,
    })
  }
  // Otherwise, format it as 'dd MMM yyyy, HH:mm'
  return new Date(utcTimestamp).toLocaleString('en-GB', {
    dateStyle: 'medium',
    timeStyle: 'short',
    hour12: true,
  })
}
</script>

<template>
  <div class="conversation">
    <div class="title-bar">
      <h1>{{ currentProject?.title }}</h1>
      <div class="status">
        <div v-if="projectStore.isLoading" class="loading">Loading conversation data...</div>
        <div v-else-if="projectStore.error" class="error">Error: {{ projectStore.error }}</div>
        <div v-else class="status-indicator" :class="connectionStatus">
          {{ connectionStatus }}
        </div>
      </div>
    </div>
    <div class="messages">
      <div
        v-for="(message, index) in currentProject?.messages"
        :key="index"
        :class="['message', message.agent_role]"
      >
        <div class="metadata">
          <div class="agent">@{{ message.agent_name }}</div>
          <div class="timestamp">{{ formatTimestamp(message.timestamp) }}</div>
        </div>
        <!-- TODO: Fix rendering to display markdown -->
        <div class="content">{{ message.content }}</div>
      </div>
    </div>
    <div class="input">
      <!-- TODO: Figure out why textarea clears after a certain amount of time-->
      <textarea
        id="message-input"
        v-model="newMessage"
        placeholder="Type your message here"
        @keydown.enter.exact.prevent="sendMessage"
        :disabled="connectionStatus !== 'connected'"
      />
      <button @click="sendMessage" :disabled="connectionStatus !== 'connected'">Send</button>
    </div>
  </div>
</template>

<style>
.agent {
  font-weight: bold;
}

.timestamp {
  font-size: 0.7rem;
  color: grey;
  align-self: flex-start;
}

.conversation {
  display: flex;
  flex-direction: column;
  width: 100%;
  height: 100%;
}

.messages {
  display: flex;
  flex-direction: column;
  overflow-y: scroll;
  gap: 1rem;
  margin: 1rem 0;
  width: 100%;
  height: 100%;
  align-self: center;
}

.input {
  width: 100%;
  display: flex;
  gap: 1rem;
  border: #555 1px solid;
  padding: 0.5rem;
  margin: 0.5rem 0;
}

.metadata {
  display: flex;
  gap: 0.5rem;
  justify-content: space-between;
  padding: 0 0 0.5rem 0;
}

textarea {
  width: 100%;
  padding: 0.5rem;
  background-color: black;
  color: white;
  border: none;
}

button {
  padding: 0.5rem 1rem;
  background-color: var(--vt-c-green);
  color: white;
  cursor: pointer;
}

.title-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #555;
}

.status-indicator {
  padding: 4px 8px;
  font-size: 0.8rem;
  color: white;
  border-radius: 1rem 0 0 1rem;
}

.status-indicator.connected {
  background-color: var(--vt-c-green);
}

.status-indicator.connecting {
  background-color: #ff9800;
}

.status-indicator.disconnected {
  background-color: #f44336;
}

.message {
  padding: 10px;
  border-radius: 0.5rem;
  /* border: grey 1px solid; */
}
.message.user {
  background-color: #000;
}

.message.assistant {
  background-color: #222;
}
</style>
