from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.models.engineer import Engineer
from app.models.organization import Organization
from app.schemas.auth import LoginRequest, TokenResponse

router = APIRouter(prefix="/api/auth", tags=["auth"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expire_minutes)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)


async def get_current_org(
    token: str | None = None,
    db: AsyncSession = Depends(get_db),
) -> Organization:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if token is None:
        raise credentials_exception
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        org_id: str | None = payload.get("sub")
        if org_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    result = await db.execute(select(Organization).where(Organization.id == org_id))
    org = result.scalar_one_or_none()
    if org is None:
        raise credentials_exception
    return org


async def get_current_engineer(
    token: str | None = None,
    db: AsyncSession = Depends(get_db),
) -> Engineer:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if token is None:
        raise credentials_exception
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        eng_id: str | None = payload.get("sub")
        role: str | None = payload.get("role")
        if eng_id is None or role != "engineer":
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    result = await db.execute(select(Engineer).where(Engineer.id == eng_id))
    eng = result.scalar_one_or_none()
    if eng is None:
        raise credentials_exception
    return eng


@router.post("/login", response_model=TokenResponse)
async def login(req: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Organization).where(Organization.email == req.email))
    org = result.scalar_one_or_none()
    if org and pwd_context.verify(req.password, org.password_hash):
        token = create_access_token({"sub": str(org.id), "role": "admin"})
        return TokenResponse(access_token=token, role="admin")

    result = await db.execute(select(Engineer).where(Engineer.email == req.email))
    eng = result.scalar_one_or_none()
    if eng and pwd_context.verify(req.password, eng.password_hash):
        if not eng.is_active:
            raise HTTPException(status_code=403, detail="Engineer account is deactivated")
        token = create_access_token({"sub": str(eng.id), "role": "engineer"})
        return TokenResponse(access_token=token, role="engineer")

    raise HTTPException(status_code=401, detail="Invalid email or password")
