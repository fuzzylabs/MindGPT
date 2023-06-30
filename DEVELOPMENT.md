# Developer Readme

This document contains documentation intended for developers of MindGPT.

## Developer environment setup

In order to work on the tool as a developer, you'll need to configure your local development environment.

**Pre-requisites**

* Python.
* [Poetry](https://python-poetry.org/).
* [PyEnv](https://github.com/pyenv/pyenv).

**Setup**

First, use PyEnv to install the recommended version of Python:

```bash
pyenv install 3.10.5
pyenv local 3.10.5
```

Next, set up Poetry:

```bash
poetry env use 3.10.5
poetry install
```

Now, you can enter the Poetry shell:

```bash
poetry shell
```

**Pre-commit checks**

Install the git hook scripts

```bash
pre-commit install
```

> The pre-commit checks will run automatically on the changed files after committing files using `git commit` command.

Optionally, to run the hooks against all of the files, run the following command.

```bash
pre-commit run --all-files
```
