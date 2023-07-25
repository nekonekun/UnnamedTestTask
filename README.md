# Another test task

Task description available [here](docs/TaskDescription.md)


## How it works

### Workflow
I assume that posts from different sources are stored in database
1. Script continuously reads user IDs from rabbit.
2. After receiving a new user ID, script reads all posts from user subscriptions.
3. Then script composes digest based on post rating, but tries to include at least one post of every subscription.
4. Then script saves digest to database, and saves digest to Redis with user ID as key.
### Database schema
###### User
 - id
 - name

###### Subscription
 - id
 - source

###### UserSubscription
 - user_id (ForeignKey on `User.id`)
 - subscription_id (ForeignKey on `Subscription.id`)

###### Post
 - id
 - subscription_id (ForeignKey on `Subscription.id`)
 - content
 - rating

###### Digest
 - id
 - timestamp
 - user_id (ForeignKey on `User.id`)

###### PostDigest
 - post_id (ForeignKey on `Post.id`)
 - digest_id (ForeignKey on `Digest.id`) 

So:
 - User can subscribe to many sources
 - Source can be subscribed by many users
 - Digest can contain many posts
 - Post can be included in many digests
## Run

Copy example env file
```shell
cp .env.example .env
```
Adjust as you wish

Run docker-compose
```shell
docker-compose up --build
```

## Test

Run docker-compose
```shell
docker-compose -f tests/docker-compose.yaml up --abort-on-container-exit --build
```

Containers will automatically stop after test finish.