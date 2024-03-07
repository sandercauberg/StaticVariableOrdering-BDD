# StaticVariableOrdering-BDD

Static Variable Ordering BDD Compilation repository.

## Development setup

### Requirements

- At least python 3.11 (pyenv managed recommended)

### Install the project
```bash
pyenv virtualenv 3.11 StaticVariableOrdering-BDD  # or your alternative to create a venv
pyenv activate StaticVariableOrdering-BDD
make install
```

### Linting
`flake8-black` and `flake8-isort` are installed and configured
```bash
make lint
```

### Formatting

`black` and `isort` are configured
```bash
make format
```

### Test

Pytest with coverage is default enabled
```bash
make test
```

### Run the application

Finally run the application:
```bash
make run
```