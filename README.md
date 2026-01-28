# ZAPHIRO POWER GRID API
this is an api to manage a SLD of a power grid.

## QUICKSTART

#### REQUIREMENTS

- python 3.12
- docker + docker compose
- uv

#### SETUP

clone the repo in your local machine:
```bash
git clone git@github.com:AntonioCeppellini/zaphiro-powergrid-api.git
```

enter the repo:
```bash
cd zaphiro-powergrid-api
```

create a .env file, you can start from the example provided:
```bash
cp .env.example .env
```

run docker compose:
```bash
docker compose up --build -d
```

wait for the containers to be ready :D

once they are running you can test the backend soooo...

#### TESTING

to launch the test run:
```bash
docker compose exec app uv run pytest
```

**this could take a bit of time** that is because we have a HEAVY test
needed to validate the api properly.

#### CREATING DEV USERS

once you see that all tests passes you can launch a script to
create two dev users to test the api, you can do that launching a script:
```bash
docker compose exec app uv run python -m app.scripts.seed_users
```

this will create two users (username / password):
* manager: manager / managerpass
* user: user / userpass

#### INTERACTIVE DOCUMENTATION

to see all the endpoints and how to use them while the container is up
visit: http://localhost:8000/docs and try it out, HAVE FUN :D

### CHOICES

fastapi + postgres + sqlalchemy + alembic
