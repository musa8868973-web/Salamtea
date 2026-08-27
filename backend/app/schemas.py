"""
Pydantic v2 Schemas — Request validation & Response serialisation
"""

from __future__ import annotations
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field, field_validator
import re


# ── Shared helpers ────────────────────────────────────────────────────────────

VALID_PACK_SIZES   = {"250g", "500g", "1kg", "2kg"}
VALID_TEA_VARIETIES = {"Black Tea", "Green Tea", "Ilaichi (Cardamom) Tea"}

# Master price map — single source of truth for pricing validation
PRICE_MAP: dict[str, dict[str, float]] = {
    "Black Tea": {
        "250g": 450.0,
        "500g": 850.0,
        "1kg":  1600.0,
        "2kg":  3100.0,
    },
    "Green Tea": {
        "250g": 500.0,
        "500g": 950.0,
        "1kg":  1800.0,
        "2kg":  3500.0,
    },
    "Ilaichi (Cardamom) Tea": {
        "250g": 550.0,
        "500g": 1050.0,
        "1kg":  2000.0,
        "2kg":  3900.0,
    },
}


# ── Order schemas ─────────────────────────────────────────────────────────────

class CartItemIn(BaseModel):
    tea_variety: str  = Field(..., description="Tea variety name")
    pack_size:   str  = Field(..., description="Pack weight e.g. 250g")
    quantity:    int  = Field(..., ge=1, le=100)

    @field_validator("tea_variety")
    @classmethod
    def validate_variety(cls, v: str) -> str:
        if v not in VALID_TEA_VARIETIES:
            raise ValueError(f"Invalid tea variety. Choose from: {VALID_TEA_VARIETIES}")
        return v

    @field_validator("pack_size")
    @classmethod
    def validate_pack(cls, v: str) -> str:
        if v not in VALID_PACK_SIZES:
            raise ValueError(f"Invalid pack size. Choose from: {VALID_PACK_SIZES}")
        return v


class CheckoutIn(BaseModel):
    customer_name:    str             = Field(..., min_length=2, max_length=120)
    customer_phone:   str             = Field(..., min_length=7, max_length=30)
    customer_email:   Optional[str]   = Field(None, max_length=120)
    delivery_address: str             = Field(..., min_length=3, max_length=500)
    notes:            Optional[str]   = Field(None, max_length=500)
    cart:             List[CartItemIn] = Field(..., min_length=1)

    @field_validator("customer_phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        digits = re.sub(r"\D", "", v)
        if len(digits) < 7:
            raise ValueError("Phone number too short.")
        return v


class OrderItemOut(BaseModel):
    tea_variety: str
    pack_size:   str
    quantity:    int
    unit_price:  float
    line_total:  float

    model_config = {"from_attributes": True}


class CheckoutOut(BaseModel):
    order_id:      str
    status:        str
    grand_total:   float
    message:       str
    created_at:    str

    model_config = {"from_attributes": True}


# ── WhatsApp link schemas ─────────────────────────────────────────────────────

class WhatsAppIn(BaseModel):
    customer_name:    str             = Field(..., min_length=2, max_length=120)
    delivery_address: str             = Field(..., min_length=5,  max_length=300)
    cart:             List[CartItemIn] = Field(..., min_length=1)


class WhatsAppOut(BaseModel):
    whatsapp_url: str
    message_text: str


# ── Contact schemas ───────────────────────────────────────────────────────────

class ContactIn(BaseModel):
    name:    str           = Field(..., min_length=2, max_length=120)
    phone:   str           = Field(..., min_length=7, max_length=30)
    email:   Optional[str] = Field(None, max_length=120)
    message: str           = Field(..., min_length=5, max_length=2000)

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        digits = re.sub(r"\D", "", v)
        if len(digits) < 7:
            raise ValueError("Phone number too short.")
        return v


class ContactOut(BaseModel):
    success: bool
    message: str
