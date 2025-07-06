<template>
  <v-container class="fill-height pa-4">
    <v-row justify="center" align="center" class="fill-height ma-0">
      <v-col cols="12" sm="10" md="8" lg="6" class="pa-0 pa-sm-2 text-center">
        <div class="glass-card pa-8 fade-in mx-auto">
          <!-- Заголовок -->
          <div class="text-center mb-8">
            <h1 class="text-h3 gradient-text mb-2">Сканер QR-кода</h1>
            <p class="text-subtitle-1 text-medium-emphasis">
              Наведите камеру на QR-код клиента
            </p>
          </div>

          <!-- Сканер QR -->
          <QRScanner
            ref="qrScanner"
            :on-scan="handleScan"
            @reset="resetScan"
          />

          <!-- Сообщения об успехе -->
          <v-alert
            v-if="scanSuccess"
            type="success"
            class="mt-4"
            variant="tonal"
          >
            <v-icon start size="24">mdi-check-circle</v-icon>
            {{ message }}
          </v-alert>

          <!-- Сообщения об ошибке -->
          <v-alert
            v-if="!scanSuccess && errorMessage"
            type="error"
            class="mt-4"
            variant="tonal"
          >
            <v-icon start size="24">mdi-alert-circle</v-icon>
            {{ errorMessage }}
          </v-alert>

          <!-- Кнопка нового сканирования -->
          <div v-if="scanSuccess || errorMessage" class="text-center mt-6">
            <v-btn
              color="primary"
              size="large"
              class="no-outline"
              @click="resetScan"
            >
              <v-icon start>mdi-qrcode-scan</v-icon>
              Новое сканирование
            </v-btn>
          </div>
        </div>
        <!-- Новый блок: постоянный QR-код для приглашения -->
        <div v-if="userStore.invite_qr" class="invite-qr mt-8">
          <h2 class="text-h5 mb-4">Ваш QR-код для приглашений</h2>
          <div class="qr-code">
            <QRCode :data="inviteLink" :size="180" level="H" />
          </div>
        </div>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'
import QRScanner from '@/components/QRScanner.vue'
import { useUserStore } from '@/stores/user'
import QRCode from '@/components/QRCode.vue'

const message = ref<string>('')
const errorMessage = ref<string>('')
const scanSuccess = ref<boolean>(false)
const qrScanner = ref<InstanceType<typeof QRScanner> | null>(null)
const userStore = useUserStore()

const inviteLink = computed(() =>
  userStore.invite_qr
    ? `https://t.me/pereplet_spb_bot/perepletspb?startapp=invite_qr_${userStore.invite_qr}`
    : ''
)

// Автоматически запрашиваем доступ к камере при открытии страницы
onMounted(() => {
  // Запрос разрешения на использование камеры при загрузке страницы
  navigator.mediaDevices.getUserMedia({ video: true })
    .then(stream => {
      // Доступ к камере получен, освобождаем поток
      stream.getTracks().forEach(track => track.stop())
      console.log('Доступ к камере получен')
    })
    .catch(error => {
      console.error('Ошибка доступа к камере:', error)
    })
})

const handleScan = async (decodedText: string) => {
  try {
    // Сбрасываем состояние
    scanSuccess.value = false
    message.value = ''
    errorMessage.value = ''
    
    // Парсим QR-код
    let qrData;
    try {
      qrData = JSON.parse(decodedText)
    } catch (parseError) {
      errorMessage.value = 'Неверный формат QR-кода'
      return
    }
    
    // Проверяем, что QR-код содержит необходимые поля
    if (!qrData.telegram_id || !qrData.code) {
      errorMessage.value = 'Некорректный QR-код'
      return
    }
    
    const response = await axios.post('/api/qr/scan', {
      telegram_id: qrData.telegram_id,
      qrData: qrData.code
    })
    
    // Проверяем статус ответа
    if (response.data.success) {
      scanSuccess.value = true
      message.value = response.data.message
    } else {
      errorMessage.value = response.data.message || 'Ошибка при сканировании'
    }
  } catch (error) {
    console.error("Ошибка при отправке QR данных:", error)
    errorMessage.value = 'Ошибка при сканировании'
  } finally {
    // Сбрасываем флаг блокировки в QRScanner через небольшую задержку
    setTimeout(() => {
      if (qrScanner.value) {
        // @ts-ignore - обращаемся к внутреннему состоянию компонента
        qrScanner.value.isProcessing.value = false
      }
    }, 1000)
  }
}

const resetScan = async () => {
  scanSuccess.value = false
  message.value = ''
  errorMessage.value = ''

  // Перезапускаем сканер с помощью метода restart
  if (qrScanner.value) {
    // Используем метод restart для полного перезапуска сканера
    await qrScanner.value.restart()
    console.log('Сканер QR-кода перезапущен')
  }
}
</script>

<style lang="scss" scoped>
@use '@/styles/main.scss' as main;
@use "sass:color";

.glass-card {
  max-width: 600px;
  margin: 0 auto;
  background: #222222;
}

.v-alert {
  border-radius: 0 !important;
  box-shadow: 0 4px 15px color.change(main.$primary-color, $alpha: 0.1);
}

.v-btn {
  background: linear-gradient(45deg, main.$primary-color, color.adjust(main.$primary-color, $lightness: 10%)) !important;
  color: white !important;
  border-radius: 0 !important;
  border: none !important;
  padding: 8px 24px;
  font-weight: 600;
  letter-spacing: 0.5px;
  text-transform: none;
  box-shadow: none !important;
  transition: all 0.3s ease;

  &:hover {
    transform: translateY(-2px);
  }

  &:active {
    transform: translateY(0);
  }
}

.no-outline {
  outline: none !important;
  
  &::before, &::after {
    display: none !important;
  }
}
</style> 