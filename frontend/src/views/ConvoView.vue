<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue';

interface Message {
  role: 'user' | 'assistant';
  agent: string;
  content: string;
  timestamp: string;
}

interface Conversation {
  title: string;
  messages: Message[];
}

const conversation = ref<Conversation>({
  title: 'Loading conversation...',
  messages: []
});

const isLoading = ref(true);
const error = ref<string | null>(null);
const newMessage = ref('');
const socket = ref<WebSocket | null>(null);
const connectionStatus = ref<'connected' | 'disconnected' | 'connecting'>('disconnected');

async function fetchConversation() {
  isLoading.value = true;
  error.value = null;
  
  try {
    const response = await fetch('http://localhost:8000/convo');
    
    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }
    
    const data = await response.json();
    conversation.value = data;
  } catch (err) {
    console.error('Failed to fetch conversation:', err);
    error.value = err instanceof Error ? err.message : 'Unknown error occurred';
  } finally {
    isLoading.value = false;
  }
}

function connectWebSocket() {
  connectionStatus.value = 'connecting';
  socket.value = new WebSocket('ws://localhost:8000/ws/chat');
  
  socket.value.onopen = () => {
    console.log('WebSocket connected');
    connectionStatus.value = 'connected';
  };
  
  socket.value.onmessage = (event) => {
    const data = JSON.parse(event.data);
    
    // Check if it's a receipt/acknowledgment message
    if (data.type === 'receipt' || data.status === 'received') {
      // Handle receipt
      // TODO: Update some UI state to show the message was delivered
      console.log('Message received by server:', data);     
    } 
    // Check if it's a conversation message to be added to the chat
    else if (data.role && data.content) {
      // Ensure it has the correct structure before adding to conversation
      if (data.role === 'assistant' || data.role === 'user') {
        // It's a valid message, add it to the conversation
        conversation.value.messages.push(data);
        
        // You might want to scroll to the new message
        setTimeout(() => {
          const messagesDiv = document.querySelector('.messages');
          if (messagesDiv) {
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
          }
        }, 50);
      }
    } 
    // Handle any other message types
    else {
      console.warn('Received unknown message format:', data);
    }
  };
  
  socket.value.onerror = (error) => {
    console.error('WebSocket error:', error);
    connectionStatus.value = 'disconnected';
  };
  
  socket.value.onclose = () => {
    console.log('WebSocket connection closed');
    connectionStatus.value = 'disconnected';
    // Attempt to reconnect after a delay
    setTimeout(connectWebSocket, 3000);
  };
}

function sendMessage() {
  if (!newMessage.value.trim() || !socket.value || socket.value.readyState !== WebSocket.OPEN) return;
  
  const message: Message = {
    role: 'user',
    agent: 'user', // You might want to dynamically set this
    content: newMessage.value,
    timestamp: new Date().toISOString()
  };
  
  // Add to local conversation immediately
  conversation.value.messages.push(message);
  
  // Send to server
  socket.value.send(JSON.stringify(message));
  
  // Clear input
  newMessage.value = '';
}

onMounted(() => {
  fetchConversation()
  .then(() => {
    connectWebSocket();
  })
  .then(() => {
    const messagesDiv = document.querySelector('.messages');
    if (messagesDiv) {
      messagesDiv.scrollTop = messagesDiv.scrollHeight;
    }
  });
});

onBeforeUnmount(() => {
  if (socket.value) {
    socket.value.close();
  }
});
</script>

<template>
  <div class="conversation">
    <div class="status">
      <div v-if="isLoading" class="loading">Loading conversation data...</div>
      <div v-else-if="error" class="error">Error: {{ error }}</div>
      <div v-else class="status-indicator" :class="connectionStatus">
        Connection: {{ connectionStatus }}
      </div>
    </div>
    <div class="messages">
      <h1>{{ conversation.title }}</h1>
      <div 
        v-for="(message, index) in conversation.messages" 
        :key="index"
        :class="['message', message.role]"
      >
        <div class="metadata">
          <span class="agent">{{ message.agent }}</span>
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
        @keyup.enter="sendMessage"
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
