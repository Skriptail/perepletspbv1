from app.tg_bot.handlers import cmd_start
from fastapi import APIRouter, Request
from httpx import AsyncClient
from app.config import settings
from loguru import logger

router = APIRouter()

@router.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    logger.info(f"Получен запрос от Telegram: {data}")
    client = AsyncClient()

    if "message" in data and "text" in data["message"]:
        if data["message"]["text"] == "/start":
            await cmd_start(client=client, user_info=data["message"]["from"])

    return {"ok": True}
