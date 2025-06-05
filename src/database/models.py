from sqlalchemy import Column, String, DateTime, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Base = declarative_base()


def lazy_relationship(*args, **kwargs):
    return relationship(*args, uselist=True, **kwargs)


user_blob_association = Table(
    "user_chatrooms",
    Base.metadata,
    Column("user_id", String(36), ForeignKey("users.id"), primary_key=True),
    Column("blob_id", String(36), ForeignKey("blobs.id"), primary_key=True),
)


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, index=True, unique=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    name = Column(String(16, collation='utf8mb4_bin'), unique=True, index=True)

    account = lazy_relationship("UserAccount", back_populates="user")

    blobs = lazy_relationship("Blob", secondary=user_blob_association, backref="users")


class UserAccount(Base):
    __tablename__ = "accounts"

    id = Column(String(36), primary_key=True, index=True, unique=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    username = Column(String(16, collation='utf8mb4_bin'), unique=True, index=True)
    password = Column(String(256))

    user_id = Column(String(36), ForeignKey("users.id"))
    user = lazy_relationship("User", back_populates="account")


class Blob(Base):
    __tablename__ = "blobs"

    id = Column(String(36), primary_key=True, index=True, unique=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    content_type = Column(String(16))
    filename = Column(String(512, collation='utf8mb4_bin'))
    url = Column(String(1024))
