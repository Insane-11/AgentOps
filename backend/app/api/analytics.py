import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.api.auth import get_current_org
from app.analytics import get_analytics, get_accuracy_stats, get_embedding_coverage, add_feedback, get_feedback_stats
from app.models.organization import Organization
from app.models.incident import Incident

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/overview")
async def overview(
    db: AsyncSession = Depends(get_db),
    org: Organization = Depends(get_current_org),
):
    return await get_analytics(db, org.id)


@router.get("/accuracy")
async def accuracy(
    db: AsyncSession = Depends(get_db),
    org: Organization = Depends(get_current_org),
):
    return await get_accuracy_stats(db, org.id)


@router.get("/embedding-coverage")
async def embedding_coverage(
    db: AsyncSession = Depends(get_db),
    org: Organization = Depends(get_current_org),
):
    return await get_embedding_coverage(db, org.id)


class FeedbackCreate(BaseModel):
    incident_id: str
    rating: int
    comment: str = ""


@router.post("/feedback")
async def submit_feedback(
    feedback: FeedbackCreate,
    db: AsyncSession = Depends(get_db),
    org: Organization = Depends(get_current_org),
):
    incident = await db.get(Incident, uuid.UUID(feedback.incident_id))
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    result = await add_feedback(db, incident.id, org.id, feedback.rating, feedback.comment)
    return result


@router.get("/feedback-stats")
async def feedback_stats(
    db: AsyncSession = Depends(get_db),
    org: Organization = Depends(get_current_org),
):
    return await get_feedback_stats(db, org.id)
