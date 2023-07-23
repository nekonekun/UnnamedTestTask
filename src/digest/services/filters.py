from digest.schemas import PostDTO


def dummy_filter(*posts: PostDTO, limit: int = 5) -> list[int]:
    result = sorted(posts, key=lambda x: x.popularity, reverse=True)[:limit]
    return [post.id for post in result]


def at_least_one_subscription(*posts: PostDTO, limit: int = 5) -> list[int]:
    result = []
    indexes = []
    included_subscriptions = []
    posts = sorted(posts, key=lambda x: x.popularity, reverse=True)
    for index, post in enumerate(posts):
        if len(result) >= limit:
            break
        if post.subscription_id not in included_subscriptions:
            result.append(post.id)
            included_subscriptions.append(post.subscription_id)
            indexes.append(index)
    for index, post in enumerate(posts):
        if len(result) >= limit:
            break
        if index not in indexes:
            result.append(post.id)
    return result
