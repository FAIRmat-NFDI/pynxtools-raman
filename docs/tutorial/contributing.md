# Development guide

This tutorial walks you through setting up a working environment for developing `pynxtools-raman` itself.

## Who is this tutorial for?

Anyone who wants to fix a bug, add a reader, or otherwise change the `pynxtools-raman` source code.

## What should you know before this tutorial?

- The [guide on getting started with `pynxtools`](https://fairmat-nfdi.github.io/pynxtools/getting-started.html){:target="_blank" rel="noopener"}.
- The [installation tutorial](installation.md).

## What will you know at the end of this tutorial?

- How to set up your environment for developing `pynxtools-raman`.
- How to run the tests and the linters.
- How to build the documentation locally.
- How to contribute your changes on GitHub.

??? info "Structure of the repository"
    The source code lives in `src/pynxtools_raman`, split into `reader.py` (the top-level reader dispatched by `pynxtools`), `witec/` and `rod/` (the format-specific sub-readers and the `pynx-raman` CLI), and `config/` (the JSON mapping files). Unit tests live in `tests`, mirroring that structure. `examples/` holds small example datasets used in the tutorials and in the tests.

## Setup

It is recommended to use Python 3.12 with a dedicated virtual environment. Learn how to manage [Python versions](https://github.com/pyenv/pyenv){:target="_blank" rel="noopener"} and [virtual environments](https://realpython.com/python-virtual-environments-a-primer/){:target="_blank" rel="noopener"}. We recommend [`uv`](https://github.com/astral-sh/uv){:target="_blank" rel="noopener"}; below you'll also find the equivalent `venv`/`pip` commands.

Start by creating a virtual environment:

=== "uv"
    ```bash
    uv venv --python 3.12
    ```

=== "venv"

    You need to have that Python version installed already.

    ```bash
    python -m venv .venv
    ```

### Development installation

[Fork the repository](https://github.com/FAIRmat-NFDI/pynxtools-raman/fork){:target="_blank" rel="noopener"} on GitHub, then clone your fork:

```console
git clone https://github.com/<your-username>/pynxtools-raman.git \
    --branch main \
    --recursive pynxtools-raman
cd pynxtools-raman
```

Install the package in editable mode, together with its development dependencies:

=== "uv"

    ```bash
    uv pip install -e ".[dev]"
    ```

=== "pip"

    ```bash
    pip install --upgrade pip
    pip install -e ".[dev]"
    ```

### Linting and formatting

We use `ruff` and `mypy` for linting, formatting, and type checking. Install the pre-commit hook so both run automatically before every commit:

```console
pre-commit install
```

### Testing

Tests are written with [pytest](https://docs.pytest.org/en/stable/){:target="_blank" rel="noopener"}:

```console
pytest -sv tests
```

### Editing the documentation

Documentation is built with [`mkdocs`](https://www.mkdocs.org/){:target="_blank" rel="noopener"} and the [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/){:target="_blank" rel="noopener"} theme. Install the extra dependencies for it:

=== "uv"

    ```bash
    uv pip install -e ".[docs]"
    ```

=== "pip"

    ```bash
    pip install -e ".[docs]"
    ```

Then serve the docs locally, with live reload on save:

```console
mkdocs serve
```

The config lives in `mkdocs.yaml` at the repository root; new pages need to be added to its `nav` section to show up in the sidebar.

### Contributing on GitHub

Before making changes, pull the latest `main` into your fork and branch off it (or rebase), so your pull request doesn't drag in unrelated history:

```console
git checkout main
git pull origin main
git checkout -b my-feature-branch
```

Once you're happy with your changes, commit them on that branch, push it to your fork, and open a pull request from there against `FAIRmat-NFDI/pynxtools-raman`'s `main` branch. CI runs linting, the test suite, and a documentation build; once those pass and a review has happened, your change gets merged.

## Developing `pynxtools-raman` as a NOMAD plugin

If you're working on the NOMAD integration (the [Raman app](../reference/app.md) or the metainfo schema), it's usually easiest to do that inside [`nomad-distro-dev`](https://github.com/FAIRmat-NFDI/nomad-distro-dev){:target="_blank" rel="noopener"}, NOMAD's own development distribution — see the [NOMAD documentation](https://nomad-lab.eu/prod/v1/docs/howto/develop/setup.html#nomad-distro-dev-development-environment-for-the-core-nomad-package-and-nomad-plugins){:target="_blank" rel="noopener"} for how to set it up.

## Troubleshooting

If you get stuck, open a [GitHub issue](https://github.com/FAIRmat-NFDI/pynxtools-raman/issues/new?template=bug.yaml){:target="_blank" rel="noopener"}.
