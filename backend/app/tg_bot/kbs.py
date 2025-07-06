from app.config import settings

# Главная клавиатура с кнопкой меню
main_kb = {
    "keyboard": [
        [
            {
                "text": "Меню",
                "commands": ["/start"]
            }
        ],
        [
            {
                "text": "Открыть PerepletApp",
                "web_app": {"url": f"{settings.FRONT_SITE}/miniapp"}  # ссылка на ваше miniapp
            }
        ]
    ],
    "resize_keyboard": True,
    "persistent": True
}
