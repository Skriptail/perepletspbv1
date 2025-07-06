/**
 * main.ts
 *
 * Bootstraps Vuetify and other plugins then mounts the App`
 */

// Plugins
import { registerPlugins } from '@/plugins'

// Components
import App from './App.vue'

// Composables
import { createApp } from 'vue'

// Инициализация Telegram WebApp
if (window.Telegram && window.Telegram.WebApp) {
  // Расширяем окно на весь экран
  window.Telegram.WebApp.expand();
  
  // Устанавливаем цвет панели
  window.Telegram.WebApp.setHeaderColor('#000000');
  
  // Устанавливаем фоновый цвет
  window.Telegram.WebApp.setBackgroundColor('#000000');
}

// Fix для мобильных высот (100vh в мобильных браузерах)
const setVhVariable = () => {
  const vh = window.innerHeight * 0.01;
  document.documentElement.style.setProperty('--vh', `${vh}px`);
};

// Устанавливаем переменную при загрузке
setVhVariable();

// Обновляем при изменении размера окна
window.addEventListener('resize', setVhVariable);
window.addEventListener('orientationchange', setVhVariable);

const app = createApp(App)

registerPlugins(app)

app.mount('#app')
