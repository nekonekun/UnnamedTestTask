from datetime import datetime

from sqlalchemy import ForeignKey, MetaData
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    """Base class"""

    metadata = MetaData(
        naming_convention={
            'ix': 'ix_%(column_0_label)s',
            'uq': 'uq_%(table_name)s_%(column_0_name)s',
            'ck': 'ck_%(table_name)s_`%(constraint_name)s`',
            'fk': 'fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s',
            'pk': 'pk_%(table_name)s',
        }
    )


class UserSubscription(Base):
    __tablename__ = 'users_subscriptions'
    user_id: Mapped[int] = mapped_column(
        ForeignKey('users.id'), primary_key=True
    )
    subscription_id: Mapped[int] = mapped_column(
        ForeignKey('subscriptions.id'), primary_key=True
    )


class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    subscriptions: Mapped[list['Subscription']] = relationship(
        secondary=UserSubscription.__table__, back_populates='users'
    )
    digests: Mapped[list['Digest']] = relationship(back_populates='user')


class Subscription(Base):
    __tablename__ = 'subscriptions'
    id: Mapped[int] = mapped_column(primary_key=True)
    source: Mapped[str] = mapped_column()
    users: Mapped[list['User']] = relationship(
        secondary=UserSubscription.__table__, back_populates='subscriptions'
    )
    posts: Mapped[list['Post']] = relationship()


class PostDigest(Base):
    __tablename__ = 'posts_digests'
    post_id: Mapped[int] = mapped_column(
        ForeignKey('posts.id'), primary_key=True
    )
    digest_id: Mapped[int] = mapped_column(
        ForeignKey('digests.id'), primary_key=True
    )


class Post(Base):
    __tablename__ = 'posts'
    id: Mapped[int] = mapped_column(primary_key=True)
    subscription_id: Mapped[int] = mapped_column(
        ForeignKey('subscriptions.id', ondelete='CASCADE'), nullable=False
    )
    subscription: Mapped[Subscription] = relationship()
    content: Mapped[str] = mapped_column()
    rating: Mapped[int] = mapped_column()
    digests: Mapped[list['Digest']] = relationship(
        secondary=PostDigest.__table__, back_populates='posts'
    )


class Digest(Base):
    __tablename__ = 'digests'
    id: Mapped[int] = mapped_column(primary_key=True)
    timestamp: Mapped[datetime] = mapped_column(
        TIMESTAMP, server_default=func.now()
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey('users.id', ondelete='CASCADE'), nullable=False
    )
    user: Mapped[User] = relationship(back_populates='digests')
    posts: Mapped[list['Post']] = relationship(
        secondary=PostDigest.__table__, back_populates='digests'
    )
