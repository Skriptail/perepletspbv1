from httpx import AsyncClient
from app.config import settings


async def bot_send_message(client: AsyncClient, chat_id: int, text: str, kb: dict | None = None):
    send_data = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    if kb:
        send_data["reply_markup"] = kb
    await client.post(f"{settings.get_tg_api_url()}/sendMessage", json=send_data)