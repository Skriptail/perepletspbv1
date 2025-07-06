from typing import List
from pydantic_settings import BaseSettings

# env_path = os.path.join(os.path.dirname(__file__), ".env")
# print(f"Загружаем .env из {env_path}")
# load_dotenv(env_path)

class Settings(BaseSettings):
    # URL для подключения к базе данных
    DATABASE_URL: str


    TELEGRAM_BOT_TOKEN: str
    ADMIN_IDS: List[int]
    FRONT_SITE: str
    # JWT настройки
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60  
    TG_API_SITE: str
    AXLE_TOKEN: str

    class Config:
        env_file = ".env" 

    def get_webhook_url(self) -> str:
        """Возвращает URL вебхука с кодированием специальных символов."""
        return f"{self.FRONT_SITE}/webhook"

    def get_tg_api_url(self) -> str:
        """Возвращает URL вебхука с кодированием специальных символов."""
        return f"{self.TG_API_SITE}/bot{self.TELEGRAM_BOT_TOKEN}"


settings = Settings()print("Проверка TELEGRAM_BOT_TOKEN:", settings.TELEGRAM_BOT_TOKEN)
print("Проверка JWT_SECRET_KEY:", settings.JWT_SECRET_KEY)
