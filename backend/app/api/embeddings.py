import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from langchain_huggingface import HuggingFaceEmbeddings

from app.database import get_db
from app.models.incident import Incident
from app.models.incident_embedding import IncidentEmbedding
from app.api.auth import get_current_user
from app.config import settings

router = APIRouter(prefix="/api/embeddings", tags=["embeddings"])


_embedder: HuggingFaceEmbeddings | None = None


def get_embeddings_model():
    global _embedder
    if _embedder is None:
        _embedder = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )
    return _embedder


class EmbedIncidentRequest(BaseModel):
    incident_id: str


class SimilarIncidentResult(BaseModel):
    id: str
    title: str
    description: str
    severity: str
    status: str
    created_at: datetime
    similarity: float
    text_chunk: str


class SearchSimilarResponse(BaseModel):
    incidents: list[SimilarIncidentResult]


@router.post("/embed", status_code=201)
async def embed_incident(
    req: EmbedIncidentRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    incident = await db.get(Incident, uuid.UUID(req.incident_id))
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    text_chunk = (
        f"Title: {incident.title}\n"
        f"Description: {incident.description}\n"
        f"Severity: {incident.severity}\n"
        f"Status: {incident.status}\n"
        f"Service: {incident.service_name or 'N/A'}"
    )

    embedder = get_embeddings_model()
    vector = await embedder.aembed_query(text_chunk)

    embedding = IncidentEmbedding(
        incident_id=incident.id,
        embedding=vector,
        text_chunk=text_chunk,
    )
    db.add(embedding)
    await db.commit()

    return {"status": "embedded", "embedding_id": str(embedding.id)}


@router.post("/similar/{incident_id}", response_model=SearchSimilarResponse)
async def find_similar_incidents(
    incident_id: str,
    limit: int = 3,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    stmt = select(IncidentEmbedding).where(
        IncidentEmbedding.incident_id == uuid.UUID(incident_id)
    )
    result = await db.execute(stmt)
    source_embeddings = result.scalars().all()
    if not source_embeddings:
        raise HTTPException(status_code=400, detail="Incident has not been embedded yet. POST /api/embeddings/embed first.")

    query_vector = source_embeddings[0].embedding

    similar_stmt = (
        select(
            Incident,
            IncidentEmbedding,
            IncidentEmbedding.embedding.cosine_distance(query_vector).label("distance"),
        )
        .join(IncidentEmbedding, IncidentEmbedding.incident_id == Incident.id)
        .where(IncidentEmbedding.id != source_embeddings[0].id)
        .order_by(IncidentEmbedding.embedding.cosine_distance(query_vector))
        .limit(limit)
    )
    similar_result = await db.execute(similar_stmt)

    seen = set()
    results = []
    for row in similar_result:
        inc, emb, distance = row
        if inc.id in seen:
            continue
        seen.add(inc.id)
        results.append(SimilarIncidentResult(
            id=str(inc.id),
            title=inc.title,
            description=inc.description,
            severity=inc.severity,
            status=inc.status,
            created_at=inc.created_at,
            similarity=1.0 - float(distance),
            text_chunk=emb.text_chunk,
        ))

    return SearchSimilarResponse(incidents=results)
