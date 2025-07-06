<template>
  <div class="qr-scanner-container">
    <div id="qr-reader" class="qr-reader"></div>
    <v-btn
      v-if="message || errorMessage"
      class="reset-button mt-4 no-outline"
      @click="$emit('reset')"
    >
      <v-icon left>mdi-refresh</v-icon>
      Сбросить
    </v-btn>
  </div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue'
import { Html5QrcodeScanner } from 'html5-qrcode'

const props = defineProps<{
  onScan: (decodedText: string) => Promise<void>
  message?: string
  errorMessage?: string
}>()

defineEmits<{
  (e: 'reset'): void
}>()

let qrScanner: Html5QrcodeScanner | null = null
// Флаг блокировки для предотвращения повторного сканирования
const isProcessing = ref(false)

// Настройки сканера - скрываем лишние элементы UI
const scannerConfig = {
  fps: 10, 
  qrbox: { width: 250, height: 250 },
  aspectRatio: 1.0,
  rememberLastUsedCamera: true,
  // Скрываем лишние элементы интерфейса, оставляя только необходимое
  showTorchButtonIfSupported: false,
  showZoomSliderIfSupported: false,
  defaultZoomValueIfSupported: 2,
  // Открываем заднюю камеру по умолчанию
  videoConstraints: { facingMode: { exact: 'environment' } }
}

// Метод для перезапуска сканера, который будет вызываться внешними компонентами
const restart = async () => {
  // Очищаем существующий сканер
  if (qrScanner) {
    await qrScanner.clear()
  }
  
  // Сбрасываем блокировку
  isProcessing.value = false
  
  // Создаем новый экземпляр сканера
  qrScanner = new Html5QrcodeScanner(
    "qr-reader",
    scannerConfig,
    /* verbose= */ false
  )
  
  // Запускаем сканер
  qrScanner.render(onScanSuccess, onScanError)
}

// Экспортируем метод restart для использования в родительских компонентах
defineExpose({
  isProcessing,
  restart
})

const onScanSuccess = async (decodedText: string) => {
  // Если уже обрабатываем запрос, игнорируем новые сканирования
  if (isProcessing.value) {
    console.log("Уже обрабатывается сканирование, игнорируем")
    return
  }
  
  // Устанавливаем флаг блокировки
  isProcessing.value = true
  console.log("QR Code Scanned:", decodedText)
  
  try {
    await props.onScan(decodedText)
  } catch (error) {
    console.error("Ошибка при обработке QR-кода:", error)
  } finally {
    // Останавливаем сканер после успешного сканирования
    if (qrScanner) {
      await qrScanner.clear()
    }
  }
}

const onScanError = (error: unknown) => {
  console.error("Ошибка сканирования:", error)
}

onMounted(() => {
  // Сразу запрашиваем доступ к камере при монтировании компонента
  navigator.mediaDevices.getUserMedia({ video: true })
    .then(stream => {
      // Доступ к камере получен, освобождаем поток и запускаем сканер
      stream.getTracks().forEach(track => track.stop())
      
      qrScanner = new Html5QrcodeScanner(
        "qr-reader",
        scannerConfig,
        /* verbose= */ false
      )
      qrScanner.render(onScanSuccess, onScanError)
    })
    .catch(err => {
      console.error("Ошибка доступа к камере:", err)
      // Даже в случае ошибки, пытаемся инициализировать сканер
      // чтобы пользователь мог вручную предоставить доступ
      qrScanner = new Html5QrcodeScanner(
        "qr-reader",
        scannerConfig,
        /* verbose= */ false
      )
      qrScanner.render(onScanSuccess, onScanError)
    })
})

onUnmounted(() => {
  if (qrScanner) {
    qrScanner.clear()
  }
})
</script>

<style lang="scss" scoped>
@use '@/styles/main.scss' as main;
@use "sass:color";

.qr-scanner-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
  max-width: 400px;
  margin: 0 auto;
}

.qr-reader {
  width: 100%;
  border: none;
  background-color: #222222;
  border-radius: 0;
  overflow: hidden;
  box-shadow: none;
  
  // Скрываем лишние элементы UI библиотеки html5-qrcode
  :deep(#html5-qrcode-select-camera) {
    margin-bottom: 10px;
  }
  
  :deep(button) {
    border-radius: 0 !important;
    background-color: white !important;
    color: black !important;
    border: none !important;
    padding: 8px 16px !important;
    font-family: 'Geist', sans-serif !important;
    margin: 8px auto !important;
    display: block !important;
  }
  
  :deep(img, div[style]) {
    border-radius: 0 !important;
  }
}

.reset-button {
  background: linear-gradient(45deg, #ff595a, color.adjust(#ff595a, $lightness: 10%)) !important;
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