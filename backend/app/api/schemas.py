from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from datetime import datetime

class UserPersonalResponse(BaseModel):
    name: str
    total_hookah_count: int
    coupons: List[str] = []
    qr_code_permanent: str
    qr_code_coupons: List[str] = []

class CouponResponse(BaseModel):
    coupons: List[str] = []
    qr_code_coupons: List[str] = []

class VoucherResponse(BaseModel):
    hookah_count: int  # Количество кальянов до бонусного

class VoucherItem(BaseModel):
    description: str
    required_hookahs: int

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenRequest(BaseModel):
    telegram_id: int
    init_data: str

class UserResponse(BaseModel):
    telegram_id: int
    name: str
    hookah_count: int
    total_hookah_count: int
    is_employee: bool
    token: str | None = None
    coupons: List[str] = []
    qr_code_permanent: str
    qr_code_coupons: List[str] = []
    phone: str | None = None
    source_of_info: str | None = None
    invite_qr: str | None = None
    invited_guests: int = 0
    invited_at: datetime | None = None

class UserCreateRequest(BaseModel):
    telegram_id: int
    first_name: str
    last_name: str | None = None
    phone: str | None = None
    source_of_info: str | None = None
    invite_qr: str | None = None
    invited_at: datetime | None = None

class QRCodeRequest(BaseModel):
    telegram_id: int
    qrData: str

class QRCodeScanResponse(BaseModel):
    success: bool = True
    message: str
    hookah_count: int
    total_hookah_count: int
    coupons: List[str] = []
    qr_code_coupons: List[str] = []

    class Config:
        from_attributes = True
