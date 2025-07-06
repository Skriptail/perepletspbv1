<template>
  <v-sheet theme="light" color="white" :rounded="false" elevation="1" class="pa-4 pt-5 pb-6 pa-sm-5 hookah-progress" style="background-color: white !important; border-radius: 0 !important;">
    <div class="hookah-icons">
      <div 
        v-for="i in 5" 
        :key="i" 
        class="hookah-item"
        :class="{ 'active': i <= currentCount }"
      >
        <div class="circle-background"></div>
        <HookahIcon
          :size="32"
          :class="{'small-icon': $vuetify.display.xs}"
          :color="i <= currentCount ? '#000000' : '#4A4A4A'"
        />
      </div>
    </div>
  </v-sheet>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useUserStore } from '@/stores/user'
import HookahIcon from './icons/HookahIcon.vue'

const userStore = useUserStore()
// Используем локальное состояние для хранения счетчика
const hookahCount = ref(userStore.hookah_count)

// Следим за изменениями в хранилище и обновляем локальное состояние
watch(() => userStore.hookah_count, (newValue) => {
  hookahCount.value = newValue
})

// Вычисляемое значение теперь использует локальный счетчик
const currentCount = computed(() => hookahCount.value)

// Метод для принудительного обновления счетчика из родительского компонента
const updateCount = (forceValue?: number) => {
  console.log('HookahProgress.updateCount(): Обновляем счетчик', {
    storeValue: userStore.hookah_count,
    currentLocalValue: hookahCount.value,
    forceValue: forceValue
  })
  
  // Если передано прямое значение, используем его
  if (forceValue !== undefined) {
    hookahCount.value = forceValue
  } else {
    // Иначе берем из хранилища
    hookahCount.value = userStore.hookah_count
  }
}

// Метод для получения текущего значения счетчика
const getCurrentCount = (): number => {
  return hookahCount.value
}

// Экспортируем методы для доступа из родительских компонентов
defineExpose({
  updateCount,
  getCurrentCount
})
</script>

<style scoped>
.hookah-progress {
  width: 100%;
  box-sizing: border-box;
  max-width: 100%;
}

.hookah-icons {
  display: flex;
  justify-content: space-between;
  width: 100%;
}

.hookah-item {
  position: relative;
  display: flex;
  justify-content: center;
  align-items: center;
  width: 55px;
  height: 55px;
}

@media (max-width: 600px) {
  .hookah-item {
    width: 45px;
    height: 45px;
  }
  
  .small-icon {
    transform: scale(0.8);
  }
}

.circle-background {
  position: absolute;
  width: 100%;
  height: 100%;
  background-color: #CCCCCC; /* Серый для неактивного состояния */
  border-radius: 50%;
  z-index: 1;
  transition: background-color 0.3s ease;
  display: flex;
  justify-content: center;
  align-items: center;
}

.hookah-item.active .circle-background {
  background-color: #FFD700; /* Жёлтый для активного состояния */
}

.hookah-item :deep(svg) {
  position: relative;
  z-index: 2;
  transform: translate(3px, 0px); /* Небольшая корректировка позиции */
}
</style> 