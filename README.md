# Backend Morra

https://morra.carminezacc.com

This documentation is split in two sections:

1. [HTTP API Reference](#api-reference)
2. [Architecture description](#architecture)

# API Reference

The API exposes multiple HTTP routes.

In this documentation, if there are parameters in
the route's path, they will be
surrounded by angle brackets, because that's how
it's specified in Flask code, so we're doing it
this way in the docs as well.

The API can be divided in three sections:
1. [Users](#Users), which deals with user creation and authentication.
2. [MatchMaking](#Matchmaking), which creates matches based on the currently online players.
3. [Matches](#Matches), which manages each match.

Each of these sections is implemented in a dedicated file in
the `_routes` subdirectory of this repository.

## Users

The API uses HTTP Bearer authentication, more specifically
requests are authorized using JWTs with no expiration date
provided by the API after a successful login to an existing
user account.

Here is a table of contents with all the routes in this section:
1. [GET `/users`](#get-users)
2. [GET `/users/user/<user_id>`](#get-usersuseruser_id)
3. [GET `/users/verify`](#get-usersverify)
4. [POST `/users/signup`](#post-userssignup)
5. [POST `/users/login`](#post-userslogin)

### Username and password requirements

To be valid, an username has to be composed exclusively of
alphanumeric characters (only letters and/or digits), and have
a length of a minimum of 3 characters and a maximum of 30.
Usernames must also be unique within the database.

A valid password can be composed of any printable character,
with the length being at least 5 characters and at most 50.

### GET `/users`

This route takes no parameters and returns an array of registered users in JSON format:

~~~
[
  {
    "id": 1,
    "punteggio": 0,
    "sconfitte": 0,
    "username": "carzacc",
    "vittorie": 0
  },
  {
    "id": 2,
    "punteggio": 0,
    "sconfitte": 0,
    "username": "Grimos10",
    "vittorie": 0
  }
]
~~~

### GET `/users/user/<user_id>`

This route's only parameter is the user ID in the query URL.
It returns the data of the user identified by that ID in JSON format.

Example output for `/users/user/1`:

~~~
{
  "id": 1,
  "punteggio": 0,
  "sconfitte": 0,
  "username": "carzacc",
  "vittorie": 0
}
~~~

### GET `/users/verify`

This route takes a JWT token in the `Authorization`
header field, in the standard HTTP bearer token format:
`Authorization: Bearer <jwt>` and returns one of the following:

* `OK` with status code 200 if the header is present and formatted 
correctly, and the JWT is valid;
* `missing Authorization header` with status code 400 if there is no `Authorization` header; 
* `bad Authorization string` with status code 400 if the `Authorization` header
content is not properly formatted;
* `bad token` with status code 401 if the provided token isn't valid.

### POST `/users/signup`

This route takes a POST request body in `application/x-www-form-urlencoded`
or `multipart/form-data` format containing two parameters:

* the `username` of the user to create;
* the `password` for the user.

and creates an user accordingly.

It returns:
* `OK` with status code 201 if the request body is valid and the user has been created;
* `missing form` with status code 400, if no valid form in the supported formats is sent along with the request;
* `missing fields [<list_of_missing_stuff>]` with status code 400 if there are missing fields in the form;
* `invalid fields [<list_of_invalid_stuff>]` with status code 400 if the username and/or password does not align with the [requirements](#username-and-password-requirements);
* `username conflict` with status code 409 if there is another user in the database with the same username.

### POST `/users/login`

This route takes a POST request body in `application/x-www-form-urlencoded`
or `multipart/form-data` format containing two parameters:

* the `username` of an existing user;
* the user's`password`.

and attempts to log into that user's account.

It returns:

* a newly generated JWT, as per the [RFC 7519](https://tools.ietf.org/html/rfc7519)
standard for the user with status code 200 if the login attempt was successful
(the user exists and the password is correct).
* `missing form` with status code 400, if no valid form in the supported formats is sent along with the request;
* `missing fields [<list_of_missing_stuff>]` with status code 400 if there are missing fields in the form;
* `invalid fields [<list_of_invalid_stuff>]` with status code 400 if the username and/or password does not align with the [requirements](#username-and-password-requirements);
* `bad credentials` with status code 401 if the login attempt failed either because
the user doesn't exist or the password is wrong.

## Matchmaking

The matchmaking section exposes five HTTP routes and listens

1. [GET `/mm/public_queue`](#get-mmpublic_queue)
2. [GET `/mm/private_queue`](#get-mmprivate_queue)
1. [GET `/mm/queue_status`](#get-mmqueue_status)
2. [POST `/mm/public_queue`](#post-mmprivate_queue)
2. [POST `/mm/private_queue`](#post-mmpublic_queue)
3. [POST `/mm/play_with_friends`](#post-mmplay_with_friends)

### GET `/mm/public_queue`

### GET `/mm/private_queue`

### GET `/mm/queue_status`

~~~
{
    "created": false,
    "pollBefore": iso 8601 string
}
~~~

or

~~~
{
    "created": true,
    "match": 5
}
~~~

### POST `/mm/public_queue`

### POST `/mm/private_queue`

### POST `/mm/play_with_friends`

## Matches

The matches management section exposes four HTTP routes.

1. [GET `/matches`](#get-matches)
2. [GET `/matches/<match_id>`](#get-matchesmatch_id)
3. [POST `/matches/<match_id>/move`](#post-matchesmatch_idmove)
4. [GET `/matches/<match_id>/lastround`](#get-matchesmatch_lastround)


#### GET `/matches`

#### GET `/matches/<match_id>`

#### POST `/matches/<match_id>/move`

#### GET `/matches/<match_id>/lastround`

# Architecture

The big picture is the following: the client interacts with an API that directly
causes or looks for a change in the main MySQL database (which contains data
for users and matches) or the Redis key-value store (which contains the state
of matchmaking and the matches currently being played).

The matchmaking API only has background threads to ensure clients haven't stopped
polling, and that's established solely based on data that's present on Redis,
whereas the match API just changes data in Redis that is then used by
a background thread (when needed) to compute round results or match cancellations
or other similar things, which are then put into Redis.

This architecture means that it should be relatively easy, were the need to arise,
to scale this backend service to multiple identical instances interacting with a single MySQL
database and a single Redis store, and one could expect that the load of
matchmaking and match-playing background threads would be pretty balanced if there
is a balanced number of matchmaking requests to each instance.

## User creation and authentication

To sign up, the user must provide an username and a password. The password will
be stored in the database using the BCrypt password hashing algorithm. The number
of salting iterations is determined by testing the server's performance and
making a judgement call on the compromise between security and speed.

Usernames are limited to 

## Matchmaking

We decided against using WebSockets for a number of reasons, so we've designed
our own matchmaking system, still based around a pub/sub model but using HTTP
request polling.

### The idea

The matchmaking system works around two queues: one of them is a public queue,
to which users desiring to be matched against strangers would be added.

The other queue is a private queue, to which we would add anyone who wants to
do what many other online games call "creating a lobby", waiting for friends
to join them by providing that user's ID.

In future versions, where matchmaking will handle more than just 1v1 matching,
the user ID may be replaced by a lobby ID that may even allow multiple players
in a team to join the public queue and wait for either an equal number of individual
players or another team of the same size to be matched against them.

At this point though, seeing how the game is usually played at a competitive level
locally, we don't think it will ever be a priority to support 3v3 matches, so discussions
about a two-player lobby potentially queuing for bigger than 2v2 matches and looking
for extra teammates is way beyond what we're thinking at this point, even though
we feel it would be something cool to have, having been quite fond CS:GO players
rarely queuing as a 5-player team.

### The implementation

When the client requests to be added to the public queue, the server might find another
user to play against right away, so the client will get the URI to access the match
in the response and status code 201. If that isn't the case, the client will get
status code 200 and the time and URL to poll to check whether a match was created
and to notify the server that it is still waiting.

The response to the polling
requests will be the same as we just described for the first queuing request. If the client
were to fail to poll in time, it is considered disconnected and removed from the queue.

This change in status will be communicated in case the user tries to poll again too late:
then the server will respond with code 404 and the client will have to add the user to
the queue again (this might happen if the user temporarily loses network connection, for example).

The private queue works largely the same way, except that it is impossible for the server
to find a match upon the first request.

Requesting to play with a specific friend will result in the same behaviour as when a match
is found at the first request for a queued user.

#### Match confirmation

Since we can't be sure the waiting client will poll again when the other client gets a match,
the match first has to be confirmed, by waiting for both clients to get the match delivered to
them.

Polling requests to verify the confirmed status will necessarily have to be more frequent.

## Playing the match

If a match is confirmed, the clients have 15 seconds from the creation of the match to communicate
the user's move for the first round. The server will respond by communicating the time and URL
to poll to get the results for the current round. If one of the clients fails to perform these
requests, they will be considered disconnected and the match will finish and counted as a loss
for the disconnecting user and a win for the other user.


