<script setup lang="ts"></script>

<template>
  <main>
    <div class="wrapper">
      <div class="mission-container">
        <div class="main-mission">
          <span class="logo">lifeasacraft</span>'s mission is to help me be better at the things
          that I care about
        </div>
        <ul>
          <li class="sub-mission">Learn to learn</li>
          <li class="sub-mission">Learn what it is that I care about</li>
          <li class="sub-mission">Be better at the things that I care about</li>
        </ul>
      </div>
    </div>
  </main>
</template>

<style scoped>
.logo {
  font-weight: bold;
  font-family: 'roboto-mono', monospace;
  font-size: x-large;
}

.main-mission {
  font-size: x-large;
}

ul {
  list-style-type: none; /* Remove default bullets */
  padding-left: 1rem; /* Remove default padding */
}

.sub-mission {
  position: relative;
  padding-left: 1.5rem;
  font-size: large;
  margin: 2rem 0;
}

.sub-mission::before {
  content: '→';
  position: absolute;
  left: -1rem;
  color: var(--vt-c-green);
  font-weight: bold;
}

main {
  height: 100%;
  width: 100%;
}
.wrapper {
  display: flex;
  height: 100%;
  align-items: center;
  justify-content: center;
}
</style>
