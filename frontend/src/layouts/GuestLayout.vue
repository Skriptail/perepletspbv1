<template>
  <div class="guest-layout">
    <!-- Основной контент -->
    <div class="content-container">
      <router-view />
    </div>
    
    <!-- Фиксированная нижняя панель навигации -->
    <div class="navigation-wrapper">
      <v-bottom-navigation
        grow
        :value="activeTab"
        color="primary"
        mode="shift"
        class="bottom-nav"
      >
        <v-btn
          value="personal"
          @click="navigateTo('guest-personal')"
        >
          <v-icon>mdi-account-circle-outline</v-icon>
          Кабинет
        </v-btn>

        <v-btn
          value="voucher"
          @click="navigateTo('guest-voucher')"
        >
          <v-icon>mdi-ticket-percent-outline</v-icon>
          Ваучеры
        </v-btn>
      </v-bottom-navigation>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onBeforeUnmount } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()

const activeTab = computed(() => {
  const path = route.path
  if (path.includes('voucher')) return 'voucher'
  if (path.includes('personal')) return 'personal'
  return 'voucher'
})

const navigateTo = (name: 'guest-personal' | 'guest-voucher') => {
  router.push({ name: name as any })
}

// Устанавливаем CSS-переменную для высоты вьюпорта
const setViewportHeight = () => {
  // Устанавливаем переменную --vh, равную 1% высоты вьюпорта
  const vh = window.innerHeight * 0.01
  document.documentElement.style.setProperty('--vh', `${vh}px`)
}

onMounted(() => {
  // Вызываем один раз при монтировании
  setViewportHeight()

  // Добавляем слушатель событий для изменения размера окна и ориентации
  window.addEventListener('resize', setViewportHeight)
  window.addEventListener('orientationchange', setViewportHeight)
})

onBeforeUnmount(() => {
  // Удаляем слушатели при размонтировании, чтобы избежать утечек памяти
  window.removeEventListener('resize', setViewportHeight)
  window.removeEventListener('orientationchange', setViewportHeight)
})
</script>

<style lang="scss" scoped>
@use '@/styles/main.scss';

.guest-layout {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  min-height: calc(var(--vh, 1vh) * 100);
  position: relative;
  overflow-x: hidden;
  width: 100%;
  max-width: 100%;
  touch-action: pan-x pan-y; /* Ограничиваем типы жестов только горизонтальным и вертикальным движением */
}

.content-container {
  flex: 1;
  padding-bottom: calc(76px + env(safe-area-inset-bottom, 0px)); /* Увеличенный отступ для нижней панели */
  overflow-y: auto;
  overflow-x: hidden; /* Предотвращаем горизонтальный скролл */
  -webkit-overflow-scrolling: touch; /* Плавный скролл на iOS */
  will-change: transform; /* Оптимизация производительности */
  height: 100%;
  display: flex;
  flex-direction: column;
  width: 100%;
  max-width: 100%;
}

.navigation-wrapper {
  position: fixed;
  bottom: 17px; /* Увеличиваем отступ от низа экрана */
  left: 8px; /* Отступ слева */
  right: 8px; /* Отступ справа */
  width: calc(100% - 16px); /* Учитываем боковые отступы */
  z-index: 1000; /* Увеличиваем z-index для гарантии отображения поверх других элементов */
  pointer-events: none; /* Предотвращает перехват жестов скролла для обертки */
  margin: 0 auto; /* Центрируем по горизонтали */
  max-width: 768px; /* Ограничиваем максимальную ширину */
  transform: translateZ(0); /* Активируем аппаратное ускорение */
  touch-action: none; /* Отключаем обработку касаний для обертки */
}

.bottom-nav {
  width: 100%;
  border-top: 1px solid rgba(32, 38, 162, 0.2);
  background: rgba(15, 15, 15, 0.95) !important;
  backdrop-filter: blur(10px);
  padding-bottom: env(safe-area-inset-bottom); /* Поддержка безопасной зоны для iPhone X и новее */
  box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.2); /* Тень для визуального отделения */
  border-radius: 0 !important; /* Убираем скругление углов */
  position: relative; /* Устанавливаем позицию relative для элемента навигации */
  pointer-events: auto; /* Включаем обработку событий для навигации */
  overflow: hidden; /* Обрезаем содержимое по границам */

  :deep(.v-btn) {
    &.v-btn--active {
      color: #FC2237 !important;
    }
  }
}

/* Добавляем стили для растягивания страницы на всю высоту */
:deep(.v-container.fill-height) {
  min-height: auto !important; /* Отменяем фиксированную высоту */
  padding-bottom: 88px; /* Увеличиваем отступ для нижней панели */
  width: 100%;
  max-width: 100%;
  overflow-x: hidden;
}

/* Медиа-запрос для скрытия навигации при показе клавиатуры на мобильных устройствах */
@media (max-height: 400px) {
  .navigation-wrapper {
    display: none;
  }
}
</style>
