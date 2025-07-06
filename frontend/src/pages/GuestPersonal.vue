<template>
  <v-container class="fill-height pa-0 pa-sm-4 personal-container">
    <v-row justify="center" class="fill-height ma-0">
      <v-col cols="12" md="8" lg="6" class="pa-0 pa-sm-2">
        <div class="main-content pa-2 pa-sm-4 fade-in pt-6">
          <!-- Логотип -->
          <div class="mb-4">
            <img src="@/assets/logo.svg" alt="PEREPLËT" class="logo">
          </div>
          
          <!-- Заголовок -->
          <div class="mb-6">
            <h1 class="text-h4 gradient-text mb-2">Личный кабинет</h1>
            <p class="text-h6 mt-2">{{ userStore.name }}</p>
          </div>

          <!-- Основные показатели -->
          <v-row class="mb-6">
            <v-col cols="12" md="6">
              <div class="stat-card glass-card fade-in" style="animation-delay: 0.1s">
                <div class="stat-value">{{ userStore.totalHookahCount }}</div>
                <div class="stat-label">кальянов выкурено</div>
              </div>
            </v-col>
            <v-col cols="12" md="6">
              <div class="stat-card glass-card fade-in" style="animation-delay: 0.2s">
                <div class="stat-value">{{ userStore.couponCount }}</div>
                <div class="stat-label">полученных купонов</div>
              </div>
            </v-col>
          </v-row>
          
          <!-- Блок с купонами -->
          <div class="coupon-section mb-8">
            <h2 class="text-h5 gradient-text mb-4">
              Мои купоны
            </h2>
            
            <!-- Обычные купоны -->
            <div v-if="hasRegularCoupons" class="mb-4 fade-in coupon-item">
              <div class="coupon-container">
                <div class="coupon-info">
                  <v-icon color="#FFF100" size="40" class="mr-3">mdi-ticket-confirmation</v-icon>
                  <div class="coupon-text">
                    <span class="coupon-count-inline">{{ regularCoupons.length }}</span>
                    <span class="coupon-label">купон на бесплатный кальян</span>
                  </div>
                </div>
                <v-btn
                  color="error"
                  class="activate-voucher"
                  @click.stop="showQR = true"
                >
                  <v-icon>mdi-qrcode-scan</v-icon>
                </v-btn>
              </div>
            </div>

            <!-- Приветственный купон -->
            <div v-if="welcomeCouponIndex !== -1" class="mb-4 fade-in coupon-item">
              <div class="coupon-container">
                <div class="coupon-info">
                  <v-icon color="#FFF100" size="40" class="mr-3">mdi-ticket-confirmation</v-icon>
                  <div class="coupon-text">
                    <span class="coupon-count-inline">1</span>
                    <span class="coupon-label">купон на скидку 30%</span>
                  </div>
                </div>
                <v-btn
                  color="error"
                  class="activate-voucher"
                  @click.stop="showWelcomeQR = true"
                >
                  <v-icon>mdi-qrcode-scan</v-icon>
                </v-btn>
              </div>
            </div>

            <!-- Сообщение если нет купонов -->
            <div v-else-if="welcomeCouponIndex === -1" class="mb-4 no-coupon-message">
              <div class="text-h6 text-medium-emphasis">
                У вас пока нет доступных купонов
              </div>
              <div class="text-subtitle-1 text-medium-emphasis">
                Накопите 5 кальянов для получения бесплатного!
              </div>
            </div>
          </div>
        </div>
      </v-col>
    </v-row>
  </v-container>

  <!-- Модальное окно с QR -->
  <v-dialog v-model="showQR" max-width="400" class="glass-card">
    <v-card class="glass-card">
      <v-card-title class="text-h5 gradient-text text-center pa-4">
        QR-код купона
      </v-card-title>
      <v-card-text class="text-center pa-6">
        <div v-if="currentRegularQrCode" class="qr-demo glass-card pa-6">
          <QRCode :data="currentRegularQrCode" :size="150" level="H" />
          <div class="text-subtitle-1 mt-4">Ваш QR-код</div>
          <div class="text-caption text-medium-emphasis mt-2">
            Покажите этот QR-код администратору для получения бесплатного кальяна
          </div>
          <div v-if="regularCoupons.length > 1" 
                  class="coupon-remaining mt-4">
            У вас еще {{ regularCoupons.length - 1 }} {{ getCouponWord(regularCoupons.length - 1) }}
          </div>
        </div>
        <div class="instruction mt-4">
          <v-icon color="info" class="mr-2">mdi-information-outline</v-icon>
          <span class="text-caption">После сканирования QR-кода администратором купон будет автоматически погашен.</span>
        </div>
      </v-card-text>
      <v-card-actions class="justify-center pb-4">
        <v-btn
          color="red"
          variant="elevated"
          class="close-button no-outline"
          @click="showQR = false"
        >
          Закрыть
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>

  <!-- Модалка QR для приветственного купона -->
  <v-dialog v-model="showWelcomeQR" max-width="400" class="glass-card">
    <v-card class="glass-card">
      <v-card-title class="text-h5 gradient-text text-center pa-4">
        QR-код купона на 30% скидку
      </v-card-title>
      <v-card-text class="text-center pa-6">
        <div v-if="welcomeCouponIndex !== -1" class="qr-demo glass-card pa-6">
          <QRCode :data="JSON.stringify({ telegram_id: userStore.telegram_id, code: userStore.qr_code_coupons[welcomeCouponIndex] })" :size="150" level="H" />
          <div class="text-subtitle-1 mt-4">Ваш QR-код</div>
          <div class="text-caption text-medium-emphasis mt-2">
            Покажите этот QR-код администратору для получения общей скидки 30% 
          </div>
        </div>
        <div class="instruction mt-4">
          <v-icon color="info" class="mr-2">mdi-information-outline</v-icon>
          <span class="text-caption">После сканирования QR-кода администратором купон будет автоматически погашен.</span>
        </div>
      </v-card-text>
      <v-card-actions class="justify-center pb-4">
        <v-btn
          color="red"
          variant="elevated"
          class="close-button no-outline"
          @click="showWelcomeQR = false"
        >
          Закрыть
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useUserStore } from '@/stores/user'
import QRCode from '@/components/QRCode.vue'

const showQR = ref(false)
const showWelcomeQR = ref(false)
const userStore = useUserStore()

// Индекс приветственного купона (если есть)
const welcomeCouponIndex = computed(() =>
  userStore.coupons.findIndex(c => c.startsWith('WELCOME_'))
)

// Обычные купоны (без приветственного)
const regularCoupons = computed(() =>
  userStore.coupons.filter(c => !c.startsWith('WELCOME_'))
)
const hasRegularCoupons = computed(() => regularCoupons.value.length > 0)

// QR-коды для обычных купонов (без приветственного)
const regularQrCodes = computed(() =>
  userStore.qr_code_coupons.filter((_, idx) => !userStore.coupons[idx]?.startsWith('WELCOME_'))
)
const currentRegularQrCode = computed(() => {
  if (!userStore.telegram_id || regularQrCodes.value.length === 0) return null;
  return JSON.stringify({
    telegram_id: userStore.telegram_id,
    code: regularQrCodes.value[0]
  });
});

// Функция для склонения слова "купон" в зависимости от количества
function getCouponWord(count: number): string {
  if (count === 1) return 'купон';
  if (count >= 2 && count <= 4) return 'купона';
  return 'купонов';
}
</script>

<style lang="scss" scoped>
@use '@/styles/main.scss' as main;
@use "sass:color";

.personal-container {
  /* Убеждаемся, что контейнер растягивается и корректно скроллится */
  min-height: 100%;
  overflow-y: auto;
  overflow-x: hidden; /* Предотвращаем горизонтальный скролл */
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

.coupon-section {
  margin-top: 2rem;
  width: 100%;
}

.progress-container {
  width: 100%;
  box-sizing: border-box;
  overflow: hidden;
}

.qr-demo {
  display: inline-flex;
  flex-direction: column;
  align-items: center;
  min-width: 200px;
  min-height: 200px;
  justify-content: center;
  border: 2px dashed rgba(255, 255, 255, 0.1);
  border-radius: 0;
  transition: all 0.3s ease;
  
  &:hover {
    border-color: rgba(255, 255, 255, 0.2);
  }
}

.coupon-item {
  display: flex;
  flex-wrap: nowrap;
  align-items: center;
  justify-content: flex-start;
  padding: 16px;
  background: #222222;
}

.coupon-container {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  background: #222222;
  padding: 16px 12px;
}

.coupon-info {
  display: flex;
  flex-direction: row;
  align-items: center;
  width: calc(100% - 60px);
}

.coupon-text {
  display: flex;
  align-items: center;
  flex-wrap: nowrap;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.coupon-count-inline {
  font-size: 1.2rem;
  font-weight: 700;
  color: #FFF100;
  margin-right: 6px;
  flex-shrink: 0;
}

.coupon-label {
  color: rgba(255, 255, 255, 0.9);
  font-size: 1.1rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.activate-voucher {
  min-width: unset !important;
  width: 48px !important;
  height: 48px !important;
  padding: 0 !important;
  border-radius: 0 !important;
  flex-shrink: 0;
  
  @media (max-width: 450px) {
    width: 40px !important;
    height: 40px !important;
  }
}

.no-coupon-message {
  padding: 16px;
  background: #222222;
}

@media (max-width: 450px) {
  .coupon-item {
    padding: 0;
  }
  
  .coupon-container {
    padding: 12px 8px;
  }
  
  .coupon-info .mr-3 {
    margin-right: 4px !important;
  }
  
  .coupon-text {
    flex-direction: row;
    align-items: center;
  }
  
  .coupon-count-inline {
    margin-right: 4px;
    font-size: 1.1rem;
  }
  
  .coupon-label {
    font-size: 0.8rem;
  }
  
  :deep(.v-icon) {
    font-size: 32px !important;
    width: 32px !important;
    height: 32px !important;
  }
}

@media (max-width: 600px) {
  .qr-demo {
    padding: 16px;
    min-width: unset;
    min-height: 180px;
  }
  
  .logo {
    width: 150px;
  }
  
  .stat-card {
    padding: 16px;
  }
}

:deep(.glass-card) {
  border-radius: 0 !important;
}

.coupon-remaining {
  background: linear-gradient(45deg, #e53935, #f44336);
  color: white;
  padding: 8px 16px;
  font-weight: 600;
  font-size: 0.9rem;
  border-radius: 0;
  display: inline-block;
}

.no-outline {
  border: none !important;
  outline: none !important;
  box-shadow: none !important;

  &::before {
    display: none !important;
  }
  
  &::after {
    display: none !important;
  }
}
</style>
