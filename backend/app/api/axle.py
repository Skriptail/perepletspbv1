import requests
import os
import asyncio
import aiohttp
from loguru import logger
from typing import Optional, Dict, Any, List
import datetime

# Получаем API Key из переменных окружения
AXLE_TOKEN = os.getenv("AXLE_TOKEN", "2a46a3b754f2bdfaefc85e7b157ad75e")

# ID сотрудника по умолчанию для создания клиентов
DEFAULT_CSA_ID = 1  # ID сотрудника по умолчанию для создания клиентов

# Базовый URL API
API_BASE_URL = "https://api.axle-crm.com/v1"

class AxleCRMClient:
    """
    Клиент для работы с API AxleCRM
    """
    def __init__(self, api_key: str = None):
        self.api_key = api_key or AXLE_TOKEN
        self.headers = {
            "Api-key": self.api_key,  # Ключ с маленькой буквы 'k' как в работающем curl-запросе
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        self._session = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """
        Получает или создает aiohttp сессию
        """
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session
    
    async def close(self):
        """
        Закрывает сессию
        """
        if self._session and not self._session.closed:
            await self._session.close()
    
    async def get_client(self, client_id: int) -> Optional[Dict[str, Any]]:
        """
        Получение клиента по его ID
        """
        try:
            client_url = f"{API_BASE_URL}/client/{client_id}"
            session = await self._get_session()
            
            async with session.get(client_url, headers=self.headers) as response:
                response.raise_for_status()
                return await response.json()
                
        except Exception as e:
            logger.error(f"Ошибка получения клиента из AxleCRM: {str(e)}")
            return None
    
    async def create_client(self, 
                          first_name: str,
                          last_name: str = None,
                          middle_name: str = None,
                          dob: str = None,
                          sex: str = None,
                          phone: str = None,
                          email: str = None,
                          card_number: str = None,
                          bonus_balance: int = None,
                          comment: str = None,
                          csa_id: int = None,
                          loyalty_id = None,
                          cohort_id = None,
                          subscription_sms: bool = False) -> Optional[Dict[str, Any]]:
        """
        Создание нового клиента в AxleCRM
        Обязательные поля по документации API:
        - first_name: имя клиента
        - phone: телефон клиента
        """
        try:
            client_url = f"{API_BASE_URL}/client/add"
            # Базовые данные клиента - обязательные поля
            client_data = {
                "first_name": first_name,
                "last_name": last_name or "",
                "middle_name": middle_name or "",
                "dob": dob,
                "sex": "male",
                "phone": phone,  # теперь только реальный номер
                "subscription_sms": False,
                "email": email or "none@axle-crm.com",
                "card_number": comment,
                "bonus_balance": None,
                "comment": comment,
                "loyalty_id": None,
                "cohort_id": None
            }
            
            # Добавляем необязательные поля, если они указаны
            if last_name:
                client_data["last_name"] = last_name
                
            if middle_name:
                client_data["middle_name"] = middle_name
                
            if dob:
                client_data["dob"] = dob
                
            if sex and sex in ["male", "female"]:
                client_data["sex"] = sex
                
            if email:
                client_data["email"] = email
                
            if card_number:
                client_data["card_number"] = card_number
                
            if comment:
                client_data["comment"] = comment
                
            if subscription_sms is not None:
                client_data["subscription_sms"] = subscription_sms
                
            if csa_id:
                client_data["csa_id"] = csa_id

            # Вывод полного запроса для отладки
            headers_debug = {**self.headers}
            if "Api-key" in headers_debug:
                headers_debug["Api-key"] = f"{headers_debug['Api-key'][:4]}...{headers_debug['Api-key'][-4:]}"
            logger.debug(f"URL: {client_url}")
            logger.debug(f"Заголовки: {headers_debug}")
            logger.info(f"Отправка данных в AxleCRM: {client_data}")
            
            # Отправляем запрос на создание клиента
            session = await self._get_session()
            
            async with session.post(client_url, json=client_data, headers=self.headers) as response:
                status = response.status
                logger.info(f"Получен ответ от AxleCRM API: статус {status}")
                
                # Пытаемся получить JSON, даже если статус не 200
                try:
                    result_text = await response.text()
                    logger.info(f"Текст ответа: {result_text}")
                    
                    if result_text:
                        try:
                            result = await response.json()
                            logger.info(f"JSON ответ: {result}")
                        except Exception as json_error:
                            logger.error(f"Ошибка парсинга JSON: {str(json_error)}")
                            result = {"status": "error", "text_response": result_text}
                    else:
                        result = {"status": "empty_response"}
                except Exception as text_error:
                    logger.error(f"Ошибка получения текста ответа: {str(text_error)}")
                    result = {"status": "error_reading_response"}
                
                # Проверяем статус
                response.raise_for_status()
                
            logger.info(f"Клиент успешно создан в AxleCRM: {first_name}")
            
            return result
            
        except aiohttp.ClientResponseError as e:
            logger.error(f"Ошибка HTTP при создании клиента в AxleCRM: {e.status} - {e.message}")
            return None
        except Exception as e:
            logger.error(f"Неизвестная ошибка создания клиента в AxleCRM: {str(e)}")
            logger.exception(e)  # Логируем полный стек-трейс для отладки
            return None
    
    async def update_client(self, 
                          client_id: int,
                          first_name: str = None,
                          last_name: str = None,
                          middle_name: str = None,
                          dob: str = None,
                          sex: str = None,
                          phone: str = None,
                          email: str = None,
                          card_number: str = None,
                          comment: str = None,
                          subscription_sms: bool = None) -> Optional[Dict[str, Any]]:
        """
        Обновление данных существующего клиента
        """
        try:
            client_url = f"{API_BASE_URL}/client/update"
            
            # Базовые данные для обновления
            update_data = {
                "client_id": client_id
            }
            
            # Добавляем остальные поля только если они указаны
            if first_name is not None:
                update_data["first_name"] = first_name
                
            if last_name is not None:
                update_data["last_name"] = last_name
                
            if middle_name is not None:
                update_data["middle_name"] = middle_name
                
            if dob is not None:
                update_data["dob"] = dob
                
            if sex is not None and sex in ["male", "female"]:
                update_data["sex"] = sex
                
            if phone is not None:
                update_data["phone"] = phone
                
            if email is not None:
                update_data["email"] = email
                
            if card_number is not None:
                update_data["card_number"] = card_number
                
            if comment is not None:
                update_data["comment"] = comment
                
            if subscription_sms is not None:
                update_data["subscription_sms"] = subscription_sms
            
            # Отправляем запрос на обновление клиента
            session = await self._get_session()
            
            async with session.post(client_url, json=update_data, headers=self.headers) as response:
                response.raise_for_status()
                result = await response.json()
                
            logger.info(f"Данные клиента успешно обновлены в AxleCRM: ID {client_id}")
            
            return result
            
        except Exception as e:
            logger.error(f"Ошибка обновления данных клиента в AxleCRM: {str(e)}")
            return None
    
    async def delete_client(self, client_id: int) -> bool:
        """
        Удаление клиента по его ID
        """
        try:
            client_url = f"{API_BASE_URL}/client/delete"
            session = await self._get_session()
            
            async with session.post(client_url, json={"client_id": client_id}, headers=self.headers) as response:
                response.raise_for_status()
                
            logger.info(f"Клиент с ID {client_id} успешно удален в AxleCRM")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка при удалении клиента из AxleCRM: {str(e)}")
            return False
    
    async def find_client_by_telegram_id(self, telegram_id: int) -> Optional[Dict[str, Any]]:
        """
        В API отсутствует прямой метод поиска по Telegram ID.
        Метод не реализован, т.к. API не предоставляет такой функциональности.
        Лучший вариант - сохранять соответствие Telegram ID и Client ID в своей базе данных.
        """
        logger.warning(f"API AxleCRM не поддерживает поиск по Telegram ID. Функция не реализована.")
        return None

# Создаем клиент при импорте модуля
axle_client = AxleCRMClient()

# Обработчик для завершения работы приложения
async def close_axle_client():
    await axle_client.close()

# Асинхронная функция для регистрации пользователя в AxleCRM
async def register_user_in_axle(telegram_id: int, name: str, last_name: str = None, birth_date: str = None, phone: str = None) -> Dict[str, Any]:
    """
    Регистрирует пользователя в AxleCRM.
    Возвращает данные созданного клиента или заглушку в случае ошибки.
    Args:
        telegram_id: Идентификатор пользователя в Telegram
        name: Имя пользователя (обязательно)
        last_name: Фамилия пользователя (опционально)
        birth_date: Дата рождения в формате строки ISO (опционально)
        phone: Телефон пользователя (обязательно)
    """
    try:
        # Удаляем дефолт: if not phone: phone = DEFAULT_PHONE
        logger.info(f"Регистрация в AxleCRM: telegram_id={telegram_id}, name={name}, phone={phone}")
        # Проверяем соединение
        logger.info(f"API URL: {API_BASE_URL}")
        logger.info(f"API Key (замаскирован): {axle_client.api_key[:4]}...{axle_client.api_key[-4:] if len(axle_client.api_key) > 8 else '****'}")
        # Добавляем комментарий с Telegram ID для упрощения интеграции
        comment = f"Telegram ID: {telegram_id}"
        # Создаем нового клиента с обязательными полями и всеми доступными данными
        client_data = await axle_client.create_client(
            first_name=name,
            last_name=last_name,
            middle_name=None,
            dob=birth_date,
            sex=None,
            phone=phone,     # теперь только реальный номер
            subscription_sms=False,
            email=None,
            card_number=comment,
            bonus_balance=None,
            comment=comment,
            loyalty_id=comment,
            cohort_id=None,  # По умолчанию подписываем на SMS
        )
        
        if client_data:
            # Ищем ID клиента в ответе
            client_id = client_data.get("id") or client_data.get("client_id")
            if client_id:
                logger.info(f"Клиент успешно зарегистрирован в AxleCRM: {name} (Telegram ID: {telegram_id}, AxleCRM ID: {client_id})")
                # Добавляем информацию об успехе
                client_data["success"] = True
                return client_data
            else:
                logger.warning(f"Клиент создан, но ID не получен: {name} (Telegram ID: {telegram_id})")
                return {
                    "status": "partial_success",
                    "message": "Клиент создан, но не получен ID",
                    "raw_response": client_data,
                    "success": True
                }
        else:
            logger.error(f"Ошибка регистрации клиента в AxleCRM (нет данных в ответе)")
            # Возвращаем заглушку вместо None
            return {
                "status": "error",
                "message": "Ошибка регистрации в AxleCRM",
                "success": False,
                "axle_id": None
            }
            
    except Exception as e:
        logger.error(f"Ошибка при регистрации пользователя в AxleCRM: {str(e)}")
        logger.exception(e)  # Логируем полный стек-трейс для отладки
        
        # Возвращаем заглушку вместо None
        return {
            "status": "error",
            "message": f"Внутренняя ошибка: {str(e)}",
            "success": False,
            "axle_id": None
        }
# # Добавляем функцию для создания тестового пользователя для проверки интеграции
# async def create_test_user_in_axle(test_name: str = "ТестИван") -> Dict[str, Any]:
#     """
#     Создает тестового пользователя в AxleCRM для проверки интеграции.
    
#     Args:
#         test_name (str, optional): Имя тестового пользователя. По умолчанию "ТестИван".
        
#     Returns:
#         Dict[str, Any]: Результат создания тестового пользователя или информация об ошибке.
#     """
#     try:
#         logger.info(f"Создание тестового пользователя в AxleCRM: {test_name}")
        
#         # Проверяем и выводим информацию о соединении
#         logger.info(f"API URL: {API_BASE_URL}")
#         logger.info(f"API Key (замаскирован): {axle_client.api_key[:4]}...{axle_client.api_key[-4:] if len(axle_client.api_key) > 8 else '****'}")
        
#         # Создаем тестового клиента
#         test_user_data = await axle_client.create_client(
#             first_name='name',
#             last_name='last_name',
#             middle_name=None,
#             dob=None,
#             sex=None,
#             phone='1235',     # Можно добавить email, если он доступен
#             subscription_sms=True,
#             email=None,
#             card_number=None,
#             bonus_balance=None,
#             comment=None,
#             loyalty_id=None,
#             cohort_id=None, 
#         )
        
#         if test_user_data:
#             logger.info(f"Тестовый пользователь успешно создан: {test_name}, результат: {test_user_data}")
            
#             # Добавляем информацию о том, что это тестовый пользователь
#             client_id = test_user_data.get("id") or test_user_data.get("client_id")
#             if client_id:
#                 logger.info(f"ID тестового клиента: {client_id}")
#                 test_user_data["test_created"] = True
#                 test_user_data["success"] = True
#                 return test_user_data
#             else:
#                 logger.warning(f"Не удалось получить ID тестового клиента из ответа: {test_user_data}")
#                 return {
#                     "status": "partial_success",
#                     "message": "Клиент создан, но не получен ID",
#                     "raw_response": test_user_data,
#                     "success": True
#                 }
#         else:
#             logger.error(f"Ошибка создания тестового клиента в AxleCRM (нет данных в ответе)")
#             return {
#                 "status": "error",
#                 "message": "Ошибка создания тестового клиента (нет данных в ответе)",
#                 "success": False
#             }
#     except Exception as e:
#         logger.error(f"Ошибка при создании тестового пользователя в AxleCRM: {str(e)}")
#         logger.exception(e)  # Логируем полный стек-трейс для отладки
#         return {
#             "status": "error",
#             "message": f"Внутренняя ошибка: {str(e)}",
#             "success": False
#         }

# Если файл запущен напрямую, добавляем возможность тестирования
# # Если файл запущен напрямую, выводим информационное сообщение
# if __name__ == "__main__":
#     print("Модуль axle.py содержит функции для интеграции с AxleCRM API.")
#     print("Для использования импортируйте register_user_in_axle в своем коде.")
#     print("\nДоступные функции для тестирования:")
#     print("1. create_test_user_in_axle() - создает тестового пользователя в AxleCRM")
    
#     import asyncio
    
#     async def run_test():
#         # Настраиваем вывод логов в консоль
#         logger.add(lambda msg: print(msg), level="INFO")
        
#         print("\n=== Тестирование создания тестового пользователя ===")
#         test_result = await create_test_user_in_axle("ТестПользователь")
#         print(f"Результат: {test_result}")
        
#         if test_result and test_result.get("success"):
#             print("\n✅ Тест успешно пройден!")
#         else:
#             print("\n❌ Тест не пройден!")
#     # Запускаем тест
#     asyncio.run(run_test())
    
#     print("\nПример использования:")
#     print("  from app.api.axle import register_user_in_axle")
#     print("  result = await register_user_in_axle(telegram_id=123456789, name='Иван', phone='+79991112233')")
#     print("  if result.get('success'):")
#     print("      print(f\"Клиент успешно создан с ID: {result.get('id')}\")")
#     print("  else:")
#     print("      print(f\"Ошибка: {result.get('message')}\")")
