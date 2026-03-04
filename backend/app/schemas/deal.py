"""Pydantic schemas for Deal model."""
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from ..models.deal import DealStatus


class DealCreate(BaseModel):
    """Schema for creating a new deal."""

    title: str = Field(..., min_length=1, max_length=255, description="Deal title")
    description: str | None = Field(None, max_length=5000, description="Deal description")
    image_url: str | None = Field(None, max_length=500, description="Deal image URL")
    price_cents: int = Field(..., gt=0, description="Price in cents")
    min_qty_to_close: int = Field(..., gt=0, description="Minimum quantity to close the deal")
    end_at: datetime = Field(..., description="Deal end datetime (timezone-aware)")


class DealRead(BaseModel):
    """Schema for reading a deal."""

    id: UUID = Field(..., description="Deal ID")
    title: str = Field(..., description="Deal title")
    description: str | None = Field(None, description="Deal description")
    image_url: str | None = Field(None, description="Deal image URL")
    price_cents: int = Field(..., description="Price in cents")
    min_qty_to_close: int = Field(..., description="Minimum quantity to close")
    current_qty: int = Field(..., description="Current quantity joined")
    end_at: datetime = Field(..., description="Deal end datetime")
    status: DealStatus = Field(..., description="Deal status")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = {"from_attributes": True}
