# This README is more aspirational than descriptive, that is to say, this is mostly `NOT IMPLEMENTED NOT IMPLEMENTED NOT IMPLEMENTED NOT IMPLEMENTED NOT IMPLEMENTED NOT IMPLEMENTED NOT IMPLEMENTED NOT IMPLEMENTED`.

ChatExchange 3
==============

A Python 3 library and command-line tool for Stack Exchange chat.

## Installation

```
pip install chatexchange3  # or your Python 3 packaging alternative of choice
```

## Authentication

For authenticated use specify a Stack Exchange username and password in
the `ChatExchangeU` and `ChatExchangeP` environment variables. OpenID and
OAuth authentication are not supported.

## Command-Line Interface

This hasn't been implemented, but I'd like to support things like this:

Import (or update) the full history of a chatroom to the database.
Records updated within the last 3600 seconds will be considered up-to-date.

```
chatexchange sqlite://./data se/r/1 --all --max-age=3600
```

Add new messages to the database as they come in:

```
chatexchange sqlite://./data chat.stackexchange.com/rooms/1 --all --max-age=Infinity --watch
```

Send a message, then disconnect (a temporary in-memory SQLite database will be used):

```
chatexchange se/r/1 --send "hello world"
```

Or maybe using our local slugs:

```
chatexchange r/B6 -s "hello world"
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
            @property .deleted: boolean
            @property .meta_slug: str
            @classmethod .meta_id_from_meta_slug(meta_slug) -> int
        - .Server extends .Base
            .url: str
            .slug: str
            .name: str
        - .User extends .Base
            .server_meta_id: int
            .id: int
            .name: str
        - .Room extends .Base
            .server_meta_id: int
            .id: int
            .name: str
        - .Message extends .Base
            .owner_meta_id: int
            .room_meta_id: int
            .id: int
            .content_html: str
            .content_text: str # derived from the HTML
            .content_markdown: str # usually None because we don't know it
    - .client # Extended models with a reference to the client and lots of sugar
        - .Server extends ..models.Server
            .get_user(id) -> .User()
            .get_room(id) -> .Room()
            .get_message(id) -> .Message()
        - .User extends ..models.User
            @property .server -> .Server
        - .Room extends ..models.Room
            @property .server -> .Server
        - .Message extends ..models.Message
            @property .owner -> .User
            @property .room -> .Room
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

### Contributors

Please see the Git commit history or 
https://github.com/jeremyBanks/ChatExchange/contributors and
https://github.com/Manishearth/ChatExchange/contributors.
