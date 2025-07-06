import axios from 'axios'

// Функция для отправки логов на сервер
export const logToServer = async (message: string, data?: any) => {
  try {
    const logData = {
      message,
      data,
      timestamp: new Date().toISOString(),
      userAgent: window.navigator.userAgent,
      url: window.location.href
    }
    
    await axios.post('/api/logs', logData)
  } catch (error) {
    console.error('Ошибка при отправке лога:', error)
  }
}

// Функция для логирования с отправкой на сервер
export const logger = {
  info: (message: string, data?: any) => {
    console.log(message, data)
    logToServer(message, data)
  },
  error: (message: string, error?: any) => {
    console.error(message, error)
    logToServer(message, { error: error?.message || error })
  },
  warn: (message: string, data?: any) => {
    console.warn(message, data)
    logToServer(message, data)
  }
} 