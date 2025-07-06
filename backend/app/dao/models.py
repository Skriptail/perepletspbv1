# backend/app/models/user.py
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, BigInteger, JSON, ForeignKey
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.dao.database import Base   # Убедитесь, что Base создан через declarative_base()
import json

class User(Base):
    __tablename__ = "users"
    __table_args__ = {"schema": "public"}

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False)
    name = Column(String, nullable=False)
    last_name = Column(String, nullable=True)  # Фамилия
    birth_date = Column(DateTime, nullable=True)  # Дата рождения
    is_employee = Column(Boolean, default=False)
    hookah_count = Column(Integer, default=0)
    total_hookah_count = Column(Integer, default=0)
    token = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    source_of_info = Column(String, nullable=True)
    # Новые поля для хранения списков
    coupons = Column(MutableList.as_mutable(ARRAY(String)), nullable=True)  # Список купонов
    qr_code_coupons = Column(MutableList.as_mutable(ARRAY(String)), nullable=True)  # Список QR кодов купонов
    qr_code_permanent = Column(String, nullable=True)  # Постоянный QR для подсчета кальянов
    invite_qr = Column(String, unique=True, nullable=True, index=True)
    invited_guests = Column(Integer, default=0)
    invited_at = Column(DateTime, nullable=True)
    scan_history = Column(ARRAY(DateTime), nullable=True)
