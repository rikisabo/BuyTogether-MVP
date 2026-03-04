"""Pydantic schemas for Participant model."""
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from ..models.participant import ParticipantState


class ParticipantCreate(BaseModel):
    """Schema for creating a new participant."""

    deal_id: UUID = Field(..., description="Deal ID")
    name: str = Field(..., min_length=1, max_length=255, description="Participant name")
    email: EmailStr = Field(..., description="Participant email")
    qty: int = Field(..., gt=0, description="Quantity to purchase")


class ParticipantRead(BaseModel):
    """Schema for reading a participant."""

    id: UUID = Field(..., description="Participant ID")
    deal_id: UUID = Field(..., description="Deal ID")
    name: str = Field(..., description="Participant name")
    email: str = Field(..., description="Participant email")
    qty: int = Field(..., description="Quantity to purchase")
    tracking_id: str | None = Field(None, description="Tracking ID")
    state: ParticipantState = Field(..., description="Participant state")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = {"from_attributes": True}
