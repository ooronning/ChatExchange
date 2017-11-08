# This README is more aspirational than descriptive, that is to say, this is mostly `NOT IMPLEMENTED NOT IMPLEMENTED NOT IMPLEMENTED NOT IMPLEMENTED NOT IMPLEMENTED NOT IMPLEMENTED NOT IMPLEMENTED NOT IMPLEMENTED`.

ChatExchange 3
==============

A Python 3 library and command-line tool for Stack Exchange chat.

## Authentication

For authenticated use specify a Stack Exchange username and password in
the `ChatExchangeU` and `ChatExchangeP` environment variables. OpenID and
OAuth authentication are not supported.

## Installation

```
pip install chatexchange3
```

## Command-Line Interface

This hasn't been implemented.

Import (or update) the full history of a chatroom to the database.
Records updated within the last 3600 seconds will be considered up-to-date.

```
chatexchange sqlite://./data se/rooms/1 --all --max-age=3600
```

Add new messages to the database as they come in:

```
chatexchange sqlite://./data se/rooms/1 --all --max-age=Infinity --watch
```

Send a message, then disconnect (a temporary in-memory SQLite database will be used):

```
chatexchange  se/rooms/1 --send "hello world"
```

## Python Interface

### Public (Please Use)

```
- chatexchange
    - .Client() # The public interface requires 
        - .get_server(slug) -> .client.Server
        - .se() -> .client.Server
        - .so() -> .client.Server
        - .mse() -> .client.Server
        - .sql_engine -> SQLAlchemy Engine
        - .sql_session() -> SQLAlchemy Session Bound to Engine
    - .models # SQLAlchmeny models for the data 
        - .Base(**attrs) extends SQLAlchemy ORM Declarative Base
            .__repr__
            .set(**attrs) -> self
            .meta_id: int
            .meta_created: DateTime
            .meta_updated: DateTime
            .meta_deleted: DateTime
            .deleted: boolean
            .meta_slug: str
            @classmethod .meta_id_from_meta_slug(meta_slug) -> int
        - .Server extends .Base
        - .User extends .Base
        - .Room extends .Base
        - .Message extends .Base
    - .client # Extended models with a reference to the client and lots of sugar
        - .Server extends ..models.Server
            .get_user(id) -> .User()
            .get_room(id) -> .Room()
            .get_message(id) -> .Message()
        - .User extends ..models.User
        - .Room extends ..models.Room
        - .Message extends ..models.Message
```

### Internal (Do Not Use)

```
- chatexchange
    - ._seed
        - .data() # yields a bunch of seed data that needs to be added to new databases
    - ._parser # classes interpreting specific HTML pages as structured data
        - .TranscriptPage
    - ._obj_dict
        - .update(o, **attrs) # a generic __init__ asserting named attributes already exist 
        - .updated(o, **attrs) # chainable version of .update()
        - .repr(o) -> # a generic __repr__() useful for debugging
```

## License

Licensed under either of

 - Apache License, Version 2.0, ([LICENSE-APACHE](LICENSE-APACHE) or
   http://www.apache.org/licenses/LICENSE-2.0)
 - MIT license ([LICENSE-MIT](LICENSE-MIT) or http://opensource.org/licenses/MIT)

at your option.

### Contribution

Unless you explicitly state otherwise, any contribution intentionally submitted
for inclusion in the work by you, as defined in the Apache-2.0 license, shall
be dual licensed as above, without any additional terms or conditions.
