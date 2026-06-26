import datetime
from sqlalchemy import String, Integer, BigInteger, Boolean, DateTime, Text, ForeignKey, Float
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)  # Telegram User ID
    username: Mapped[str] = mapped_column(String(150), nullable=True)
    first_name: Mapped[str] = mapped_column(String(150), nullable=True)
    last_name: Mapped[str] = mapped_column(String(150), nullable=True)
    profile_photo: Mapped[str] = mapped_column(String(500), nullable=True)
    join_date: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)
    last_activity: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)
    download_count: Mapped[int] = mapped_column(Integer, default=0)
    is_banned: Mapped[bool] = mapped_column(Boolean, default=False)

class Download(Base):
    __tablename__ = "downloads"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"))
    platform: Mapped[str] = mapped_column(String(50))
    url: Mapped[str] = mapped_column(Text)
    file_name: Mapped[str] = mapped_column(String(255), nullable=True)
    size: Mapped[int] = mapped_column(BigInteger, default=0)  # in bytes
    status: Mapped[str] = mapped_column(String(50))  # completed, failed, processing
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)

class ApiRoute(Base):
    __tablename__ = "apis"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100))
    platform: Mapped[str] = mapped_column(String(50))
    endpoint: Mapped[str] = mapped_column(String(500))
    status: Mapped[bool] = mapped_column(Boolean, default=True)
    priority: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)

class AdminUser(Base):
    __tablename__ = "admins"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(100), unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    permissions: Mapped[str] = mapped_column(String(255), default="root")

class Promotion(Base):
    __tablename__ = "promotions"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(200))
    sponsor_username: Mapped[str] = mapped_column(String(100), nullable=True)
    sponsor_name: Mapped[str] = mapped_column(String(150), nullable=True)
    image_file_id: Mapped[str] = mapped_column(String(500), nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    message: Mapped[str] = mapped_column(Text, nullable=True)
    button_text: Mapped[str] = mapped_column(String(100), nullable=True)
    button_url: Mapped[str] = mapped_column(String(500), nullable=True)
    status: Mapped[bool] = mapped_column(Boolean, default=True)
    views: Mapped[int] = mapped_column(Integer, default=0)
    clicks: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)

class AppSettings(Base):
    __tablename__ = "settings"
    
    key: Mapped[str] = mapped_column(String(100), primary_key=True)
    value: Mapped[str] = mapped_column(Text)