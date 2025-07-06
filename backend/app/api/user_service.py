# backend/app/services/user_service.py
import uuid
import os
import qrcode
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import Depends, HTTPException
from app.dao.user_dao import UserDAO

async def get_user_by_telegram_id(db_session: AsyncSession, telegram_id: int):
    """
    Получает пользователя по telegram_id.
    """
    dao = UserDAO(db_session)
    return await dao.get_by_telegram_id(telegram_id)

async def create_user(db_session: AsyncSession, telegram_id: int, name: str, is_employee: bool = False):
    """
    Создает нового пользователя с начальными значениями.
    """
    dao = UserDAO(db_session)
    return await dao.create_user(telegram_id, name, is_employee)

async def update_user_token(db_session: AsyncSession, user, token: str):
    """
    Обновляет токен пользователя.
    """
    dao = UserDAO(db_session)
    await dao.update_token(user, token)

async def add_hookahs(db_session: AsyncSession, user, hookahs: int):
    """
    Добавляет указанное количество кальянов:
      - Увеличивает текущее значение hookah_count
      - Увеличивает общее значение total_hookah_count
    """
    dao = UserDAO(db_session)
    await dao.add_hookahs(user, hookahs)

async def update_user_coupon(db_session: AsyncSession, user, coupon: str):
    """
    Обновляет купон пользователя.
    """
    dao = UserDAO(db_session)
    await dao.update_coupon(user, coupon)

async def generate_coupon_and_qr(db_session: AsyncSession, user):
    """
    Генерирует купон и QR-код для пользователя, если его количество кальянов >= 6.
    """
    # Если накопилось 6 кальянов, выдаем купон и генерируем QR-код
    if user.hookah_count >= 6:
        user.hookah_count = 0  # Сбрасываем счётчик до бонуса
        coupon_code = str(uuid.uuid4())[:8]  # Генерируем новый купон
        
        # Инициализируем списки купонов, если они None
        if user.coupons is None:
            user.coupons = []
        if user.qr_code_coupons is None:
            user.qr_code_coupons = []
            
        # Добавляем новый купон и QR-код
        user.coupons.append(coupon_code)
        
        # Генерация QR-кода для купона
        qr_data = f"http://127.0.0.1:8000/redeem_coupon/{coupon_code}"
        qr_code = str(uuid.uuid4())  # Уникальный идентификатор для QR-кода
        user.qr_code_coupons.append(qr_code)
        
        await db_session.commit()

        return coupon_code, qr_code

    return None, None
