<template>
  <v-container class="fill-height pa-4">
    <v-row justify="center" align="center" class="fill-height ma-0">
      <v-col cols="12" sm="10" md="8" lg="6" class="pa-0 pa-sm-2 text-center">
        <div class="glass-card pa-8 fade-in mx-auto">
          <!-- Логотип -->
          <div class="text-center mb-8">
            <img src="@/assets/logo.svg" alt="PEREPLËT" class="logo">
            <h1 class="text-h4 gradient-text mt-6">Добро пожаловать</h1>
            <p class="text-subtitle-1 text-medium-emphasis mt-4">
              Войдите через Telegram для доступа к личному кабинету
            </p>
          </div>

          <!-- Кнопка входа -->
          <div class="text-center">
            <LoginButton :handleLogin="handleTelegramLogin" :loading="isAuthorizing" />
          </div>

          <!-- Информация об условиях использования -->
          <div class="text-center mt-6">
            <p class="text-caption terms-text">
              Нажимая кнопку «Войти через Telegram», вы соглашаетесь с 
              <a href="#" @click.prevent="showTerms = true" class="terms-link">Условиями использования</a> 
              и даете согласие на 
              <a href="#" @click.prevent="showPrivacy = true" class="terms-link">обработку персональных данных</a>
            </p>
          </div>
        </div>
      </v-col>
    </v-row>
  </v-container>

  <!-- Модальное окно с условиями использования -->
  <v-dialog v-model="showTerms" max-width="700" class="terms-dialog">
    <v-card class="terms-card pa-6">
      <v-card-title class="text-h5 pb-6">
        Условия использования сервиса
      </v-card-title>
      <v-card-text class="terms-content">
        <h3 class="text-subtitle-1 mb-2">1. Общие положения</h3>
        <p>1.1. Настоящие Условия использования сервиса PEREPLËT (далее — «Условия») определяют правила и порядок использования сервиса, а также права и обязанности Пользователей.</p>
        <p>1.2. Используя сервис PEREPLËT, Пользователь подтверждает свое согласие с настоящими Условиями.</p>
        
        <h3 class="text-subtitle-1 mb-2 mt-4">2. Использование сервиса</h3>
        <p>2.1. Сервис PEREPLËT предоставляет Пользователям возможность учёта посещений, получения и использования купонов.</p>
        <p>2.2. Пользователь обязуется использовать сервис только в соответствии с его целевым назначением.</p>
        <p>2.3. Пользователь несет ответственность за все действия, совершенные с использованием его учетной записи.</p>
        
        <h3 class="text-subtitle-1 mb-2 mt-4">3. Права и ограничения</h3>
        <p>3.1. Пользователь не имеет права воспроизводить, копировать, продавать, перепродавать или использовать в коммерческих целях любую часть сервиса без явного письменного разрешения администрации.</p>
        <p>3.2. Администрация сервиса оставляет за собой право в любое время изменять или прекращать работу сервиса без предварительного уведомления Пользователя.</p>
      </v-card-text>
      <v-card-actions class="justify-center pt-4">
        <v-btn
          color="white"
          variant="tonal"
          @click="showTerms = false"
          class="close-btn"
        >
          Закрыть
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>

  <!-- Модальное окно с политикой конфиденциальности -->
  <v-dialog v-model="showPrivacy" max-width="700" class="terms-dialog">
    <v-card class="terms-card pa-6">
      <v-card-title class="text-h5 pb-6">
        Политика обработки персональных данных
      </v-card-title>
      <v-card-text class="terms-content">
        <h3 class="text-subtitle-1 mb-2">1. Общие положения</h3>
        <p>1.1. Настоящая Политика обработки персональных данных (далее — «Политика») определяет порядок обработки и защиты информации о физических лицах, использующих сервис PEREPLËT.</p>
        <p>1.2. Целью данной Политики является обеспечение защиты прав и свобод человека и гражданина при обработке его персональных данных.</p>
        
        <h3 class="text-subtitle-1 mb-2 mt-4">2. Собираемые данные</h3>
        <p>2.1. При использовании сервиса PEREPLËT, могут быть собраны следующие персональные данные:</p>
        <ul class="pl-4 mb-2">
          <li>Идентификатор пользователя Telegram</li>
          <li>Имя и фамилия пользователя</li>
          <li>История взаимодействия с сервисом</li>
        </ul>
        
        <h3 class="text-subtitle-1 mb-2 mt-4">3. Использование данных</h3>
        <p>3.1. Персональные данные используются исключительно для:</p>
        <ul class="pl-4 mb-2">
          <li>Идентификации пользователя</li>
          <li>Предоставления сервиса и его функций</li>
          <li>Улучшения качества обслуживания</li>
        </ul>
        
        <h3 class="text-subtitle-1 mb-2 mt-4">4. Хранение и защита данных</h3>
        <p>4.1. Персональные данные хранятся в зашифрованном виде и защищены от несанкционированного доступа.</p>
        <p>4.2. Период хранения персональных данных ограничивается сроком, необходимым для достижения целей их обработки.</p>
      </v-card-text>
      <v-card-actions class="justify-center pt-4">
        <v-btn
          color="white"
          variant="tonal"
          @click="showPrivacy = false"
          class="close-btn"
        >
          Закрыть
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>

  <!-- Модальное окно регистрации для новых пользователей -->
  <v-dialog v-model="showRegisterModal" :fullscreen="smAndDown" max-width="500" persistent class="register-dialog">
    <v-card class="pa-6">
      <v-card-title class="text-h5 pb-4">
        Завершите регистрацию
      </v-card-title>
      <v-card-text>
        <v-form ref="registerForm" @submit.prevent="handleContinueRegistration">
          <v-text-field
            v-model="userName"
            label="Ваше имя"
            variant="outlined"
            :rules="[v => !!v || 'Имя обязательно для заполнения']"
            required
            class="mb-4"
          ></v-text-field>

          <!-- Поле для фамилии -->
          <v-text-field
            v-model="lastName"
            label="Ваша фамилия"
            variant="outlined"
            class="mb-4"
          ></v-text-field>

          <!-- Новый формат даты рождения: три выпадающих списка -->
          <div class="d-flex mb-4" style="gap: 8px;">
            <v-select
              v-model="birthDay"
              :items="days"
              label="День"
              variant="outlined"
              dense
              style="max-width: 80px;"
            ></v-select>
            <v-select
              v-model="birthMonth"
              :items="months"
              label="Месяц"
              variant="outlined"
              dense
              style="max-width: 110px;"
            ></v-select>
            <v-select
              v-model="birthYear"
              :items="years"
              label="Год"
              variant="outlined"
              dense
              style="max-width: 100px;"
            ></v-select>
          </div>

          <!-- Выпадающий список источника информации -->
          <v-select
            v-model="sourceOfInfo"
            :items="sourceOptions"
            label="Откуда узнали о нас?"
            variant="outlined"
            class="mb-4"
          ></v-select>

          <!-- Поле для ручного ввода телефона -->
          <v-text-field
            ref="phoneInputRef"
            v-model="manualPhone"
            label="Ваш номер телефона"
            variant="outlined"
            :rules="[
              v => {
                console.log('Validating phone:', v);
                return !!v || 'Номер телефона обязателен'
              },
              v => !v || /^9\d{9}$/.test(v) || 'Введите 10 цифр, начиная с 9'
            ]"
            required
            class="mb-4"
            type="tel"
            maxlength="10"
            placeholder="9XX XXX XX XX"
            @input="(event: Event) => console.log('Phone input:', (event.target as HTMLInputElement).value)"
          >
            <template #prepend>
              <div class="text-grey-darken-1 font-weight-medium mr-2">+7</div>
            </template>
          </v-text-field>

          <v-alert v-if="registrationError" type="error" class="mb-4">
            {{ registrationError }}
          </v-alert>

          <!-- Одна кнопка для продолжения и получения телефона -->
          <v-btn
            color="white"
            variant="tonal"
            block
            @click="handleContinueRegistration"
            :loading="isCompletingRegistration"
            class="close-btn"
          >
            Продолжить
          </v-btn>
        </v-form>
      </v-card-text>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { useRouter } from "vue-router"
import axios from "axios"
import { useWebApp } from "vue-tg"
import { useUserStore } from '@/stores/user'
import LoginButton from "@/components/LoginButton.vue"
import { onMounted, ref } from 'vue'
import { logger } from '@/utils/logger'
import { useDisplay } from 'vuetify'

const router = useRouter()
const userStore = useUserStore()
const { initDataUnsafe } = useWebApp()
const isAuthorizing = ref(false)
const showTerms = ref(false)
const showPrivacy = ref(false)

// Для модального окна регистрации
const showRegisterModal = ref(false)
const userName = ref('')
const registrationError = ref('')
const isCompletingRegistration = ref(false)
const birthDay = ref('')
const birthMonth = ref('')
const birthYear = ref('')
const sourceOfInfo = ref('')

// Добавляем ref для фамилии
const lastName = ref('')
// Добавляем ref для ручного ввода телефона
const manualPhone = ref('')

// Опции для выбора источника информации
const sourceOptions = [
  'TG',
  'Instagram',
  'VK',
  'Блогеры',
  'Сарафанка',
  'Фасадные вывески',
  'Яндекс Карты',
  '2ГИС',
  'Сайт',
  'Проходил мимо',
]

// Для новой формы даты рождения
const days = Array.from({ length: 31 }, (_, i) => String(i + 1).padStart(2, '0'))
const months = [
  '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12'
]
const years = Array.from({ length: 100 }, (_, i) => String(new Date().getFullYear() - i))

// Объявляем интерфейс для формы
interface FormType {
  validate: () => Promise<{valid: boolean}>
}

// Определяем интерфейс для пользователя Telegram
interface TelegramUser {
  id: number | string
  first_name: string
  last_name?: string
  phone_number?: string
}

// И используем его при объявлении ref
const registerForm = ref<FormType | null>(null)
const currentTelegramUser = ref<TelegramUser | null>(null)

const hasPhone = ref(false)
const isRequestingPhone = ref(false)

const isTelegramWebApp = ref(false)

const inviteQr = ref<string | null>(null)

const { smAndDown } = useDisplay()

// Инициализация Telegram Web App
onMounted(async () => {
  if ((window as any).Telegram?.WebApp) {
    const tg = (window as any).Telegram.WebApp
    tg.ready()
    isTelegramWebApp.value = true
    logger.info('Telegram WebApp инициализирован, ожидание действий пользователя')
  } else {
    logger.warn('Telegram WebApp не инициализирован')
    isTelegramWebApp.value = false
  }

  let qr = null;
  // 1. Сначала пробуем через Telegram WebApp API
  if ((window as any).Telegram?.WebApp?.initDataUnsafe?.start_param) {
    qr = (window as any).Telegram.WebApp.initDataUnsafe.start_param;
    if (qr && qr.startsWith('invite_qr_')) {
      qr = qr.replace('invite_qr_', '');
    }
  }
  // 2. Если не нашли — пробуем из URL
  if (!qr) {
    const params = new URLSearchParams(window.location.search)
    qr = params.get('invite_qr') || params.get('startapp')?.replace('invite_qr_', '')
  }
  if (qr) {
    inviteQr.value = qr
    userStore.invite_qr = qr
    logger.info('invite_qr сохранён:', qr)
  }
})

// Обработчик входа через Telegram
const handleTelegramLogin = async () => {
  if (isAuthorizing.value) return
  
  try {
    isAuthorizing.value = true
    logger.info('Начало процесса авторизации')
    
    if ((window as any).Telegram?.WebApp) {
      const tg = (window as any).Telegram.WebApp
      const user = tg.initDataUnsafe.user
      
      if (user) {
        logger.info('Данные пользователя из Telegram:', JSON.stringify(user, null, 2))
        hasPhone.value = !!user.phone_number
        
        // Сразу выполняем авторизацию без запроса имени
        await completeLogin(user)
      } else {
        logger.error('Данные пользователя не получены из Telegram')
        isAuthorizing.value = false
      }
    } else {
      logger.error('Telegram WebApp не инициализирован')
      isAuthorizing.value = false
    }
  } catch (error) {
    logger.error('Ошибка при входе через Telegram:', error)
    isAuthorizing.value = false
  }
}

// Функция завершения процесса входа
const completeLogin = async (user: TelegramUser) => {
  try {
    // Запрос на бэкенд для авторизации
    const response = await axios.post("https://e-perepletspb.ru/api/auth", {
      telegram_id: user.id,
      first_name: user.first_name,
      last_name: user.last_name || null,
      phone: user.phone_number || null,
    })

    logger.info('Ответ от сервера:', response.data)
    const userData = response.data
    
    userStore.setUserData(userData)
    logger.info('Данные сохранены в store')

    // Проверяем роль и делаем редирект
    try {
      if (userData.is_employee) {
        logger.info('Редирект на страницу сотрудника')
        await router.push('/employee')
      } else {
        logger.info('Редирект на кабинет гостя')
        await router.push('/guest/voucher')
      }
      logger.info('Путь после редиректа:', router.currentRoute.value.path)
    } catch (error) {
      logger.error('Ошибка при редиректе:', error)
      window.location.reload()
    }
  } catch (error: any) {
    logger.error('Ошибка при авторизации:', error)
    // Если пользователь не найден — открываем регистрацию
    if (error.response && error.response.status === 404) {
      currentTelegramUser.value = user
      showRegisterModal.value = true
    } else {
      alert('Ошибка авторизации. Попробуйте позже.')
    }
  } finally {
    isAuthorizing.value = false
  }
}

// Новый обработчик кнопки "Продолжить"
const handleContinueRegistration = async () => {
  if (isCompletingRegistration.value) return

  // Валидация формы
  const isValid = await registerForm.value?.validate()
  if (!isValid?.valid) {
    return
  }

  // Собираем дату рождения в формате YYYY-MM-DD
  let birthDateStr = ''
  if (birthYear.value && birthMonth.value && birthDay.value) {
    birthDateStr = `${birthYear.value}-${birthMonth.value}-${birthDay.value}`
  }

  // Запускаем регистрацию
  await completeRegistrationWithPhone(birthDateStr)
}

// Обновленная функция регистрации
const completeRegistrationWithPhone = async (birthDateStr: string) => {
  isCompletingRegistration.value = true
  registrationError.value = ''

  try {
    if (!currentTelegramUser.value) {
      throw new Error('Не удалось получить данные пользователя')
    }
    const user = currentTelegramUser.value
    // Если нет user.phone_number, используем manualPhone
    let phoneToSend = user.phone_number || manualPhone.value
    // Если пользователь вводит вручную, добавляем +7
    if (!user.phone_number && manualPhone.value) {
      phoneToSend = '+7' + manualPhone.value
    }
    if (!phoneToSend) {
      registrationError.value = 'Пожалуйста, введите номер телефона.'
      isCompletingRegistration.value = false
      return
    }
    const response = await axios.post("https://e-perepletspb.ru/api/register", {
      telegram_id: user.id,
      name: userName.value,
      last_name: lastName.value || "",
      phone: phoneToSend,
      birth_date: birthDateStr || null,
      source_of_info: sourceOfInfo.value || null,
      invite_qr: inviteQr.value || null,
    })
    logger.info('Ответ на регистрацию:', response.data)
    const userData = response.data
    userStore.setUserData(userData)
    showRegisterModal.value = false
    try {
      if (userData.is_employee) {
        await router.push('/employee')
      } else {
        await router.push('/guest/voucher')
      }
    } catch (e) {}
  } catch (error: any) {
    logger.error('Ошибка при регистрации:', error)
    registrationError.value = error?.response?.data?.detail || error.message || 'Ошибка регистрации'
  } finally {
    isCompletingRegistration.value = false
  }
}

const phoneInputRef = ref(null);
const scrollPhoneIntoView = () => {
  setTimeout(() => {
    // @ts-ignore
    (phoneInputRef.value as any)?.$el?.scrollIntoView({ behavior: 'smooth', block: 'center' });
  }, 300);
};
</script>

<style lang="scss" scoped>
@use '@/styles/main.scss' as main;
@use "sass:color";

.logo {
  width: 250px;
  height: auto;
  max-height: 250px;
  object-fit: contain;
  filter: drop-shadow(0 0 20px color.change(main.$accent-color, $alpha: 0.3));
}

.glass-card {
  max-width: 500px;
  margin: 0 auto;
}

.terms-text {
  line-height: 1.6;
  color: rgba(255, 255, 255, 0.7);
}

.terms-link {
  color: #2AABEE;
  text-decoration: none;
  transition: all 0.2s ease;
  
  &:hover {
    text-decoration: underline;
    color: #42b9f5;
  }
}

.terms-dialog {
  .terms-card {
    background: #1E1E1E;
    color: white;
  }
  
  .terms-content {
    max-height: 60vh;
    overflow-y: auto;
    color: rgba(255, 255, 255, 0.8);
    
    h3 {
      color: white;
      font-weight: 600;
    }
    
    p, li {
      margin-bottom: 8px;
      line-height: 1.6;
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

.register-dialog {
  .v-card {
    background: #1E1E1E;
    color: white;
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

@media (max-width: 600px) {
  .register-dialog .v-card {
    margin: 0 !important;
    border-radius: 0 !important;
    min-height: 100vh;
    max-height: 100vh;
    overflow-y: auto;
  }
}
</style> 