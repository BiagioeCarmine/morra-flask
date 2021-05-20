# Backend Morra

https://morra.carminezacc.com

This documentation is split in two sections:

1. [HTTP API Reference](#api-reference)
2. [Architecture description](#architecture)

The second part in particular is way too long, detailed and pretending to be serious and fun at the same time for its
own good.

# API Reference

The API exposes multiple HTTP routes.

In this documentation, if there are parameters in
the route's path, they will be
surrounded by angle brackets, because that's how
it's specified in Flask code, so we're doing it
this way in the docs as well.

The API can be divided in three sections:
1. [Users](#users), which deals with user creation and authentication.
2. [MatchMaking](#matchmaking), which creates matches based on the currently online players.
3. [Matches](#matches), which manages each match.

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

If there is no user with that ID, it responds with `not found` and
status code 404.

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

* `{id: <user_id>}` with status code 200 if the header is present and formatted 
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

1. [GET `/mm/queue`](#get-mmqueue)
1. [GET `/mm/queue_status`](#get-mmqueue_status)
2. [POST `/mm/queue`](#post-mmqueue)
3. [POST `/mm/play_with_friend`](#post-mmplay_with_friend)

### GET `/mm/queue`

This route takes the `type` of queue as a query parameter and
returns a list of the users currently in the chosen queue and
status code 200 if the `type` is present and set to either
`public` or `private`, or status code 400 and:

* `missing queue type` if there is no `type` query parameter and;
* `invalid queue type` if the specified `type` is neither `public` nor `private`.

If the queue is empty, the status code is still 200 and it returns
an empty list (`[]`).

Example for `/mm/queue?type=public`:

~~~
[
  {
    "id": 1,
    "punteggio": 0,
    "sconfitte": 0,
    "username": "carzacc",
    "vittorie": 0
  }
]
~~~

Example for `/mm/queue?type=private` (where there is the possibility of having more than one queued user):

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

### GET `/mm/queue_status`

This route takes a JWT token in the `Authorization`
header field, in the standard HTTP bearer token format:
`Authorization: Bearer <jwt>` and is a route used by the
client to know whether a match has been created for the user.

Either this isn't the case, and the user has to poll again:

~~~
{
   "created":false,
   "inQueue":true,
   "pollBefore":"2021-04-27T13:37:43.106416+00:00"
}
~~~

or a match has been created since the last poll, and in that
case the ID is returned in the response:

~~~
{
    "created": true,
    "match": 5
}
~~~

### POST `/mm/queue`

This route takes a JWT token in the `Authorization`
header field, in the standard HTTP bearer token format:
`Authorization: Bearer <jwt>` and a POST request form in `application/x-www-form-urlencoded`
or `multipart/form-data` format containing one parameter:

* `type` set to `public` or `private`.

You can expect the same responses as the ones returned by [GET `/users/verify`](#get-usersverify) if there is an issue
with the `Authorization` header, and the same behaviour as [POST `/users/signup`](#post-userssignup) if the form is
missing or invalid.

If the request is valid, the route adds the user to the chosen matchmaking queue, and this can result in one of two
things: either the queue is empty or the user is being added to the private queue
, so the user will get the following, asking to poll  again (at `/mm/queue_status`):

~~~
{
   "created":false,
   "inQueue":true,
   "pollBefore":"2021-04-27T13:37:43.106416+00:00"
}
~~~

or, if the chosen queue is the public queue, there may be another user in queue,
which means that a match will be created right away and the ID will be returned:

~~~
{
    "created": true,
    "match": 5
}
~~~
  
### POST `/mm/play_with_friend`

This route is used to ask to play with an user supposed to be in the private queue.

This route takes a JWT token in the `Authorization`
header field, in the standard HTTP bearer token format:
`Authorization: Bearer <jwt>` and a POST request form in `application/x-www-form-urlencoded`
or `multipart/form-data` format containing one parameter:

* `user`, the ID of the user to play with.

You can expect the same responses as the ones returned by [GET `/users/verify`](#get-usersverify) if there is an issue
with the `Authorization` header, and the same behaviour as [POST `/users/signup`](#post-userssignup) if the form is
missing or invalid.

If the request is valid and the user is online, the response the following, with `1` replaced by the match ID:

~~~
{
  "created":true,
  "match":1
}
~~~

If the user is not online, it will return `friend not online` and status code 404.

## Matches

The matches management section exposes four HTTP routes.

1. [GET `/matches`](#get-matches)
2. [GET `/matches/<match_id>`](#get-matchesmatch_id)
3. [POST `/matches/<match_id>/move`](#post-matchesmatch_idmove)
4. [GET `/matches/<match_id>/last_round`](#get-matchesmatch_idlast_round)


#### GET `/matches`

This route returns a list of the matches currently in the database. It returns an empty list (`[]`) if there aren't
any, or something like this if there are some:

~~~
[
  {
    "confirmed": true,
    "finished": true,
    "id": 1,
    "punti1": 12,
    "punti2": 5,
    "start_time": "2021-04-28T07:20:20+00:00",
    "first_round_results": "2021-04-28T07:20:30+00:00",
    "userid1": 1,
    "userid2": 2
  },
  {
    "confirmed": true,
    "finished": false,
    "id": 2,
    "punti1": 2,
    "punti2": 0,
    "start_time": "2021-04-28T07:48:20+00:00",
    "first_round_results": "2021-04-28T07:48:30+00:00",
    "userid1": 2,
    "userid2": 1
  },
  {
    "confirmed": false,
    "finished": false,
    "id": 3,
    "punti1": 0,
    "punti2": 0,
    "start_time": "2021-04-28T07:50:20+00:00",
    "first_round_results": "2021-04-28T07:50:30+00:00",
    "userid1": 3,
    "userid2": 1
  }
]
~~~

#### GET `/matches/<match_id>`

This route returns the match data for the match with the provided match ID.

If there is no match with that ID, it responds with `not found` and  status code 404.

Example output for `/matches/1`:

~~~
{
  "confirmed": true,
  "finished": true,
  "id": 1,
  "punti1": 12,
  "punti2": 5,
  "start_time": "2021-04-28T07:20:20+00:00",
  "first_round_results": "2021-04-28T07:20:30+00:00",
  "userid1": 1,
  "userid2": 2
}
~~~


#### POST `/matches/<match_id>/move`

This route is used to make a move in a match..

This route takes a JWT token in the `Authorization`
header field, in the standard HTTP bearer token format:
`Authorization: Bearer <jwt>` and a POST request form in `application/x-www-form-urlencoded`
or `multipart/form-data` format containing two parameters:

* `hand`, the number that would be represented by the hand in an in-person game;
* `prediction`, the number the player would shout in a real game.

You can expect the same responses as the ones returned by [GET `/users/verify`](#get-usersverify) if there is an issue
with the `Authorization` header, and the same behaviour as [POST `/users/signup`](#post-userssignup) if the form is
missing or invalid.

If the match ID is not a number, it will return `invalid match_id` with status code 400.

If the user is not part of the match, it will return `User not in match` with status code 401.

If the request is valid, the server will return `OK` and status code 200.

#### GET `/matches/<match_id>/last_round`

This route is used to get the results from the last round that has been played for the match with the specified
`match_id`. It returns `invalid match_id` with status code 400 if the match id is not a number, and `not found` with
status code 404 if the match doesn't exist or no rounds have been played (to avoid accessing the database for this).

Example output for `/matches/5/last_round`:

~~~
{
  "cur_points1": "1",
  "cur_points2": "0",
  "hand1": "1",
  "hand2": "2",
  "next_round_start": "2021-04-28T12:23:40.267734+00:00",
  "next_round_results": "2021-04-28T12:23:50.267734+00:00",
  "prediction1": "3",
  "prediction2": "5"
}
~~~

# Architecture

1. [User creation and authentication](#user-creation-and-authentication)
2. [Matchmaking](#matchmaking-architecture)
   * [The idea](#the-idea)
   * [The implementation](#the-implementation)
3. [Playing the match](#playing-the-match)
4. [How we manage timing](#how-we-manage-timing-aka-where-the-dirty-laundry-might-be)
    * [The running theme](#the-running-theme)
    * [How we manage the queue](#how-we-manage-the-queue)
    * [How we manage playing rounds](#how-we-manage-playing-rounds)


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

Also, using Redis for the data used to respond to polling request (which tend to be, by their nature, very frequent)
instead of storing even more ephemeral data in the database decreases the load on the

## User creation and authentication

To sign up, the user must provide an username and a password. The password will
be stored in the database using the BCrypt password hashing algorithm. The number
of salting iterations is determined by testing the server's performance and
making a judgement call on the compromise between security and speed.

## Matchmaking architecture

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

Currently, we use short polling, but we'll probably switch to long polling at some point,
but that doesn't mean anything for a properly implemented frontend that doesn't hang while
waiting for backend responses.

The response to the polling requests will be the same as we just described for the first queuing request. If the client
were to fail to poll in time, it is considered disconnected and removed from the queue.

This change in status will be communicated in case the user tries to poll again too late:
then the server will respond with code 404 and the client will have to add the user to
the queue again (this might happen if the user temporarily loses network connection, for example).

The private queue works largely the same way, except that it is impossible for the server
to find a match upon the first request.

Requesting to play with a specific friend will result in the same behaviour as when a match
is found at the first request for a queued user.

#### Preempting criticism

An apparently dumb design decision is to have a set in Redis to denote a "public queue" that can contain either one or
zero users.

This, though, isn't entirely the case. Even though we only support 1v1 matches *right now*, the plan is to support
bigger matches, and we don't want to massively change the API and the backend architecture when we decide to switch to
that. As things are right now, matchmaking doesn't have to change a whole lot: we just add some more data to a user's
entry in the queue to specify what kind of matches they're trying to queue for, so we only have to massively overhaul
the match playing part which, as painful-sounding and scary as it is, isn't as bad as pretty much rewriting the
matchmaking code as well.

Also, if the app has massive success (yeah, *ikr*, I'm laughing while writing this as well), we may decide to implement
some additional filters to the matchmaking system (inspired by popular multiplayer games), for example only matching
people with similar ability or, being really visionary and optimistic about the app's chances of great success,
matching people who are geographically close and having them connect to a server in their region.

At the moment, though, it doesn't hurt to have it a bit more symmetrical to the private queue and to be able to
(relatively) easily switch over to supporting 2v2 matches at least as well.

#### Match confirmation

Since we can't be sure the waiting client will poll again when the other client gets a match,
the match first has to be confirmed, by waiting for both clients to get the match delivered to
them.

Polling requests to verify the confirmed status will necessarily have to be more frequent.

## Playing the match

Now, though, let's move on to a more specific anal
If a match is confirmed, the clients have 15 seconds from the creation of the match to communicate
the user's move for the first round. The server will respond by communicating the time and URL
to poll to get the results for the current round. If one of the clients fails to perform these
requests, they will be considered disconnected and the match will finish and counted as a loss
for the disconnecting user and a win for the other user.

## How we manage timing, a.k.a. where the dirty laundry might be

The aspect of the implementation that is most likely to be sub-optimal is the implementation of timing: how we manage
the MM queue and how we manage playing rounds in terms of making sure responses arrive in time and that the server
responds in the right way.

To talk about this, we are [first](#the-running-theme) going to talk about what we're doing and [how we can improve](#a-different-smarter-way-we-could-have-done-things)
in general our approach to solving this problem, then we are going to go over specific implementation details for
[the matchmaking queue](#how-we-manage-the-queue) and [the match rounds mechanism](#how-we-manage-playing-rounds).

### The running theme

Of course, managing a matchmaking queue is different than playing rounds of a match, but the general approach we took
is the same: each time there is a moment in time before which a request is expected, the server is going to have a thread
waiting for that time and checking whether a request was actually made by the client.

The advantage of our current approach is that the server deals with everything in real time when it needs to be dealt
with, so in every moment the server's state reflects what is expected (if the user is inactive, they *will* be kicked out
of the queue when the time comes, and the same goes for match rounds when an user doesn't set a move).

A potential disadvantage is the complexity (both computational and in terms of code) of our app. This is partially
mitigated by the use of lightweight green threads in place of fully fledged OS threads, but we really don't know
whether the next solution I'm going to propose _would have been_/_would be_ better.

Another disadvantage is that network communication (especially using HTTP requests and not stuff like TCP sockets) is
inherently slow, so we need to have grace times that allow the request to be received and the log to be updated before
the user is kicked out of the queue or the match is terminated early.

#### A different (smarter?) way we could have done things

_This section is going to be written mostly in first person as it is mostly a personal reflection based on past personal
experience_.

Borrowing from my (Carmine Zaccagnino, mostly the *backend guy* for this project) previous very brief experiences with
situations in which optimising CPU usage was the whole point of what I was doing, straight-up simulating something isn't
necessarily the most efficient approach to solving a problem.

This means that, of course, having the backend app's state mimic the more abstract state of the app in terms of users
in the queue and match confirmation/termination status maybe could be sacrificed for the sake of keeping things easy for
us when maintaining the code and the server when executing it, and potentially for the sake of eliminating the grace
times that make especially the match playing part a bit clunky and annoying for the end user.

More specifically, instead of having a thread for each check we need to do, we could check on subsequent requests,
given that any effects of a client making or failing to make a request will only be noticed by the client when it
requests something, obviously.

This, though, would increase reliance on data stores like Redis for relatively longer-term data storage (still short-term,
if the app sees any kind of significant usage, which *strangely* feels like it's not very likely D:), which isn't a
worry with the current architecture and implementation, as each request's side-effects are managed when they could start
having an effect and not when they actually might have an effect, if this makes any sense.

If that sentence or this whole section (maybe this entire document) *doesn't*, maybe this next bit will, as it goes
more specifically into the details of each of the two cases in which timing arises as an issue in our app.

### How we manage the queue

Currently, each time an user is added to a queue a thread (more specificaly, a lightweight Eventlet green thread) is
spawned, waiting until the `pollBefore` time, and checking whether the user has polled (we store the latest poll data
in Redis).

Of course, networks and stuff are slow, so we need to allow for a grace time before we kick the user out of the queue,
which is a better option IMO than trying to manage the delay on the client side, partly because it feels less intuitive
and especially because, being a mobile app, we can't update the frontend code very quickly on most or all of the users'
devices in case we realize the needs change.

This could alternatively be managed by evaluating whether an user needs to be deleted from the queue whenever another
matchmaking-related request is received.


### How we manage playing rounds

Each time a match is created, the server spawns a green thread that acts as the match server, coordinating the clients
and giving them the results.

At the heart of this is the part when client interaction comes into play: when a round _ends_ virtually and the clients
have to send the user's move to the server, and then request the round results.

This three-way dependency is the main cause of annoyance when we look at how the backend implementation affects the user
experience: the code that checks whether the users have set their move, computes the round results, and saves them on
Redis for retrieval by the client through the `/matches/<id>/last_round` route.

This means that the code has to run in between those two moments in time, and this means that the time between those two
moments has to be delayed to avoid issues, and currently that delay is quite long (we are looking at shortening it),
which directly affects the user experience when playing a match in a negative way. This is mitigated in the frontend
by adding animations and other entertaining bits to keep the user busy while the client waits for the server to do its
thing.

This could alternatively be managed by calculating the last round results when a client requests the results for the
last round, or when the last client sends the user's move, and by adding flags in Redis to make sure the GET request
results are only given out when they are ready. This would reduce the time to get the results to the minimum necessary,
but would make it unpredictable and potentially inconsistent.

### WebSocket and similar things, a.k.a. the elephant in the room

Could we have used a real-time communication protocol instead? Probably, and this would have eliminated some of the issues,
and many implementation details could have been delegated to the libraries available for such protocols.

Why didn't we do that? That's an hard question to answer. Initially, we wrote this backend's MM system using Socket.io,
but we encountered too many issues when testing that were imputable to Socket.io that we decided against it early on.

Also, we're not sure about Socket.io Android integration, but knowing how bad it is with Flutter we were skeptical right
from the start.

We didn't consider pure WebSocket too much honestly, but our lack of experience with working with and writing an app
that uses WebSocket for most of the exchanges between client and server meant that some of the challenges we thought
we could face now (in the initial implementation) and in the future (if we ever get users) could have meant wasting more
time than it has taken us to write a slightly more complex (and *a lot* slower) system that relies solely on polling.
