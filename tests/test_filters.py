import logging

from digest.services.filters import dummy_filter, at_least_one_subscription


def test_dummy_filter(gateway):
    user_id = 1
    posts = gateway.read_posts_for_user(user_id)
    filtered_posts = dummy_filter(*posts)
    assert len(filtered_posts) == 5

    user_id = 3
    posts = gateway.read_posts_for_user(user_id)
    filtered_posts = dummy_filter(*posts)
    assert len(filtered_posts) == 0


def test_at_least_one_subscription(gateway):
    user_id = 1
    posts = gateway.read_posts_for_user(user_id)
    filtered_posts = at_least_one_subscription(*posts)
    filtered_dtos = list(filter(lambda x: x.id in filtered_posts, posts))
    assert all(post.subscription_id == 1 for post in filtered_dtos)

    user_id = 2
    posts = gateway.read_posts_for_user(user_id)
    filtered_posts = at_least_one_subscription(*posts)
    filtered_dtos = list(filter(lambda x: x.id in filtered_posts, posts))
    assert all(post.subscription_id in [2, 3, 4] for post in filtered_dtos)
    assert any(post.subscription_id == 2 for post in filtered_dtos)
    assert any(post.subscription_id == 3 for post in filtered_dtos)
    assert any(post.subscription_id == 4 for post in filtered_dtos)

    user_id = 2
    posts = gateway.read_posts_for_user(user_id)
    filtered_posts = at_least_one_subscription(*posts, limit=2)
    filtered_dtos = list(filter(lambda x: x.id in filtered_posts, posts))
    assert len(filtered_posts) == 2
    assert filtered_dtos[0].subscription_id != filtered_dtos[1].subscription_id
