from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
import asyncio
from app.db.models import User, Company, JobPosting, JobApplication  # Import the model class (replace with actual path)

DATABASE_URL = "postgresql+asyncpg://junction:Artificialbois1@recruitingdb.postgres.database.azure.com:5432/recdev1"
engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

async def get_all_rows(table):
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(select(table))
            rows = result.scalars().all()
            for row in rows:
                print(row)

async def main():
    await get_all_rows(User)  # Pass the model class, not a string

if __name__ == "__main__":
    asyncio.run(main())