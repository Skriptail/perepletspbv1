import json
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from fastapi.staticfiles import StaticFiles
from starlette.staticfiles import StaticFiles
from app.tg_bot.router import router as router_tg_bot
from app.api.router import router as router_api
from app.async_client import http_client_manager
from app.config import settings
from app.api.axle import close_axle_client

# Настраиваем глобальное логирование
logger.add(
    "logs/app.log",
    rotation="1 day",
    retention="7 days",
    level="INFO",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
    encoding="utf-8"
)

# Добавляем вывод в консоль
logger.add(
    lambda msg: print(msg),
    level="INFO",
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> | <white>{message}</white>",
    colorize=True
)

async def set_webhook(client):
    """Устанавливает вебхук для Telegram-бота."""
    try:
        response = await client.post(f"{settings.get_tg_api_url()}/setWebhook", json={
            "url": settings.get_webhook_url()
        })
        response_data = response.json()
        if response.status_code == 200 and response_data.get("ok"):
            logger.info(f"Webhook установлен: {response_data}")
        else:
            logger.error(f"Ошибка при установке вебхука: {response_data}")
    except Exception as e:
        logger.exception(f"Не удалось установить вебхук: {e}")

async def send_admin_msg(client, text):
    for admin in settings.ADMIN_IDS:
        try:
            await client.post(f"{settings.get_tg_api_url()}/sendMessage",
                              json={"chat_id": admin, "text": text, "parse_mode": "HTML"})
        except Exception as E:
            logger.exception(f"Ошибка при отправке сообщения админу: {E}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Контекстный менеджер для настройки и завершения работы бота."""
    client = http_client_manager.get_client()
    logger.info("Настройка бота...")
    await set_webhook(client)
    await client.post(f"{settings.get_tg_api_url()}/setMyCommands",
                      data={"commands": json.dumps([{"command": "start", "description": "Главное меню"}])})
    await send_admin_msg(client, "Бот запущен!")
    yield
    logger.info("Завершение работы бота...")
    await send_admin_msg(client, "Бот остановлен!")
    await http_client_manager.close_client()
    await close_axle_client()  # Закрываем клиент AxleCRM

# STATIC = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
# app = FastAPI(openapi_url='/openapi.json', docs_url="/docs", root_path="/api", lifespan=lifespan)
app = FastAPI(lifespan=lifespan)

# app.mount("/static", StaticFiles(directory="app/static"), name="static")

origins = [
    'http://localhost:5173',
    "http://e-perepletspb.ru",  # Vue.js сервер
    "http://127.0.0.1:8000",
]

# Добавляем middleware для CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Разрешаем все источники
    allow_credentials=True,
    allow_methods=["*"],  # Разрешаем все методы
    allow_headers=["*"],  # Разрешаем все заголовки
)
print("Current working directory:", os.getcwd())
app.include_router(router_api)
app.include_router(router_tg_bot)

