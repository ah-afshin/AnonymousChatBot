from sqlalchemy import (
    String,
    BigInteger,
    Column,
    select,
    # ForeignKey,
    Result
)
from sqlalchemy.orm import (
    sessionmaker,
    # relationship,
    DeclarativeMeta,
    declarative_base
)
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    AsyncEngine,
    create_async_engine
)
from config import DATABASE_URI
import uuid
import typing as t


Base: t.Type[DeclarativeMeta] = declarative_base()
engine: AsyncEngine = create_async_engine(f"sqlite+aiosqlite:///{DATABASE_URI}", echo=True)
SessionLocal: sessionmaker[AsyncSession] = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


def generate_anon_id() -> str:
    """generate anonymous ID for users"""
    return str(uuid.uuid4())[:8]


class User(Base):
    __tablename__: str = "users"
    anon_id: Column[String] = Column("anonID", String(8), primary_key=True, default=generate_anon_id)
    bale_id: Column[String] = Column("baleID", String(32), unique=True)
    chat_id: Column[BigInteger] = Column("chatID", BigInteger, unique=True)
    # chats
    # blocks
    # reports

    def __init__(self, baleid: str, chatid: int) -> None:
        self.bale_id = baleid
        self.chat_id = chatid

    def __repr__(self) -> dict[str, str]:
        return {
            'anonid': str(self.anon_id),
            'baleid': str(self.bale_id),
            'chatid': str(self.chat_id)
        }

    def __str__(self) -> str:
        return f"<user {self.anon_id}>"


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def add_user(chat_id: int, bale_id: str) -> str:
    async with SessionLocal() as session:
        async with session.begin():
            user: User = User(bale_id, chat_id)
            session.add(user)
        await session.refresh(user)
        return str(user.anon_id)


async def get_chatid(anonid: str) -> int:
    "get user's chat ID by Anonymous ID"
    async with SessionLocal() as session:
        executed: Result[_T] = await session.execute(
            select(User.chat_id)
            .where(User.anon_id == anonid)
        )
        result: int = executed.scalar_one_or_none()
        if result is None:
            raise ValueError(f"user not found.")
        return result
