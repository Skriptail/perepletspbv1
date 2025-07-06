<template>
  <div class="qr-code-container">
    <canvas ref="qrCanvas"></canvas>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import QRCode from 'qrcode'

const props = defineProps<{
  data: string
  size?: number
  level?: 'L' | 'M' | 'Q' | 'H'
}>()

const qrCanvas = ref<HTMLCanvasElement | null>(null)

const generateQR = async () => {
  if (!qrCanvas.value || !props.data) return

  try {
    await QRCode.toCanvas(qrCanvas.value, props.data, {
      width: props.size || 200,
      margin: 2,
      errorCorrectionLevel: props.level || 'H',
      color: {
        dark: '#000000',
        light: '#ffffff'
      }
    })
  } catch (err) {
    console.error('Ошибка при генерации QR кода:', err)
  }
}

onMounted(() => {
  generateQR()
})

watch(() => props.data, () => {
  generateQR()
})
</script>

<style scoped>
.qr-code-container {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 16px;
}
</style> 