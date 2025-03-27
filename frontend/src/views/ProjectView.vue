<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, computed } from 'vue'
import { useRoute } from 'vue-router'
import { useProjectStore } from '@/stores/project'
import { type Agent, type Message, type Project } from '@/types'

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
const connectionStatus = ref<'connected' | 'disconnected' | 'connecting'>('disconnected')

function scrollToBottom() {
  setTimeout(() => {
    const messagesDiv = document.querySelector('.messages')
    if (messagesDiv) {
      messagesDiv.scrollTop = messagesDiv.scrollHeight
    }
  }, 50)
}

function connectWebSocket() {
  connectionStatus.value = 'connecting'
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
  }

  socket.value.onclose = () => {
    console.log('WebSocket connection closed')
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
  <div class="conversation">
    <div class="status">
      <div v-if="projectStore.isLoading" class="loading">Loading conversation data...</div>
      <div v-else-if="projectStore.error" class="error">Error: {{ projectStore.error }}</div>
      <div v-else class="status-indicator" :class="connectionStatus">
        Connection: {{ connectionStatus }}
      </div>
    </div>
    <div class="messages">
      <h1>{{ currentProject?.title }}</h1>
      <div
        v-for="(message, index) in currentProject?.messages"
        :key="index"
        :class="['message', message.agent_role]"
      >
        <div class="metadata">
          <span class="agent">{{ message.agent_name }}</span>
          <span>|</span>
          <span class="timestamp">{{ new Date(message.timestamp).toLocaleTimeString() }}</span>
        </div>
        <div class="content">{{ message.content }}</div>
      </div>
    </div>
    <div class="input">
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
.conversation {
  display: flex;
  flex-direction: column;
  width: 100%;
  height: 100%;
  overflow-y: hidden;
}

.status {
  padding: 1rem;
}

.messages {
  display: flex;
  flex-direction: column;
  overflow-y: scroll;
  gap: 1rem;
  border-radius: 0.5rem;
  padding: 1rem;
  width: 100%;
  align-self: center;
}

.input {
  width: 100%;
  display: flex;
  gap: 1rem;
  padding: 1rem;
}

.metadata {
  display: flex;
  gap: 0.5rem;
}

textarea {
  width: 100%;
  padding: 0.5rem;
  background-color: black;
  color: white;
}

button {
  padding: 0.5rem 1rem;
  background-color: var(--vt-c-green);
  color: white;
  cursor: pointer;
}

.status-indicator {
  padding: 4px 8px;
  font-size: 0.8rem;
  color: white;
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
  border: grey 1px solid;
}
.message.user {
  background-color: #000;
}

.message.assistant {
  background-color: #222;
}
</style>
