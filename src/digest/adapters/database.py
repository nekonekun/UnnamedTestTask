from contextlib import contextmanager

from sqlalchemy import desc, insert, select
from sqlalchemy.orm import Session, joinedload, selectinload, sessionmaker

from digest.db.models import (
    Digest,
    Post,
    PostDigestAssociation,
    Subscription,
    UserSubscriptionAssociation,
)
from digest.schemas import DigestDTO, PostDTO


class RepoBase:
    def __init__(self, sessionmaker_: sessionmaker):
        self.sessionmaker = sessionmaker_

    @contextmanager
    def session_control(self, commit: bool = True, session: Session = None):
        current_session = session if session else self.sessionmaker()

        yield current_session

        if not session:
            if commit:
                current_session.commit()
            current_session.close()


class Gateway(RepoBase):
    def read_most_popular_posts_for_user(
        self, user_id: int, limit: int = 5, session: Session | None = None
    ):
        stmt = select(Post).join(Subscription.posts)
        stmt = stmt.join(UserSubscriptionAssociation)
        stmt = stmt.where(UserSubscriptionAssociation.user_id == user_id)
        stmt = stmt.order_by(desc(Post.popularity)).limit(limit)
        with self.session_control(commit=False, session=session) as s:
            response = s.execute(stmt)
            posts: list[Post] = response.scalars().all()
        return [PostDTO.model_validate(post) for post in posts]

    def create_digest(
        self, user_id: int, *post_ids: int, session: Session | None = None
    ):
        stmt = insert(Digest).values(user_id=user_id)
        stmt = stmt.returning(Digest).options(selectinload(Digest.posts))
        with self.session_control(commit=True, session=session) as s:
            response = s.execute(stmt)
            digest_: Digest = response.scalars().first()
            stmt = insert(PostDigestAssociation).values(
                [
                    {'post_id': post_id, 'digest_id': digest_.id}
                    for post_id in post_ids
                ]
            )
            s.execute(stmt)
            s.refresh(digest_)
            stmt = select(Post).where(Post.id.in_(post_ids))
            response = s.execute(stmt)
            posts = response.scalars().all()
            return DigestDTO(
                id=digest_.id,
                user_id=digest_.user_id,
                timestamp=digest_.timestamp,
                posts=[PostDTO.model_validate(post) for post in posts],
            )

    def read_digest(self, digest_id: int, session: Session | None = None):
        stmt = select(PostDigestAssociation)
        stmt = stmt.options(joinedload(PostDigestAssociation.digests))
        stmt = stmt.where(PostDigestAssociation.digest_id == digest_id)
        stmt = stmt.options(joinedload(PostDigestAssociation.posts))
        with self.session_control(commit=False, session=session) as s:
            response = s.execute(stmt)
            content = response.scalars().all()
            if content:
                response = DigestDTO(
                    id=content[0].digests.id,
                    user_id=content[0].digests.user_id,
                    timestamp=content[0].digests.timestamp,
                    posts=[
                        PostDTO.model_validate(entry.posts)
                        for entry in content
                    ],
                )
            else:
                response = None
        return response
