from datetime import datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.incident import Incident
from app.models.incident_embedding import IncidentEmbedding


async def get_analytics(db: AsyncSession, org_id):
    total_incidents = await db.scalar(
        select(func.count(Incident.id)).where(Incident.organization_id == org_id)
    ) or 0

    resolved = await db.scalar(
        select(func.count(Incident.id)).where(
            Incident.organization_id == org_id,
            Incident.status == "RESOLVED",
        )
    ) or 0

    critical = await db.scalar(
        select(func.count(Incident.id)).where(
            Incident.organization_id == org_id,
            Incident.severity == "CRITICAL",
        )
    ) or 0

    avg_resolution_hours = await db.scalar(
        select(
            func.avg(
                func.extract("epoch", Incident.resolved_at - Incident.created_at) / 3600
            )
        ).where(
            Incident.organization_id == org_id,
            Incident.resolved_at.isnot(None),
        )
    ) or 0

    return {
        "total_incidents": total_incidents,
        "resolved_incidents": resolved,
        "critical_incidents": critical,
        "resolution_rate": round(resolved / total_incidents * 100, 1) if total_incidents else 0,
        "avg_resolution_hours": round(float(avg_resolution_hours), 1),
    }


async def get_accuracy_stats(db: AsyncSession, org_id):
    now = datetime.utcnow()
    thirty_days = now - timedelta(days=30)

    rows = (
        await db.execute(
            select(Incident.severity, func.count(Incident.id))
            .where(
                Incident.organization_id == org_id,
                Incident.created_at >= thirty_days,
            )
            .group_by(Incident.severity)
        )
    ).all()

    severity_distribution = {row[0]: row[1] for row in rows}

    agent_summaries = await db.scalar(
        select(func.count(Incident.id)).where(
            Incident.organization_id == org_id,
            Incident.agent_summary.isnot(None),
            Incident.created_at >= thirty_days,
        )
    ) or 0

    return {
        "severity_distribution": severity_distribution or {},
        "agent_analysis_count": agent_summaries,
        "period_days": 30,
    }


async def get_embedding_coverage(db: AsyncSession, org_id):
    total = await db.scalar(
        select(func.count(Incident.id)).where(Incident.organization_id == org_id)
    ) or 0

    embedded = (
        await db.execute(
            select(func.count(IncidentEmbedding.id))
            .join(Incident, Incident.id == IncidentEmbedding.incident_id)
            .where(Incident.organization_id == org_id)
        )
    ).scalar() or 0

    return {
        "total_incidents": total,
        "embedded_incidents": embedded,
        "coverage_pct": round(embedded / total * 100, 1) if total else 0,
    }
