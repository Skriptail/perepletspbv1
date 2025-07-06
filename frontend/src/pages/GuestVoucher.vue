<template>
  <v-container class="fill-height pa-0 pa-sm-4 voucher-container">
    <v-row justify="center" class="fill-height ma-0">
      <v-col cols="12" md="8" lg="6" class="pa-0 pa-sm-2">
        <div class="main-content pa-2 pa-sm-4 fade-in pt-6">
          <!-- Логотип -->
          <div class="mb-4">
            <img src="@/assets/logo.svg" alt="PEREPLËT" class="logo">
          </div>
          
          <!-- Заголовок -->
          <div class="mb-1 d-flex justify-space-between align-center">
            <h1 class="text-h4 gradient-text">Программа лояльности</h1>
            <v-btn
              icon
              variant="text"
              color="#FFF100"
              @click="refreshProgress"
              :loading="loading"
              size="small"
              class="refresh-btn"
            >
              <v-icon>mdi-refresh</v-icon>
              <v-tooltip activator="parent" location="bottom">Обновить прогресс</v-tooltip>
            </v-btn>
          </div>

          <!-- Прогресс -->
          <div class="block-container mb-4">
            <div class="progress-container mb-3">
              <HookahProgress ref="hookahProgress" />
            </div>
            
            <!-- Информационное сообщение -->
            <div class="info-message text-center">
              <p class="text-subtitle-1 text-medium-emphasis mb-0">
                Все ваши купоны хранятся в личном кабинете
              </p>
            </div>
          </div>
          
          <!-- QR код -->
          <div class="block-container">
            <div class="qr-section fade-in">
              <div class="qr-code-container">
                <div class="qr-title text-left">Ваш QR-код</div>
                <div class="qr-description text-left">Покажите его сотруднику для зачисления кальяна</div>
                <div class="qr-code">
                  <QRCode
                    v-if="userStore.qrCodePermanent"
                    :data="userStore.qrCodePermanent"
                    :size="200"
                    level="H"
                    renderAs="svg"
                    margin="0"
                    color="#000000"
                    background="#ffffff"
                  />
                  <v-icon v-else size="100" color="grey">mdi-qrcode</v-icon>
                </div>
              </div>
            </div>
          </div>
        </div>
      </v-col>
    </v-row>
  </v-container>

  <!-- Модальное окно регистрации для новых пользователей -->
  <v-dialog v-model="showRegisterModal" max-width="500" persistent class="register-dialog">
    <v-card class="pa-6">
      <v-card-title class="text-h5 pb-4">
        Завершите регистрацию
      </v-card-title>
      <v-card-text>
        <p class="text-subtitle-1 mb-6">Пожалуйста, введите ваше имя, чтобы завершить регистрацию</p>
        
        <v-form ref="registerForm" @submit.prevent="completeRegistration">
          <v-text-field
            v-model="userName"
            label="Ваше имя"
            variant="outlined"
            :rules="[v => !!v || 'Имя обязательно для заполнения']"
            required
            class="mb-4"
          ></v-text-field>
          
          <v-alert v-if="registrationError" type="error" class="mb-4">
            {{ registrationError }}
          </v-alert>
        </v-form>
      </v-card-text>
      <v-card-actions class="pt-2">
        <v-spacer></v-spacer>
        <v-btn
          color="white"
          variant="tonal"
          @click="completeRegistration"
          :loading="isCompletingRegistration"
          class="close-btn"
        >
          Продолжить
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { useUserStore } from '@/stores/user'
import QRCode from '@/components/QRCode.vue'
import HookahProgress from '@/components/HookahProgress.vue'
import { logger } from '@/utils/logger'
import { ref, onMounted } from 'vue'
import axios from 'axios'

const userStore = useUserStore()
const loading = ref(false)
const hookahProgress = ref<InstanceType<typeof HookahProgress> | null>(null)

// Для модального окна регистрации
const showRegisterModal = ref(false)
const userName = ref('')
const registrationError = ref('')
const isCompletingRegistration = ref(false)

// Объявляем интерфейс для формы
interface FormType {
  validate: () => Promise<{valid: boolean}>
}

// И используем его при объявлении ref
const registerForm = ref<FormType | null>(null)

// Проверка имени пользователя при загрузке страницы
onMounted(async () => {
  await checkUserRegistration()
  await refreshProgress()
})

// Проверка, есть ли у пользователя имя
async function checkUserRegistration() {
  try {
    const telegramId = userStore.telegram_id
    if (!telegramId) return
    
    logger.info('Проверка регистрации пользователя:', { telegramId })
    
    // Запрос на получение данных пользователя
    const response = await axios.get(`https://e-perepletspb.ru/api/user/${telegramId}`)
    
    // Проверяем наличие имени
    if (response.data && (!response.data.name || response.data.name.trim() === '')) {
      logger.info('Имя пользователя не задано, показываем форму регистрации')
      
      showRegisterModal.value = true
    } else {
      logger.info('Пользователь уже зарегистрирован:', response.data.name)
    }
  } catch (error) {
    logger.error('Ошибка при проверке регистрации:', error)
    // Если ошибка, то лучше показать форму регистрации
    showRegisterModal.value = true
  }
}

// Завершение регистрации пользователя
async function completeRegistration() {
  if (isCompletingRegistration.value) return
  
  // Валидация формы
  const isValid = await registerForm.value?.validate()
  if (!isValid?.valid) {
    return
  }
  
  isCompletingRegistration.value = true
  registrationError.value = ''
  
  try {
    const telegramId = userStore.telegram_id
    
    if (!telegramId) {
      throw new Error('Не удалось получить ID пользователя')
    }
    
    // Запрос на регистрацию с указанным именем
    const response = await axios.post("https://e-perepletspb.ru/api/register", {
      telegram_id: telegramId,
      name: userName.value
    })
    
    logger.info('Ответ на регистрацию:', response.data)
    
    // Сохраняем данные в store
    userStore.setUserData(response.data)
    
    // Закрываем модальное окно
    showRegisterModal.value = false
    
    // Обновляем страницу для применения изменений
    window.location.reload()
    
  } catch (error) {
    logger.error('Ошибка при регистрации:', error)
    registrationError.value = 'Произошла ошибка при регистрации. Пожалуйста, попробуйте еще раз.'
  } finally {
    isCompletingRegistration.value = false
  }
}

async function refreshProgress() {
  loading.value = true
  try {
    // Логируем состояние перед обновлением
    logger.info('Состояние перед обновлением', { 
      hookahCount: userStore.hookah_count,
      totalHookahCount: userStore.total_hookah_count
    })

    // Получаем обновленную информацию о пользователе
    const responseData = await userStore.updateUserProgress()
    
    // Логируем полученный ответ от API
    logger.info('Данные, полученные от API', { responseData })
    
    // Получаем актуальный hookah_count напрямую, чтобы обойти возможные проблемы с хранилищем
    let actualHookahCount = userStore.hookah_count
    
    // Проверяем, что responseData содержит данные
    if (responseData && typeof responseData === 'object') {
      // Получаем hookah_count напрямую из ответа API для максимальной актуальности
      if ('hookah_count' in responseData && responseData.hookah_count !== undefined) {
        const apiHookahCount = responseData.hookah_count
        logger.info('Получено значение hookah_count напрямую из API', { apiHookahCount })
        actualHookahCount = apiHookahCount
      }
    }
    
    // Принудительно обновляем компонент прогресса с актуальными данными
    if (hookahProgress.value) {
      logger.info('Вызываем обновление компонента прогресса', { 
        actualHookahCount: actualHookahCount
      })
      
      // Передаем актуальное значение напрямую в компонент
      hookahProgress.value.updateCount(actualHookahCount)
      
      logger.info('Компонент прогресса обновлен')
    }
    
    logger.info('Прогресс обновлен', { 
      hookahCount: userStore.hookah_count,
      totalHookahCount: userStore.total_hookah_count,
      providedHookahCount: actualHookahCount
    })
  } catch (error) {
    logger.error('Ошибка при обновлении прогресса', { error })
  } finally {
    loading.value = false
  }
}
</script>

<style lang="scss" scoped>
@use '@/styles/main.scss' as main;
@use "sass:color";

.voucher-container {
  /* Убеждаемся, что контейнер растягивается и корректно скроллится */
  min-height: 100%;
  overflow-y: auto;
  overflow-x: hidden;
  display: flex;
  flex-direction: column;
  width: 100%;
  max-width: 100%;
}

.main-content {
  width: 100%;
  display: flex;
  flex-direction: column;
}

.logo {
  width: 200px;
  height: auto;
  max-height: 200px;
  object-fit: contain;
  filter: drop-shadow(0 0 20px color.change(main.$accent-color, $alpha: 0.3));
  display: block;
}

.block-container {
  background: #222222;
  width: 100%;
  padding: 16px;
  margin-bottom: 20px;
}

.progress-container {
  width: 100%;
  box-sizing: border-box;
  overflow: hidden;
  padding: 16px;
  border-radius: 0 !important;
}

.info-message {
  padding: 8px 16px;
  margin-top: 8px;
  width: 100%;
}

.qr-section {
  width: 100%;
  display: flex;
  justify-content: center;
  margin-top: 0;
}

.qr-code-container {
  text-align: center;
  padding: 0;
  border-radius: 0 !important;
  transition: all 0.3s ease;
  max-width: 400px;
  width: 100%;
}

.qr-title {
  font-size: 1.2rem;
  margin-bottom: 8px;
  font-weight: 500;
}

.qr-description {
  font-size: 0.9rem;
  margin-bottom: 16px;
  color: #f0f0f0;
  opacity: 0.7;
}

.qr-code {
  display: flex;
  justify-content: center;
  margin-top: 8px;
  padding: 16px;
  background: white;
  border-radius: 8px;
  width: fit-content;
  margin: 0 auto;
}

.fade-in {
  animation: fadeIn 0.6s ease-in-out;
}

.refresh-btn {
  opacity: 0.7;
  transition: all 0.3s ease;
  
  &:hover {
    opacity: 1;
    transform: rotate(180deg);
  }
}

/* Стили для модального окна регистрации */
.register-dialog {
  .v-card {
    background: #1E1E1E;
    color: white;
    border-radius: 0;
  }
  
  .v-text-field {
    input {
      color: white !important;
    }
    
    label {
      color: rgba(255, 255, 255, 0.7) !important;
    }
    
    &.v-input--is-focused {
      .v-field__outline {
        --v-field-border-opacity: 1 !important;
        --v-field-border-width: 2px !important;
      }
    }
  }
  
  .close-btn {
    background-color: white !important;
    color: black !important;
    font-weight: 500;
    min-width: 120px;
    transition: all 0.2s ease;
    box-shadow: none !important;
    
    &:hover {
      background-color: #f5f5f5 !important;
      transform: translateY(-2px);
    }
    
    &::before {
      display: none;
    }
  }
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@media (max-width: 600px) {
  .qr-code {
    padding: 12px;
  }
  
  .qr-code-container {
    padding: 16px;
  }
  
  .logo {
    width: 150px;
  }
}
</style>

