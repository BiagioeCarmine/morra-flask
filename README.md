# Backend Morra

https://morra.carminezacc.com

# API Reference

The API exposes multiple HTTP routes and interacts with two Socket.IO namespaces.

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
* `missing username` with status code 400 if in the form there is no `username`;
* `missing password` with status code 400 if in the form there is no `password`;
* `bad username` with status code 400 if the username does not align with the [requirements](#username-and-password-requirements);
* `bad password` with status code 400 if the password does not align with the [requirements](#username-and-password-requirements).
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
* `missing username` with status code 400 if in the form there is no `username`;
* `missing password` with status code 400 if in the form there is no `password`;
* `bad username` with status code 400 if the username does not align with the [requirements](#username-and-password-requirements);
* `bad password` with status code 400 if the password does not align with the [requirements](#username-and-password-requirements).
* `bad credentials` with status code 401 if the login attempt failed either because
the user doesn't exist or the password is wrong.

## Matchmaking

The matchmaking section exposes two HTTP routes and listens
for Socket.IO connections on the `/mm` namespace.

1. [GET `/mm/public_queue`](#get-mmpublic_queue)
2. [GET `/mm/private_queue`](#get-mmprivate_queue)
1. [`queue` event](#queue)
2. [`private_queue` event](#private_queue)
3. [`play_with_friends` event](#play_with_friend)

### HTTP routes

1. [GET `/mm/public_queue`](#get-mmpublic_queue)
2. [GET `/mm/private_queue`](#get-mmprivate_queue)

#### GET `/mm/public_queue`

#### GET `/mm/private_queue`

### Socket.IO events

All of these events are handled in the `/mm` namespace and the
default `/socket.io` path.

1. [`queue` event](#queue)
2. [`private_queue` event](#private_queue)
3. [`play_with_friends` event](#play_with_friend)

#### `queue`

#### `private_queue`

#### `play_with_friend`

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
