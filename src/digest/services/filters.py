"""Posts-filtering functions."""
from digest.schemas import PostDTO


def dummy_filter(*posts: PostDTO, limit: int = 5) -> list[int]:
    """Filter posts by rating.

    :param posts: posts to be filtered
    :type posts: PostDTO
    :param limit: how many posts should be returned
    :type limit: int
    :return: list of chosen Posts IDs
    """
    result = sorted(posts, key=lambda x: x.rating, reverse=True)[:limit]
    return [post.id for post in result]


def at_least_one_subscription(
        *posts: PostDTO,
        limit: int = 5
) -> list[int]:
    """Semi-smart filter.

    Return top-rated post from each subscription.
    If number of subscriptions is lower than limit,
    then add other top-rated posts.

    :param posts: posts to be filtered
    :type posts: PostDTO
    :param limit: how many posts should be returned
    :type limit: int
    :return: list of chosen Posts IDs
    """
    result = []
    indexes = []
    included_subscriptions = []
    posts = sorted(posts, key=lambda x: x.rating, reverse=True)
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
