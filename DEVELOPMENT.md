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

## Updating Dependency Versions
Dependency versioning is handled by `poetry`.

To trigger an update of the dependencies run the following (ensuring you are in the `poetry` shell)

```bash
poetry update
```

This will carry out the package resolution as per the [pyproject.toml](pyproject.toml) file,
ensuring there are no package conflicts, then updating the [poetry.lock](poetry.lock) file.

Finally, to ensure that the `pre-commit` hooks are correctly updated inline with the new lock file,
run:

```bash
pre-commit run sync_with_poetry --all-files
```

This command runs a pre-commit meta-hook
([sync_with_poetry](https://github.com/floatingpurr/sync_with_poetry/tree/main)) which parses the
[poetry.lock](poetry.lock) file and updates the corresponding revisions ("rev")
in [.pre-commit-config.yaml](.pre-commit-config.yaml)

### Adding a new `pre-commit` dependency
When adding a new `pre-commit` hooks, to ensure the above dependency management tracks the new hook,
you should follow the following steps:

1. Use `poetry` to add the dependency to the "dev" group:

```bash
poetry add <pkg>@<version> --group dev
```

Where &lt;pkg&gt; is the dependency package name and &lt;version&gt; is the semantic version string.
E.g. `requests@^2.13.0`.
See [dependency specification](https://python-poetry.org/docs/dependency-specification/) for more details.

This will update the [pyproject.toml](pyproject.toml) and [poetry.lock](poetry.lock) files automatically.

2. Add the repo details for the dependency to [.poetry-pre-commit-sync.json](.poetry-pre-commit-sync.json)

This file is a reference for the `pre-commit` repositories. Add in a new block of the form:

```json
"<repo-name-in-pypi>": {
  "repo": "<repo-url>",
  "rev": "<revision-format>"
}
```

More details on the specifics of this config can be found on
the [sync_with_poetry github](https://github.com/floatingpurr/sync_with_poetry/tree/main)
