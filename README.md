## System requirements

- Python 3.10+
- Redis
- PostgreSQL
- Xapian 1.4
- Nginx

## Configuration

Add `.env` file to the base directory. It will be sourced by Django `settings` app.

Available settings are:

| Name                     | Type | Meaning                                                                                                   |
|--------------------------|------|-----------------------------------------------------------------------------------------------------------|
| SECRET_KEY               | str  | Django secret key                                                                                         |
| DEBUG                    | bool | Allow debugging                                                                                           |
| LOGURU_DIAGNOSE          | bool | [Show values in stack trace](https://loguru.readthedocs.io/en/stable/api/logger.html)                     |
| ALLOWED_HOSTS            | list | A list of hosts Django is allowed to serve                                                                |
| SENTRY_KEY               | str  | [Sentry API key](https://sentry.thefresh.by/fresh/settings/projects/lime)                                 |
| SENTRY_PROJECT           | str  | [Sentry project ID](https://sentry.thefresh.by/fresh/settings/projects/lime)                              |
| ENVIRONMENT              | str  | Environment tag for Sentry (‘Production’, ‘Staging’, or ‘Testing’)                                        |
| DB_NAME                  | str  | Default database name                                                                                     |
| DB_USER                  | str  | Default database user's name                                                                              |
| DB_PASSWORD              | str  | Default database user's password                                                                          |
| DB_HOST                  | str  | Default database host                                                                                     |
| DB_PORT                  | int  | Default database port                                                                                     |
| RF_AUTH_CLASSES          | list | A list of [DRF's authentication classes](https://www.django-rest-framework.org/api-guide/authentication/) |
| CELERY_BROKER_URL        | str  | Celery broker URL (only Redis is supported)                                                               |
| CELERY_TASK_ALWAYS_EAGER | bool | Synchronous mode switch. May be useful in debugging.                                                      |

## Development

Add any principal (top-level) dependency to `requirements.in` file.

Before committing your changes, issue a command `pip-compile` to update
`requirements.txt`.

```shell
$ pip-compile requirements.in
```

## Code style

We use the following tools to maintain code style:  

**black** – code formatter  
**flake8** – code style enforcer  
**isort** – to keep imports sorted  
**pre-commit** – to manage pre-commit hooks  

To install pre-commit hooks to your local repository, run:

```shell
$ pre-commit install
$ pre-commit run --all-files
```

## Installation

To reproduce the environment on testing or deployment stage, do

```shell
$ pip install -r requirements.txt
```

## Testing

```shell
$ pytest
```
