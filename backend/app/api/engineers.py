import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from passlib.context import CryptContext
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.engineer import Engineer
from app.models.organization import Organization
from app.schemas.engineer import EngineerCreate, EngineerRead, EngineerUpdate
from app.api.auth import get_current_org

router = APIRouter(prefix="/api/engineers", tags=["engineers"])

OrgDep = Annotated[Organization, Depends(get_current_org)]
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.get("", response_model=list[EngineerRead])
async def list_engineers(org: OrgDep, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Engineer).where(Engineer.organization_id == org.id).order_by(Engineer.name)
    )
    return result.scalars().all()


@router.get("/{engineer_id}", response_model=EngineerRead)
async def get_engineer(engineer_id: uuid.UUID, org: OrgDep, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Engineer).where(Engineer.id == engineer_id, Engineer.organization_id == org.id)
    )
    eng = result.scalar_one_or_none()
    if not eng:
        raise HTTPException(status_code=404, detail="Engineer not found")
    return eng


@router.post("", response_model=EngineerRead, status_code=status.HTTP_201_CREATED)
async def create_engineer(req: EngineerCreate, org: OrgDep, db: AsyncSession = Depends(get_db)):
    password_hash = pwd_context.hash(req.password)
    engineer = Engineer(
        organization_id=org.id,
        name=req.name,
        email=req.email,
        password_hash=password_hash,
        role=req.role,
        phone=req.phone,
    )
    db.add(engineer)
    await db.commit()
    await db.refresh(engineer)
    return engineer


@router.put("/{engineer_id}", response_model=EngineerRead)
async def update_engineer(engineer_id: uuid.UUID, req: EngineerUpdate, org: OrgDep, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Engineer).where(Engineer.id == engineer_id, Engineer.organization_id == org.id)
    )
    eng = result.scalar_one_or_none()
    if not eng:
        raise HTTPException(status_code=404, detail="Engineer not found")

    update_data = req.model_dump(exclude_unset=True)
    if not update_data:
        return eng

    stmt = update(Engineer).where(Engineer.id == engineer_id).values(**update_data).returning(Engineer)
    result = await db.execute(stmt)
    await db.commit()
    return result.scalar_one()
