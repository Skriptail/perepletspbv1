from httpx import AsyncClient
from app.tg_bot.kbs import main_kb
from app.tg_bot.methods import bot_send_message


async def cmd_start(client: AsyncClient, user_info: dict):
    greeting_message = "Привет! Нажми кнопку ниже, чтобы открыть miniapp:"
    chat_id = user_info["id"]
    # Отправляем приветственное сообщение с кнопкой для miniapp
    await bot_send_message(client, chat_id, greeting_message, main_kb)
