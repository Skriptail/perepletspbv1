interface TelegramWebApp {
  expand: () => void;
  setHeaderColor: (color: string) => void;
  setBackgroundColor: (color: string) => void;
  ready: () => void;
  close: () => void;
  // Другие методы API Telegram WebApp
}

interface Telegram {
  WebApp: TelegramWebApp;
}

declare global {
  interface Window {
    Telegram?: Telegram;
  }
}

export {}; 