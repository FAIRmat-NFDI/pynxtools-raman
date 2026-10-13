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
- Which branch to use for which kind of change.
- How to contribute your changes on GitHub.
- How a new version is released.

??? info "Structure of the repository"
    The source code lives in `src/pynxtools_raman`, split into `reader.py` (the top-level reader dispatched by `pynxtools`), `parsers/` (the parser classes and their shared base), `rod_database/` (the `pynx-raman` CLI for downloading and batch-converting Raman Open Database records — not to be confused with `parsers/rod.py`, the single-file `.rod` parser), and `config/` (the JSON mapping files). Unit tests live in `tests`, mirroring that structure. `examples/` holds small example datasets used in the tutorials and in the tests.

## Branching model

`pynxtools-raman` follows the same branching model as the core NOMAD packages.

| Branch | Role |
|---|---|
| `develop` | Default branch. All regular development PRs target this branch. |
| `main` | Released versions only. Only `release/*` branches are merged here, so its history is the release history. |
| `release/vX.Y.Z` | Temporary release branch, created from `develop` and merged into `main`. The version may carry a pre-release suffix, e.g. `release/vX.Y.Z-beta` or `release/vX.Y.Z-rc1`. |

| Activity | Branch |
|---|---|
| Feature development | `develop` |
| PR review and integration | `develop` |
| Selecting changes for a release | `release/vX.Y.Z` |
| Release-specific bug fixes | `release/vX.Y.Z` |
| Published release history | `main` |
| Porting release fixes back to ongoing development | Merge `release/vX.Y.Z` back into `develop` |

The `Check if source is release/*` workflow
([`.github/workflows/check-source-is-release.yml`](https://github.com/FAIRmat-NFDI/pynxtools-raman/blob/develop/.github/workflows/check-source-is-release.yml))
allows PRs into `main` only from `release/*` branches. PRs from any other branch, **including `develop`**,
fail this check. It is enforced by marking it as a required status check in the branch protection rule
for `main`.

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
    --branch develop \
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

Before making changes, pull the latest `develop` into your fork and branch off it (or rebase), so your pull request doesn't drag in unrelated history:

```console
git checkout develop
git pull origin develop
git checkout -b my-feature-branch
```

Once you're happy with your changes, commit them on that branch, push it to your fork, and open a pull request from there against `FAIRmat-NFDI/pynxtools-raman`'s `develop` branch. Never open a pull request against `main`: it receives only `release/*` branches. CI runs linting, the test suite, and a documentation build; once those pass and a review has happened, your change gets merged.

## Release workflow

1. Create the release branch from `develop`:

    ```console
    git switch develop && git pull
    git switch -c release/vX.Y.Z
    git push -u origin release/vX.Y.Z
    ```

1. Commit only release-specific changes on this branch (version bumps, changelog, last-minute bug fixes). New features keep going into `develop`.
1. Bump `version` in `CITATION.cff` to `X.Y.Z`, including any pre-release suffix (e.g. `0.1.2-rc1` for the tag `v0.1.2-rc1`). The publish workflow fails if it differs from the tag.
1. Open a PR from `release/vX.Y.Z` into `main`. Do not merge yet!
1. Create a GitHub release with the tag `vX.Y.Z` and select `release/vX.Y.Z` as its target branch. The publish workflow refuses to upload to PyPI if the release does not target `release/vX.Y.Z` or if the tagged commit is not on that branch.
1. Once CI passes and the release is published to PyPI, merge the PR.
1. If you fixed anything directly on the release branch, open a PR from `release/vX.Y.Z` into `develop` so the fixes are not lost in ongoing development.
1. Delete the `release/vX.Y.Z` branch.

## Developing `pynxtools-raman` as a NOMAD plugin

If you're working on the NOMAD integration (the [Raman app](../reference/app.md) or the metainfo schema), it's usually easiest to do that inside [`nomad-distro-dev`](https://github.com/FAIRmat-NFDI/nomad-distro-dev){:target="_blank" rel="noopener"}, NOMAD's own development distribution — see the [NOMAD documentation](https://nomad-lab.eu/prod/v1/docs/howto/develop/setup.html#nomad-distro-dev-development-environment-for-the-core-nomad-package-and-nomad-plugins){:target="_blank" rel="noopener"} for how to set it up.

## Troubleshooting

If you get stuck, open a [GitHub issue](https://github.com/FAIRmat-NFDI/pynxtools-raman/issues/new?template=bug.yaml){:target="_blank" rel="noopener"}.
