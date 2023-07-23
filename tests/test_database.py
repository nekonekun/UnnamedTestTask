def test_gateway_read_posts(gateway, refill_database):
    assert gateway.read_posts_for_user(3) == []
    football_posts = gateway.read_posts_for_user(1)
    assert len(football_posts) == 10
    news_posts = gateway.read_posts_for_user(2)
    assert len(news_posts) == 12


def test_gateway_make_digest(gateway, refill_database):
    user_id = 3
    posts = gateway.read_posts_for_user(user_id)
    assert gateway.create_digest(user_id, *[post.id for post in posts]) is None

    user_id = 1
    posts = gateway.read_posts_for_user(user_id)
    digest_ = gateway.create_digest(user_id, *[post.id for post in posts])
    assert digest_ is not None
    assert digest_.user_id == user_id
    assert len(digest_.posts) == 10


def test_gateway_read_digest(gateway, refill_database):
    user_id = 1
    posts = gateway.read_posts_for_user(user_id)
    digest_ = gateway.create_digest(user_id, *[post.id for post in posts])

    check = gateway.read_digest(digest_.id)

    assert digest_.id == check.id
    assert digest_.user_id == check.user_id
    assert digest_.timestamp == check.timestamp
    assert all(post in check.posts for post in digest_.posts)

    assert gateway.read_digest(2) is None
