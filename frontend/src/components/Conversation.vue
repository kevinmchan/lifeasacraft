<script setup lang="ts">
import { marked } from 'marked'
import DOMPurify from 'dompurify'
import { type PropType } from 'vue'

import { type Message } from '@/types'

const props = defineProps({
  title: {
    type: String,
    required: true,
  },
  connectionStatus: {
    type: String,
    required: true,
  },
  isLoading: {
    type: Boolean,
    required: true,
  },
  error: {
    type: [String, Object] as PropType<string | null>,
    required: false,
    default: null,
  },
  messages: {
    type: Array<Message>,
    required: true,
  },
  onSendMessage: {
    type: Function,
    required: true,
  },
  newMessage: {
    type: String,
    required: true,
  },
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

function renderMarkdown(content: string): string {
  const parsedContent = marked.parse(content, { async: false })
  const sanitizedContent = DOMPurify.sanitize(parsedContent)
  return sanitizedContent
}

const emit = defineEmits(['update:newMessage'])
</script>

<template>
  <div class="conversation">
    <div class="title-bar">
      <h1>{{ title }}</h1>
      <div class="status">
        <div v-if="isLoading" class="loading">Loading conversation data...</div>
        <div v-else-if="error" class="error">Error: {{ error }}</div>
        <div v-else class="status-indicator" :class="connectionStatus">
          {{ connectionStatus }}
        </div>
      </div>
      <!-- <div class="settings"></div> -->
    </div>
    <div class="messages">
      <div
        v-for="(message, index) in messages"
        :key="index"
        :class="['message', message.agent_role]"
      >
        <div class="metadata">
          <div class="agent">@{{ message.agent_name }}</div>
          <div class="timestamp">{{ formatTimestamp(message.timestamp) }}</div>
        </div>
        <div class="content" v-html="renderMarkdown(message.content)" />
      </div>
    </div>
    <div class="input">
      <!-- TODO: Figure out why textarea clears after a certain amount of time-->
      <textarea
        id="message-input"
        :value="newMessage"
        placeholder="Type your message here"
        @input="emit('update:newMessage', ($event.target as HTMLTextAreaElement)?.value || '')"
        @keydown.enter.exact.prevent="(event) => onSendMessage(event)"
        :disabled="connectionStatus !== 'connected'"
      />
      <button @click="(event) => onSendMessage(event)" :disabled="connectionStatus !== 'connected'">
        Send
      </button>
    </div>
  </div>
  <div class="setting-container"></div>
</template>

<style scoped>
.conversation {
  display: flex;
  flex-direction: column;
  width: 100%;
  height: 100%;
}

textarea {
  width: 100%;
  padding: 0.5rem;
  background-color: black;
  color: white;
  border: none;
}
.agent {
  font-weight: bold;
}

.timestamp {
  font-size: 0.7rem;
  color: grey;
  align-self: flex-start;
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
