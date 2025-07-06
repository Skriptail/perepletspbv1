from sqlalchemy.future import select
from app.dao.models import User
from app.dao.base import BaseDAO
import qrcode
import os
import uuid
from fastapi import HTTPException
import json
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func




from loguru import logger
from typing import Optional, List, Dict, Any
from datetime import datetime

class UserDAO(BaseDAO):
    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def get_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        """
        Получить пользователя по telegram_id
        """
        query = select(User).where(User.telegram_id == telegram_id)
        result = await self.session.execute(query)
        return result.scalars().first()

    async def create_user(self, telegram_id: int, name: str, last_name: str = None, birth_date: datetime = None, phone: str = None, is_employee: bool = False, source_of_info: str = None, invite_qr: str = None) -> User:
        """
        Создает нового пользователя с начальными значениями.
        """
        try:
            # Проверяем, не существует ли уже пользователь
            existing_user = await self.get_by_telegram_id(telegram_id)
            if existing_user:
                return existing_user

            # Генерируем уникальный код и QR-код
            unique_code = str(uuid.uuid4())[:8]
            permanent_qr = f"{telegram_id}_{unique_code}"
            logger.info(f"debug: create_user source_of_info={source_of_info!r}")
            invite_qr_to_save = invite_qr if is_employee else None 
            # Генерируем приветственный купон и QR-код для него
            welcome_coupon = f"WELCOME_{str(uuid.uuid4())[:8]}"
            welcome_qr = f"{telegram_id}_{welcome_coupon}"
             # Создаем нового пользователя
            new_user = User(
                telegram_id=telegram_id,
                name=name,
                last_name=last_name,
                birth_date=birth_date,
                phone=phone,
                is_employee=is_employee,
                source_of_info=source_of_info,
                hookah_count=0,
                total_hookah_count=0,
                token=None,
                coupons=[welcome_coupon],  # Приветственный купон
                qr_code_coupons=[welcome_qr],  # QR-код для приветственного купона
                qr_code_permanent=permanent_qr,
                invite_qr=invite_qr_to_save,
                invited_guests=0
            )
            
            self.session.add(new_user)
            await self.session.commit()
            await self.session.refresh(new_user)
            return new_user
            
        except Exception as e:
            await self.session.rollback()
            raise e

    async def redeem_coupon(self, user: User) -> Dict[str, Any]:
        """
        Использует (удаляет) купон пользователя.
        Реализует принцип FIFO - используется первый (самый старый) купон.
        """
        if not user.coupons or len(user.coupons) == 0:
            raise HTTPException(status_code=400, detail="У пользователя нет доступных купонов")
        
        # Получаем и удаляем первый купон из списка (FIFO)
        redeemed_coupon = user.coupons.pop(0)
        
        # Если есть соответствующий QR-код, удаляем и его
        if user.qr_code_coupons and len(user.qr_code_coupons) > 0:
            user.qr_code_coupons.pop(0)
        
        await self.session.flush()
        
        return {
            "redeemed_coupon": redeemed_coupon,
            "remaining_coupons": len(user.coupons)
        }

    async def activate_voucher(self, user: User) -> Dict[str, Any]:
        """
        Активирует ваучер для пользователя, если есть купоны.
        """
        if not user.coupons or len(user.coupons) == 0:
            raise HTTPException(status_code=400, detail="У пользователя нет доступных купонов")
            
        # Если уже есть активные QR-коды купонов, ничего не делаем
        if user.qr_code_coupons and len(user.qr_code_coupons) > 0:
            return {
                "message": "QR-код купона уже активирован",
                "coupons": user.coupons,
                "qr_code_coupons": user.qr_code_coupons,
            }
            
        # Если купоны есть, но QR-код отсутствует, генерируем новый QR-код
        if not user.qr_code_coupons:
            user.qr_code_coupons = []
            
        user.qr_code_coupons.append(str(uuid.uuid4()))
        
        await self.session.flush()
        
        return {
            "message": "QR-код купона успешно активирован",
            "coupons": user.coupons,
            "qr_code_coupons": user.qr_code_coupons,
        }

    async def update_token(self, user: User, token: str):
        """
        Обновляет поле token у пользователя.
        """
        user.token = token
        await self.commit()

    async def add_hookahs(self, user: User, hookahs: int):
        """
        Добавляет заданное количество кальянов:
          - увеличивает текущее значение hookah_count
          - увеличивает общее количество total_hookah_count
        """
        try:
            # Получаем текущие значения
            current_hookah_count = user.hookah_count
            current_total_hookah_count = user.total_hookah_count
            
            # Увеличиваем значения
            user.hookah_count = current_hookah_count + hookahs
            user.total_hookah_count = current_total_hookah_count + hookahs
            
            # Если достигнут порог (5 кальянов) – генерируем купон
            if user.hookah_count >= 5:
                # Инициализируем списки, если они None
                if user.coupons is None:
                    user.coupons = []
                if user.qr_code_coupons is None:
                    user.qr_code_coupons = []
                
                # Создаем новый купон и QR-код
                new_coupon = str(uuid.uuid4())[:8]
                new_qr_code = f"{user.telegram_id}_{new_coupon}"
                
                # Добавляем в списки
                user.coupons.append(new_coupon)
                user.qr_code_coupons.append(new_qr_code)
                
                # Сбрасываем счетчик
                user.hookah_count = 0
            
            # Сохраняем изменения
            await self.commit()
            
            # Обновляем объект из базы
            await self.session.refresh(user)
        except Exception as e:
            await self.rollback()
            raise e

    async def update_coupon(self, user: User, coupon: str):
        """
        Добавляет купон в список купонов пользователя.
        """
        try:
            # Инициализируем список купонов, если он None
            if user.coupons is None:
                user.coupons = []
            
            # Добавляем купон в список
            user.coupons.append(coupon)
            
            await self.commit()
        except Exception as e:
            await self.rollback()
            raise e

    async def generate_permanent_qr_code(self, user: User) -> str:
        """
        Генерирует постоянный QR-код для пользователя в формате {telegram_id}_{unique_code}
        """
        try:
            # Генерируем уникальный код
            unique_code = str(uuid.uuid4())[:8]
            permanent_qr = f"{user.telegram_id}_{unique_code}"

            # Обновляем запись в базе данных
            user.qr_code_permanent = permanent_qr
            await self.commit()
            
            # Обновляем объект из базы
            await self.session.refresh(user)
            
            return permanent_qr
        except Exception as e:
            await self.rollback()
            raise e

    async def generate_coupon_qr_code(self, user: User) -> str:
        """
        Генерирует QR-код купона для пользователя, если у него 5 кальянов.
        """
        if user.hookah_count < 5:
            raise HTTPException(status_code=400, detail="User does not have enough hookahs for a coupon.")

        # Инициализируем списки купонов, если они None
        if user.coupons is None:
            user.coupons = []
        if user.qr_code_coupons is None:
            user.qr_code_coupons = []
        
        # Генерация уникального кода купона
        coupon_code = str(uuid.uuid4())[:8]
        qr_code = f"{user.telegram_id}_{coupon_code}"
        
        # Добавляем в списки
        user.coupons.append(coupon_code)
        user.qr_code_coupons.append(qr_code)
        
        # Сбрасываем счетчик кальянов
        user.hookah_count = 0
        
        await self.commit()
        
        return qr_code

    async def delete_user(self, telegram_id: int) -> bool:
        """
        Удаляет пользователя по telegram_id.
        Возвращает True, если пользователь был найден и удален, False если пользователь не был найден.
        """
        user = await self.get_by_telegram_id(telegram_id)
        if not user:
            return False
            
        await self.session.delete(user)
        await self.commit()
        return True

    async def get_all_users(self) -> list[User]:
        """
        Получает список всех пользователей.
        """
        query = select(User)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def update_name(self, telegram_id: int, name: str) -> None:
        """Обновляет имя пользователя по telegram_id"""
        try:
            user = await self.get_by_telegram_id(telegram_id)
            if user:
                user.name = name
                await self.commit()
        except Exception as e:
            await self.rollback()
            raise e
            
    async def get_user_data(self, telegram_id: int) -> dict:
        """Возвращает данные пользователя в формате, подходящем для ответа API"""
        user = await self.get_by_telegram_id(telegram_id)
        if not user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
            
        # Получаем списки купонов и QR-кодов
        coupons_list = user.coupons if user.coupons is not None else []
        qr_codes_list = user.qr_code_coupons if user.qr_code_coupons is not None else []
        
        # Форматируем дату рождения в строку ISO, если она есть
        birth_date_str = user.birth_date.isoformat() if user.birth_date else None
        
        return {
            "telegram_id": user.telegram_id,
            "name": user.name,
            "last_name": user.last_name,
            "birth_date": birth_date_str,
            "phone": user.phone,
            "hookah_count": user.hookah_count,
            "total_hookah_count": user.total_hookah_count,
            "is_employee": user.is_employee,
            "coupons": coupons_list,
            "qr_code_permanent": user.qr_code_permanent,
            "qr_code_coupons": qr_codes_list,
            "source_of_info": user.source_of_info,
            "invite_qr": user.invite_qr,
            "invited_guests": user.invited_guests
        }

    async def get_by_invite_qr(self, invite_qr: str) -> Optional[User]:
        query = select(User).where(User.invite_qr == invite_qr)
        result = await self.session.execute(query)
        return result.scalars().first()
    async def update_user_info(self, telegram_id: int, name: str = None, last_name: str = None, birth_date: datetime = None, phone: str = None, source_of_info: str = None) -> None:
        """
        Обновляет данные пользователя по telegram_id
        """
        try:
            user = await self.get_by_telegram_id(telegram_id)
            if not user:
                raise HTTPException(status_code=404, detail="Пользователь не найден")
            
            # Обновляем только те поля, которые были переданы
            if name is not None:
                user.name = name
            
            if last_name is not None:
                user.last_name = last_name
            
            if birth_date is not None:
                user.birth_date = birth_date
            
            if phone is not None:
                user.phone = phone
            if source_of_info is not None:
                user.source_of_info = source_of_info
            # Сохраняем изменения
            await self.commit()
            # Обновляем объект из базы
            await self.session.refresh(user)
            return user
        except HTTPException:
            raise
        except Exception as e:
            await self.rollback()
            raise e
                

