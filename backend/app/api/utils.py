from datetime import datetime
import pytz
from app.tg_bot.scheduler_task import schedule_appointment_notification

MOSCOW_TZ = pytz.timezone("Europe/Moscow")


async def add_notification(user_tg_id, appointment, notification_time, reminder_label, notification_times):
    """
    Универсальная функция для добавления напоминания и обновления списка временных точек.
    """
    if notification_time > datetime.now(MOSCOW_TZ):
        await schedule_appointment_notification(
            user_tg_id=user_tg_id,
            appointment=appointment,
            notification_time=notification_time,
            reminder_label=reminder_label
        )
        notification_times.append(notification_time)
