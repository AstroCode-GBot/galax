from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.config import settings

# Adjust driver variant for clean async execution mapping
db_url = settings.DATABASE_URL.replace("mysql+pymysql://", "mysql+aiomysql://")

engine = create_async_engine(
    db_url,
    pool_size=20,
    max_overflow=10,
    pool_recycle=3600,
    echo=False
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session