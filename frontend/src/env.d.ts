/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_URL: string
  readonly VITE_TELEGRAM_BOT_TOKEN: string
  readonly VITE_APP_TITLE: string
  readonly VITE_APP_DESCRIPTION: string
  readonly VITE_SOURCEMAP: string
  readonly VITE_OPTIMIZE: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}

interface TelegramWebApp {
  ready: () => void
  initDataUnsafe: {
    user?: {
      id: number
      first_name: string
      last_name?: string
      username?: string
      language_code?: string
      start_param?: string
    }
  }
}

interface Telegram {
  WebApp: TelegramWebApp
}

declare global {
  interface Window {
    Telegram: Telegram
  }
} 