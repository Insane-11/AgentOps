import asyncio

from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session_factory, engine, Base
from app.models.organization import Organization
from app.models.engineer import Engineer
from app.models.service import Service

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def seed():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_factory() as db:
        result = await db.execute(select(Organization).where(Organization.email == "admin@agentops.dev"))
        existing = result.scalar_one_or_none()
        if existing:
            print("Seed data already exists, skipping.")
            return

        org = Organization(
            name="AgentOps Demo",
            email="admin@agentops.dev",
            password_hash=pwd_context.hash("admin123"),
        )
        db.add(org)
        await db.flush()

        engineers = [
            Engineer(
                organization_id=org.id,
                name="Alice Chen",
                email="alice@agentops.dev",
                password_hash=pwd_context.hash("alice123"),
                role="senior",
                is_on_call=True,
            ),
            Engineer(
                organization_id=org.id,
                name="Bob Martinez",
                email="bob@agentops.dev",
                password_hash=pwd_context.hash("bob123"),
                role="engineer",
                is_on_call=True,
            ),
            Engineer(
                organization_id=org.id,
                name="Carol Smith",
                email="carol@agentops.dev",
                password_hash=pwd_context.hash("carol123"),
                role="junior",
                is_on_call=False,
            ),
        ]
        db.add_all(engineers)
        await db.flush()

        services = [
            Service(organization_id=org.id, name="api-gateway", description="Main API gateway service"),
            Service(organization_id=org.id, name="auth-service", description="Authentication and authorization"),
            Service(organization_id=org.id, name="payment-processor", description="Payment processing pipeline"),
            Service(organization_id=org.id, name="database-primary", description="Primary PostgreSQL database"),
            Service(organization_id=org.id, name="cache-redis", description="Redis caching layer"),
        ]
        db.add_all(services)

        await db.commit()
        print("Seed data created successfully!")
        print(f"  Admin:     admin@agentops.dev / admin123")
        print(f"  Engineer:  alice@agentops.dev / alice123")
        print(f"  Engineer:  bob@agentops.dev / bob123")
        print(f"  Engineer:  carol@agentops.dev / carol123")


if __name__ == "__main__":
    asyncio.run(seed())
