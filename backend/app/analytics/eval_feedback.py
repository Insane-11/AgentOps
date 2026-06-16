"""Evaluation and feedback storage using the local database (free, no external API)."""

import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import Base, get_db


class EvalFeedback(Base):
    __tablename__ = "eval_feedback"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    incident_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("incidents.id"), nullable=False)
    organization_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


async def add_feedback(db: AsyncSession, incident_id: uuid.UUID, org_id: uuid.UUID, rating: int, comment: str = ""):
    feedback = EvalFeedback(
        incident_id=incident_id,
        organization_id=org_id,
        rating=rating,
        comment=comment,
    )
    db.add(feedback)
    await db.commit()
    return {"status": "recorded"}


async def get_feedback_stats(db: AsyncSession, org_id: uuid.UUID):
    result = await db.execute(
        select(EvalFeedback).where(EvalFeedback.organization_id == org_id)
    )
    feedbacks = result.scalars().all()

    if not feedbacks:
        return {"total": 0, "average_rating": 0, "count": 0}

    ratings = [f.rating for f in feedbacks]
    return {
        "total": len(feedbacks),
        "average_rating": round(sum(ratings) / len(ratings), 2),
        "count": len(feedbacks),
    }
