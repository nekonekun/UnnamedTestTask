"""Database adapters."""
from contextlib import contextmanager

from sqlalchemy import insert, select
from sqlalchemy.orm import Session, selectinload, sessionmaker

from digest.db import (
    Digest,
    Post,
    PostDigest,
    Subscription,
    UserSubscription,
)
from digest.schemas import DigestDTO, PostDTO


class RepoBase:
    """Base adapter class."""

    def __init__(self, sessionmaker_: sessionmaker):
        """Initialize adapter with sessionmaker.

        :param sessionmaker_: sessionmaker instance
        :type sessionmaker_: sessionmaker
        """
        self.sessionmaker = sessionmaker_

    @contextmanager
    def session_control(self, commit: bool = True, session: Session = None):
        """Create new Session if not provided.

        :param commit: commits if set to True and Session is not provided
        :type commit: bool
        :param session: already opened session. Will be created if not provided
        :type session: Session
        :return: Session instance to work with
        """
        current_session = session if session else self.sessionmaker()

        yield current_session

        if not session:
            if commit:
                current_session.commit()
            current_session.close()


class Gateway(RepoBase):
    """Database adapter. Works with all used in project tables."""

    def read_posts_for_user(
        self, user_id: int, session: Session | None = None
    ) -> list[PostDTO]:
        """Read posts from user subscriptions.

        :param user_id: target user ID
        :type user_id: int
        :param session: session to be passed to session_control
        :type session: Session
        :return: list of Posts
        """
        stmt = select(Post).join(Subscription).join(UserSubscription)
        stmt = stmt.where(Subscription.id == Post.subscription_id)
        stmt = stmt.where(UserSubscription.user_id == user_id)
        with self.session_control(commit=False, session=session) as s:
            response = s.execute(stmt)
            posts: list[Post] = response.scalars().all()
        return [PostDTO.model_validate(post) for post in posts]

    def create_digest(
        self, user_id: int, *post_ids: int, session: Session | None = None
    ) -> DigestDTO | None:
        """Create and save Digest for given user.

        :param user_id: target user ID
        :type user_id: int
        :param post_ids: post IDs to be included in Digest
        :type post_ids: int
        :param session: session to be passed to session_control
        :type session: Session
        :return: resulting Digest
        """
        if not post_ids:
            return None
        stmt = insert(Digest).values(user_id=user_id)
        stmt = stmt.returning(Digest)
        with self.session_control(commit=True, session=session) as s:
            response = s.execute(stmt)
            digest_: Digest = response.scalars().first()
            stmt = insert(PostDigest).values(
                [
                    {'post_id': post_id, 'digest_id': digest_.id}
                    for post_id in post_ids
                ]
            )
            s.execute(stmt)
            s.refresh(digest_)
            return DigestDTO.model_validate(digest_)

    def read_digest(
        self, digest_id: int, session: Session | None = None
    ) -> DigestDTO | None:
        """Read Digest by id.

        :param digest_id: target digest ID
        :type digest_id: int
        :param session: session to be
        :type session: Session
        :return: found digest or None
        """
        stmt = select(Digest)
        stmt = stmt.where(Digest.id == digest_id)
        stmt = stmt.options(selectinload(Digest.posts))
        with self.session_control(commit=False, session=session) as s:
            response = s.execute(stmt)
            content: Digest = response.scalars().first()
            if content:
                return DigestDTO.model_validate(content)
            return None
