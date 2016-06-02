# Busbus

An API proxy for NextBus departure information.

This app fetches routes and stops information from the NextBus public API and
stores it locally in a database. It also provides departure information for the
closest stops of a desired location.

Check the [documentation](http://bflask.readthedocs.io/en/latest/).

## Development Environment

At a bare minimum you'll need:

- Python 3
- PostgreSQL
- Virtualenv

Assuming you have the required dependencies, then run:

```bash
$ git clone <repo>
$ cd <project>
$ mkdir env | virtualenv env --python python3
$ source env/bin/activate
$ pip install -r requirements.txt
```

The app uses a `.env` file to export environment variables to its instance
settings. Create a `.env` file like the sample below and modify according to
your local setup.

```
FLASK_DEBUG=1
DATABASE_URL=postgresql://user:password@host:port/database
```

The app uses [Alembic](https://bitbucket.org/zzzeek/alembic) to manage database
migrations. Run `$ python app.py db upgrade` to install.

## Running

`TODO`

## Testing

`TODO`
