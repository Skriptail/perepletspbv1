from loguru import logger
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession
from app.dao.session_maker_fast_api import db
from app.dao.user_dao import UserDAO
from app.api.schemas import UserPersonalResponse, UserResponse, VoucherItem, CouponResponse, VoucherResponse, UserCreateRequest, QRCodeRequest, QRCodeScanResponse
from app.api.axle import register_user_in_axle
import json
import uuid
import pydantic
from datetime import datetime
router = APIRouter(prefix="/api", tags=["api"])

class CheckUserResponse(pydantic.BaseModel):
    is_new_user: bool
    telegram_id: int = None

@router.get("/check-user")
async def check_user_exists(telegram_id: int, db_session: AsyncSession = Depends(db.get_db)):
    """Проверка существования пользователя по telegram_id"""
    user_dao = UserDAO(db_session)
    user = await user_dao.get_by_telegram_id(telegram_id)
    
    return CheckUserResponse(
        is_new_user=user is None,
        telegram_id=telegram_id
    )

@router.post("/register")
async def register_user(request: Request, db_session: AsyncSession = Depends(db.get_db_with_commit)):
    """Регистрация нового пользователя с указанным именем"""
    try:
        data = await request.json()
        telegram_id = data.get("telegram_id")
        name = data.get("name")
        last_name = data.get("last_name")
        birth_date_str = data.get("birth_date")
        phone = data.get("phone")
        source_of_info = data.get("source_of_info")
        invite_qr = data.get("invite_qr")
        logger.info(f"Получен запрос на регистрацию: telegram_id={telegram_id}, name={name}, last_name={last_name}, birth_date={birth_date_str}, phone={phone}, source_of_info={source_of_info}")
        logger.info(f'invite_qr   : {invite_qr}')
        # Преобразуем строку даты в объект datetime
        birth_date = None
        birth_date_for_axle = None
        if birth_date_str:
            try:
                birth_date = datetime.fromisoformat(birth_date_str)
                birth_date_for_axle = birth_date_str
                logger.info(f"Преобразована дата: {birth_date}")
            except ValueError as e:
                logger.error(f"Ошибка при преобразовании даты: {str(e)}")
                # В случае неверного формата, просто оставляем None
                pass
        
        if not telegram_id or not name:
            logger.error(f"Отсутствуют обязательные поля: telegram_id={telegram_id}, name={name}")
            raise HTTPException(status_code=400, detail="Необходимо указать telegram_id и имя")
        
        user_dao = UserDAO(db_session)
        
        # Проверяем, существует ли пользователь
        existing_user = await user_dao.get_by_telegram_id(telegram_id)
        if existing_user:
            logger.info(f"Пользователь с telegram_id={telegram_id} найден, обновляем данные")
            # Если пользователь уже существует, обновляем его данные
            await user_dao.update_user_info(
                telegram_id=telegram_id,
                name=name,
                last_name=last_name,
                birth_date=birth_date,
                phone=phone
            )
            user = await user_dao.get_by_telegram_id(telegram_id)
        else:
            logger.info(f"Пользователь с telegram_id={telegram_id} не найден, создаем нового")
            # Если пользователь новый, создаем его
            user = await user_dao.create_user(
                telegram_id=telegram_id,
                name=name,
                last_name=last_name,
                birth_date=birth_date,
                phone=phone,
                is_employee=False,
                source_of_info=source_of_info,
           )
        if invite_qr:
            employee = await user_dao.get_by_invite_qr(invite_qr)
            logger.info(f'   invite_qr: {employee}')
            if employee and employee.telegram_id != telegram_id:
                logger.info(f' invited_guests   {employee.telegram_id}')
                employee.invited_guests += 1
                user.invited_at = datetime.utcnow()
                logger.info(f"invited_at set to {user.invited_at}")
                await db_session.commit()

        # Генерируем QR код для пользователя, если его нет
        user_data = await user_dao.get_user_data(telegram_id)
        
        # Регистрируем пользователя в AxleCRM
        try:
            logger.info(f"Начинаем регистрацию пользователя в AxleCRM: telegram_id={telegram_id}")
            # Получаем номер телефона, если есть
            phone = data.get("phone")
            
            axle_result = await register_user_in_axle(
                telegram_id=telegram_id,
                name=name,
                last_name=last_name,
                birth_date=birth_date_for_axle,
                phone=phone
            )
            
            logger.info(f"Получен результат от AxleCRM: {axle_result}")
            
            if axle_result and axle_result.get("success") is not False:
                logger.info(f"Пользователь успешно зарегистрирован в AxleCRM: {telegram_id}, result={axle_result}")
                
                # Можно добавить сохранение ID клиента из AxleCRM в свою базу
                axle_id = axle_result.get("id") or axle_result.get("client_id")
                if axle_id:
                    logger.info(f"ID клиента в AxleCRM: {axle_id}")
                    # Здесь можно добавить код для сохранения axle_id в базе данных
            else:
                error_msg = axle_result.get("message") if axle_result else "Нет данных"
                logger.warning(f"Не удалось зарегистрировать пользователя в AxleCRM: {telegram_id}, причина: {error_msg}")
        except Exception as axle_error:
            # Если возникла ошибка при регистрации в AxleCRM, логируем её, но не прерываем основной процесс
            logger.error(f"Ошибка при регистрации в AxleCRM: {str(axle_error)}")
            logger.exception(axle_error)  # Полный стек-трейс для отладки
        
        return user_data
    except Exception as e:
        logger.error(f"Общая ошибка при регистрации: {str(e)}")
        logger.exception(e)  # Полный стек-трейс для отладки
        raise HTTPException(status_code=500, detail=f"Ошибка при регистрации: {str(e)}")

@router.post("/logs")
async def receive_logs(request: Request):
    try:
        log_data = await request.json()
        
        # Форматируем сообщение лога
        message = f"[Frontend] {log_data['message']}"
        if log_data.get('data'):
            message += f"\nData: {json.dumps(log_data['data'], ensure_ascii=False, indent=2)}"
        
        # Записываем лог
        logger.info(message)
        
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Error processing log: {str(e)}")
        return {"status": "error", "message": str(e)}

@router.post("/auth", response_model=UserResponse)
async def auth_user(user_data: UserCreateRequest, session: AsyncSession = Depends(db.get_db_with_commit)):
    """
    Эндпоинт для авторизации пользователя по Telegram.
    """
    logger.info(f"Получен запрос авторизации от пользователя {user_data.telegram_id}")
    user_dao = UserDAO(session)

    # Проверяем, есть ли пользователь
    user = await user_dao.get_by_telegram_id(user_data.telegram_id)
    logger.info(f"Результат поиска пользователя: {'найден' if user else 'не найден'}")

    if not user:
        # Если нет — создаем нового
        logger.warning(f' {user_data.telegram_id}  .  404.')
        raise HTTPException(status_code=404, detail='User not found')

    # Получаем списки купонов и QR-кодов - теперь это уже списки, а не JSON
    coupons_list = user.coupons if user.coupons is not None else []
    qr_codes_list = user.qr_code_coupons if user.qr_code_coupons is not None else []

    response_data = UserResponse(
        telegram_id=user.telegram_id,
        name=user.name,
        hookah_count=user.hookah_count,
        total_hookah_count=user.total_hookah_count,
        is_employee=user.is_employee,
        coupons=coupons_list,
        qr_code_permanent=user.qr_code_permanent,
        qr_code_coupons=qr_codes_list,
        invite_qr=user.invite_qr,
        invited_guests=user.invited_guests 
    )
    logger.info(f"Отправка ответа пользователю {user_data.telegram_id}: {response_data}")
    return response_data

@router.get("/user/{telegram_id}")
async def get_user(telegram_id: int, session: AsyncSession = Depends(db.get_db)):
    """Эндпоинт для получения пользователя по telegram_id"""
    user_dao = UserDAO(session)
    user = await user_dao.get_by_telegram_id(telegram_id)
    if not user:
        return {"error": "User not found"}
    return user

@router.post("/user")
async def create_user(telegram_id: int, name: str, session: AsyncSession = Depends(db.get_db_with_commit)):
    """Эндпоинт для создания нового пользователя"""
    user_dao = UserDAO(session)
    new_user = await user_dao.create_user(telegram_id=telegram_id, name=name)
    return {"message": "User created", "user_id": new_user.id}

@router.get("/personal", response_model=UserPersonalResponse)
async def get_personal_info(telegram_id: int, session: AsyncSession = Depends(db.get_db_with_commit)):
    """Возвращает информацию о пользователе: имя, количество кальянов, купон"""
    user_dao = UserDAO(session)
    user = await user_dao.get_by_telegram_id(telegram_id)

    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    # Получаем списки купонов и QR-кодов - теперь это уже списки, а не JSON
    coupons_list = user.coupons if user.coupons is not None else []
    qr_codes_list = user.qr_code_coupons if user.qr_code_coupons is not None else []

    return UserPersonalResponse(
        name=user.name,
        total_hookah_count=user.total_hookah_count,
        hookah_count=user.hookah_count,
        coupons=coupons_list,
        qr_code_permanent=user.qr_code_permanent,
        qr_code_coupons=qr_codes_list
    )

@router.get("/coupon", response_model=CouponResponse)
async def get_coupon(telegram_id: int, session: AsyncSession = Depends(db.get_db)):
    """Возвращает купоны пользователя, если они есть"""
    user_dao = UserDAO(session)
    user = await user_dao.get_by_telegram_id(telegram_id)

    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    # Получаем списки купонов и QR-кодов - теперь это уже списки, а не JSON
    coupons_list = user.coupons if user.coupons is not None else []
    qr_codes_list = user.qr_code_coupons if user.qr_code_coupons is not None else []

    return CouponResponse(coupons=coupons_list, qr_code_coupons=qr_codes_list)

@router.get("/voucher", response_model=VoucherResponse)
async def get_voucher(telegram_id: int, session: AsyncSession = Depends(db.get_db_with_commit)):
    """Возвращает количество кальянов до бонусного"""
    user_dao = UserDAO(session)
    user = await user_dao.get_by_telegram_id(telegram_id)

    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    return VoucherResponse(hookah_count=user.hookah_count)

@router.post("/activate-coupon")
async def activate_coupon(
    telegram_id: int,
    session: AsyncSession = Depends(db.get_db_with_commit)
):
    """Активирует ваучер при накоплении 5 кальянов"""
    user_dao = UserDAO(session)
    user = await user_dao.get_by_telegram_id(telegram_id)

    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    if user.hookah_count < 5:
        raise HTTPException(
            status_code=400,
            detail="Недостаточно кальянов для активации ваучера"
        )

    # Получаем списки купонов и QR-кодов - теперь это уже списки, а не JSON
    coupons_list = user.coupons if user.coupons is not None else []
    qr_codes_list = user.qr_code_coupons if user.qr_code_coupons is not None else []
    
    # Генерируем купон и QR-код
    new_coupon = str(uuid.uuid4())[:8]
    new_qr_code = f"{user.telegram_id}_{new_coupon}"
    
    # Добавляем в списки
    coupons_list.append(new_coupon)
    qr_codes_list.append(new_qr_code)
    
    # Обновляем поля модели - теперь напрямую присваиваем списки
    user.coupons = coupons_list
    user.qr_code_coupons = qr_codes_list
    
    # Сбрасываем счетчик
    user.hookah_count = 0
    
    await session.commit()
    
    return {
        "telegram_id": user.telegram_id,
        "name": user.name,
        "is_employee": user.is_employee,
        "hookah_count": user.hookah_count,
        "total_hookah_count": user.total_hookah_count,
        "coupons": coupons_list,
        "qr_code_permanent": user.qr_code_permanent,
        "qr_code_coupons": qr_codes_list
    }

@router.post("/coupon/redeem")
async def redeem_coupon(telegram_id: int, session: AsyncSession = Depends(db.get_db_with_commit)):
    """Погашает купон пользователя по принципу FIFO (первым погашается самый старый купон)"""
    user_dao = UserDAO(session)
    user = await user_dao.get_by_telegram_id(telegram_id)

    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    # Получаем списки купонов и QR-кодов - теперь это уже списки, а не JSON
    coupons_list = user.coupons if user.coupons is not None else []
    qr_codes_list = user.qr_code_coupons if user.qr_code_coupons is not None else []
    
    if not coupons_list:
        raise HTTPException(status_code=400, detail="У пользователя нет активных купонов")

    # Удаляем первый (самый старый) купон по принципу FIFO
    redeemed_coupon = coupons_list.pop(0)
    redeemed_qr = qr_codes_list.pop(0) if qr_codes_list else None
    
    # Обновляем списки в модели - теперь напрямую присваиваем списки
    user.coupons = coupons_list
    user.qr_code_coupons = qr_codes_list
    
    await session.commit()
    
    return {
        "message": "Купон успешно погашен",
        "redeemed_coupon": redeemed_coupon,
        "remaining_coupons": len(coupons_list)
    }

@router.post("/qr/scan", response_model=QRCodeScanResponse)
async def process_qr_code(
    qr_request: QRCodeRequest,
    session: AsyncSession = Depends(db.get_db_with_commit)
):
    """
    Эндпоинт для обработки сканированного QR-кода пользователя.
    Если отсканированный код совпадает  qr_code_permanent, увеличивает hookah_count и total_hookah_count.
    Если отсканированный код совпадает  одним из qr_code_coupons, погашает купон.
    Если hookah_count достигает 5, генерирует новый купон и сбрасывает hookah_count.
    """
    user_dao = UserDAO(session)
    user = await user_dao.get_by_telegram_id(qr_request.telegram_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    # Перед любыми операциями с объектом сначала получим все нужные значения
    # и сохраним их в локальные переменные
    current_hookah_count = user.hookah_count
    current_total_hookah_count = user.total_hookah_count
    permanent_qr = user.qr_code_permanent
    
    # Получаем список купонов и QR-кодов (теперь это уже списки, а не JSON)
    coupons_list = user.coupons if user.coupons is not None else []
    qr_codes_list = user.qr_code_coupons if user.qr_code_coupons is not None else []

    # Проверяем, совпадает ли отсканированный QR-код с постоянным QR-кодом пользователя
    if qr_request.qrData == permanent_qr:
        # Постоянный QR-код - увеличиваем счетчик кальянов
        user.total_hookah_count = current_total_hookah_count + 1
        new_hookah_count = current_hookah_count + 1

        # Если достигнут порог (например, 5 кальянов) – генерируем купон и сбрасываем hookah_count
        if new_hookah_count >= 5:
            # Генерируем новый купон
            new_coupon = str(uuid.uuid4())[:8]
            new_qr_code = f"{user.telegram_id}_{new_coupon}"
            
            # Добавляем в списки
            coupons_list.append(new_coupon)
            qr_codes_list.append(new_qr_code)
            
            # Обновляем поля модели - теперь напрямую присваиваем списки
            user.coupons = coupons_list
            user.qr_code_coupons = qr_codes_list
            
            # Сбрасываем счетчик
            user.hookah_count = 0
            
            logger.info(f"Автоматически сгенерирован купон для пользователя {user.telegram_id}: {new_coupon}")
        else:
             user.hookah_count = new_hookah_count
        # Сначала применяем изменения
        await session.commit()
        
        # После коммита обновляем объект из базы для получения актуальных значений
        await session.refresh(user)
        
        # Получаем обновленные списки
        coupons_list = user.coupons if user.coupons is not None else []
        qr_codes_list = user.qr_code_coupons if user.qr_code_coupons is not None else []

        return QRCodeScanResponse(
            success=True,
            message="QR-код успешно обработан, кальян засчитан!",
            hookah_count=user.hookah_count,
            total_hookah_count=user.total_hookah_count,
            coupons=coupons_list,
            qr_code_coupons=qr_codes_list
        )
    # Проверяем, есть ли отсканированный QR-код в списке QR-кодов купонов
    elif qr_request.qrData in qr_codes_list and len(coupons_list) > 0:
        # Получаем индекс купона
        qr_index = qr_codes_list.index(qr_request.qrData)
        
        # Получаем купон для погашения
        redeemed_coupon = coupons_list.pop(qr_index) if qr_index < len(coupons_list) else None
        # Удаляем QR-код купона
        qr_codes_list.pop(qr_index)
        # Обновляем списки в модели
        user.coupons = coupons_list
        user.qr_code_coupons = qr_codes_list
        await session.commit()
        await session.refresh(user)
        # Проверяем, является ли купон приветственным
        if redeemed_coupon and redeemed_coupon.startswith("WELCOME_"):
            # Увеличиваем total_hookah_count при использовании welcome-купона
            user.total_hookah_count += 1
            await session.commit()
            await session.refresh(user)
            
            return QRCodeScanResponse(
                success=True,
                message="Приветственный купон на скидку 30% успешно погашен!",
                hookah_count=user.hookah_count,
                total_hookah_count=user.total_hookah_count,
                coupons=user.coupons if user.coupons is not None else [],
                qr_code_coupons=user.qr_code_coupons if user.qr_code_coupons is not None else []
            )
        else:
            return QRCodeScanResponse(
                success=True,
                message="Купон успешно погашен!",
                hookah_count=user.hookah_count,
                total_hookah_count=user.total_hookah_count,
                coupons=user.coupons if user.coupons is not None else [],
                qr_code_coupons=user.qr_code_coupons if user.qr_code_coupons is not None else []
            )
    else:
        return QRCodeScanResponse(
            success=False,
            message="Неверный QR-код",
            hookah_count=current_hookah_count,
            total_hookah_count=current_total_hookah_count,
            coupons=coupons_list,
            qr_code_coupons=qr_codes_list
        )

@router.delete("/user/{telegram_id}")
async def delete_user(
    telegram_id: int,
    session: AsyncSession = Depends(db.get_db_with_commit)
):
    """
    Удаляет пользователя по telegram_id.
    Возвращает сообщение об успешном удалении или ошибку, если пользователь не найден.
    """
    user_dao = UserDAO(session)
    deleted = await user_dao.delete_user(telegram_id)
    
    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Пользователь не найден"
        )
        
    return {"message": "Пользователь успешно удален"}

@router.get("/user/employee-status")
async def get_employee_status(telegram_id: int, session: AsyncSession = Depends(db.get_db)):
    """Возвращает статус сотрудника пользователя"""
    user_dao = UserDAO(session)
    user = await user_dao.get_by_telegram_id(telegram_id)

    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    user.is_employee = True
    await session.commit()

    return {"user": {"telegram_id": user.telegram_id, "is_employee": user.is_employee}}

@router.get("/users")
async def get_all_users(session: AsyncSession = Depends(db.get_db)):
    """
    Возвращает список всех пользователей с их telegram_id.
    """
    user_dao = UserDAO(session)
    users = await user_dao.get_all_users()
    
    return {
        "users": [
            {
                "telegram_id": user.telegram_id,
                "name": user.name,
                "is_employee": user.is_employee
            }
            for user in users
        ]
    }

@router.post("/user/make_employee")
async def make_employee(telegram_id: int, session: AsyncSession = Depends(db.get_db_with_commit)):
    user_dao = UserDAO(session)
    user = await user_dao.get_by_telegram_id(telegram_id)
    if not user:
        raise HTTPException(status_code=404, detail="polzovatel ne naiden")  
    
    if not user.is_employee:
        user.is_employee = True
        if not user.invite_qr:
            user.invite_qr = str(uuid.uuid4())
        await session.commit()
        invite_link = f"https://t.me/pereplet_spb_bot/perepletspb?startapp=invite_qr_{user.invite_qr}"
        return {"user": {"telegram_id": user.telegram_id, "is_employee": user.is_employee, "invite_qr": user.invite_qr, "invite_link": invite_link}}
    else:
        if user.invite_qr:
            invite_link = f'https://t.me/pereplet_spb_bot/perepletspb?startapp=invite_qr_{user.invite_qr}'
        else:
            invite_link = None
        return {"message": "уже сотрудник", "invite_qr": user.invite_qr, "invite_link": invite_link}
