<template>
  <v-btn
    class="login-button no-outline"
    size="x-large"
    @click="handleLogin"
    :loading="loading"
    :disabled="loading"
    color="white"
    variant="tonal"
  >
    <template v-if="loading">
      <span class="loading-text">Идет загрузка<span class="loading-dots"></span></span>
    </template>
    <template v-else>
      <span class="login-text">
        <v-icon class="mr-2" color="black">mdi-telegram</v-icon>
        Войти через Telegram
      </span>
    </template>
  </v-btn>
</template>

<script setup lang="ts">
const props = defineProps<{
  handleLogin: () => Promise<void>,
  loading?: boolean
}>()
</script>

<style lang="scss" scoped>
.login-button {
  background-color: white !important;
  color: black !important;
  border-radius: 0 !important;
  padding: 12px 32px;
  font-weight: 600;
  letter-spacing: 0.5px;
  text-transform: none;
  box-shadow: none !important;
  transition: all 0.3s ease;
  border: none !important;
  margin-left: 10px;
  
  &:hover {
    background-color: #f5f5f5 !important;
    transform: translateY(-2px);
  }
  
  &::before {
    display: none;
  }

}

.loading-text, .login-text {
  color: white !important;
  font-family: 'Geist', sans-serif;
  font-weight: 500;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: flex-start;
  padding-right: 30px;
  width: 100%;
}

.loading-dots::after {
  content: '';
  animation: loadingDots 1.5s infinite;
}

@keyframes loadingDots {
  0% { content: ''; }
  25% { content: '.'; }
  50% { content: '..'; }
  75% { content: '...'; }
  100% { content: ''; }
}

.no-outline {
  outline: none !important;
  
  &::before, &::after {
    display: none !important;
  }
}
</style> 

