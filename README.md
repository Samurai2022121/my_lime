## Development

Add any principal (top-level) dependency to `requirements.in` file.

Before committing your changes, issue a command `pip-compile` to update
`requirements.txt`.

```shell
$ pip-compile requirements.in
```

## Code style

We use the following tools to maintain code style:
black - code formatter  
flake8 - code style enforcer  
isort - to keep imports sorted  
pre-commit - to manager pre-commit hooks  

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
