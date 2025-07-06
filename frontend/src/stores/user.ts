import { defineStore } from 'pinia';
import axios from 'axios';

interface User {
  telegram_id: number;
  name: string;
  is_employee: boolean;
  hookah_count: number;
  total_hookah_count: number;
  coupons?: string[];
  qr_code_permanent?: string | null;
  qr_code_coupons?: string[];
  invite_qr?: string | null;
  invited_guests?: number;
}

export const useUserStore = defineStore('user', {
  state: () => ({
    telegram_id: 0,
    name: '',
    is_employee: false,
    hookah_count: 0,
    total_hookah_count: 0,
    coupons: [] as string[],
    qr_code_permanent: null as string | null,
    qr_code_coupons: [] as string[],
    invite_qr: null as string | null,
    invited_guests: 0 as number
  }),

  actions: {
    setUserData(userData: User) {
      this.telegram_id = userData.telegram_id;
      this.name = userData.name;
      this.is_employee = userData.is_employee;
      this.hookah_count = userData.hookah_count;
      this.total_hookah_count = userData.total_hookah_count;
      this.coupons = userData.coupons || [];
      this.qr_code_permanent = userData.qr_code_permanent || null;
      this.qr_code_coupons = userData.qr_code_coupons || [];
      this.invite_qr = userData.invite_qr || null;
      this.invited_guests = userData.invited_guests || 0;
    },
    clearUserData() {
      this.telegram_id = 0;
      this.name = '';
      this.is_employee = false;
      this.hookah_count = 0;
      this.total_hookah_count = 0;
      this.coupons = [];
      this.qr_code_permanent = null;
      this.qr_code_coupons = [];
      this.invite_qr = null;
      this.invited_guests = 0;
    },
    async updateUserProgress() {
      try {
        console.log(`Запрос обновления информации для пользователя с ID ${this.telegram_id}`);
        
        // Добавляем timestamp для предотвращения кэширования
        const response = await axios.get(`/api/personal`, {
          params: { 
            telegram_id: this.telegram_id,
            _t: new Date().getTime() // Добавляем случайный параметр для предотвращения кэширования
          }
        });
        
        console.log("Полный ответ от API:", JSON.stringify(response.data, null, 2));
        
        if (response.data) {
          console.log("Текущее значение hookah_count в хранилище:", this.hookah_count);
          console.log("Полученные данные с сервера:", response.data);
          
          // Преобразуем response.data в объект, если он пришел как строка
          let data = response.data;
          if (typeof data === 'string') {
            try {
              data = JSON.parse(data);
              console.log("Преобразованные данные из строки:", data);
            } catch (e) {
              console.error("Не удалось преобразовать ответ из строки в объект:", e);
            }
          }
          
          // Принудительно отправим второй запрос для проверки актуальности данных
          console.log(`Отправляем дополнительный запрос для проверки актуальных данных`);
          const verificationResponse = await axios.get(`/api/voucher`, {
            params: { 
              telegram_id: this.telegram_id,
              _t: new Date().getTime() + 1
            }
          });
          console.log("Данные проверки (только hookah_count):", verificationResponse.data);
          
          // Используем значение hookah_count из второго запроса
          const voucherData = verificationResponse.data;
          if (voucherData && voucherData.hookah_count !== undefined) {
            console.log(`Обновляем hookah_count на основе дополнительной проверки: ${this.hookah_count} -> ${voucherData.hookah_count}`);
            this.hookah_count = voucherData.hookah_count;
          } else if (data.hookah_count !== undefined) {
            console.log(`Обновляем hookah_count из основного ответа: ${this.hookah_count} -> ${data.hookah_count}`);
            this.hookah_count = data.hookah_count;
          } else {
            console.error("ОШИБКА: hookah_count отсутствует в обоих ответах сервера");
          }
          
          // Обновляем остальные данные из основного ответа
          if (data.total_hookah_count !== undefined) {
            console.log(`Обновляем total_hookah_count: ${this.total_hookah_count} -> ${data.total_hookah_count}`);
            this.total_hookah_count = data.total_hookah_count;
          } else {
            console.error("ОШИБКА: total_hookah_count отсутствует в ответе сервера", data);
          }
          
          if (data.coupons !== undefined) {
            this.coupons = data.coupons || [];
          }
          
          if (data.qr_code_coupons !== undefined) {
            this.qr_code_coupons = data.qr_code_coupons || [];
          }
          
          console.log("Состояние хранилища после обновления:", {
            hookah_count: this.hookah_count,
            total_hookah_count: this.total_hookah_count,
            coupons: this.coupons.length,
            qr_code_coupons: this.qr_code_coupons.length
          });
        }
        
        return response.data;
      } catch (error) {
        console.error('Ошибка при обновлении прогресса:', error);
        throw error;
      }
    },
    async activateVoucher() {
      try {
        const response = await axios.post('/api/activate-coupon', {
          telegram_id: this.telegram_id
        });
        this.setUserData(response.data);
        return response.data;
      } catch (error) {
        console.error('Ошибка при активации ваучера:', error);
        throw error;
      }
    },
    async redeemCoupon() {
      try {
        const response = await axios.post('/api/coupon/redeem', {
          telegram_id: this.telegram_id
        });
        // Удаляем первый купон и QR код из списка
        if (this.coupons.length > 0) {
          this.coupons.shift();
        }
        if (this.qr_code_coupons.length > 0) {
          this.qr_code_coupons.shift();
        }
        
        return response.data;
      } catch (error) {
        console.error('Ошибка при использовании купона:', error);
        throw error;
      }
    }
  },

  getters: {
    isAuthenticated: (state) => state.telegram_id !== 0,
    isEmployee: (state) => state.is_employee,
    fullName: (state) => state.name,
    userCoupons: (state) => state.coupons || [],
    hasMultipleCoupons: (state) => (state.coupons?.length || 0) > 1,
    qrCodePermanent: (state) => {
      if (!state.telegram_id || !state.qr_code_permanent) return null;
      return JSON.stringify({
        telegram_id: state.telegram_id,
        code: state.qr_code_permanent
      });
    },
    qrCodeCoupons: (state) => {
      if (!state.telegram_id || state.qr_code_coupons.length === 0) return [];
      return state.qr_code_coupons.map(code => JSON.stringify({
        telegram_id: state.telegram_id,
        code: code
      }));
    },
    currentQrCodeCoupon: (state) => {
      if (!state.telegram_id || state.qr_code_coupons.length === 0) return null;
      return JSON.stringify({
        telegram_id: state.telegram_id,
        code: state.qr_code_coupons[0]  // Всегда используем первый (самый старый) купон
      });
    },
    hookahCount: (state) => state.hookah_count,
    totalHookahCount: (state) => state.total_hookah_count,
    couponCount: (state) => state.coupons?.length || 0,
    inviteQr: (state) => state.invite_qr
  },
}); 