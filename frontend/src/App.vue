<template>
  <v-app id="app">
    <router-view />
  </v-app>
</template>

<script lang="ts" setup>
import { onMounted } from 'vue'

// Сообщаем Telegram что приложение готово, когда компонент смонтирован
onMounted(() => {
  // Сообщаем Telegram WebApp, что приложение готово
  if (window.Telegram && window.Telegram.WebApp) {
    window.Telegram.WebApp.ready();
  }
})
</script>

<style>
html, body {
  margin: 0;
  padding: 0;
  height: 100%;
  width: 100%;
  overscroll-behavior: none;
  font-family: 'GeistSans', sans-serif;
  overflow-x: hidden;
  max-width: 100vw;
  position: relative;
  box-sizing: border-box;
}

#app {
  min-height: 100vh;
  min-height: calc(var(--vh, 1vh) * 100);
  width: 100%;
  max-width: 100vw;
  -webkit-overflow-scrolling: touch;
  font-family: 'GeistSans', sans-serif;
  position: relative;
  overflow-x: hidden;
  box-sizing: border-box;
}

/* Более мягкая фиксация для мобильных устройств */
@media (max-width: 768px) {
  html, body {
    overflow-x: hidden;
    width: 100%;
    max-width: 100vw;
  }
  
  #app {
    overflow-y: auto;
    overflow-x: hidden;
    width: 100%;
    max-width: 100%;
    height: 100%;
  }
  
  .v-container {
    max-width: 100%;
    padding-left: 16px;
    padding-right: 16px;
    box-sizing: border-box;
  }
}

/* Применяем шрифт Geist глобально */
.v-application {
  font-family: 'GeistSans', sans-serif !important;
  overflow-x: hidden;
  max-width: 100vw;
}

/* Исправление для iOS Safari */
@supports (-webkit-touch-callout: none) {
  #app {
    min-height: -webkit-fill-available;
  }
}
</style>
