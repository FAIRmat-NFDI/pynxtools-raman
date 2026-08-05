# Installation guide

## Who is this tutorial for?

Anyone who wants to convert Raman data to NeXus, either from the command line or as part of a NOMAD installation.

## What should you know before this tutorial?

It doesn't hurt to skim the `pynxtools` tutorials first:

- [Guide on getting started with `pynxtools`, NeXus, and NOMAD](https://fairmat-nfdi.github.io/pynxtools/getting-started.html){:target="_blank" rel="noopener"}
- [Installation tutorial for `pynxtools`](https://fairmat-nfdi.github.io/pynxtools/tutorial/installation.html){:target="_blank" rel="noopener"}

## What will you know at the end of this tutorial?

- How to install `pynxtools-raman` on its own.
- How to install it together with NOMAD.

## Setup

It is recommended to use Python 3.12 with a dedicated virtual environment for this package. Learn how to manage [Python versions](https://github.com/pyenv/pyenv){:target="_blank" rel="noopener"} and [virtual environments](https://realpython.com/python-virtual-environments-a-primer/){:target="_blank" rel="noopener"}.

We recommend using [`uv`](https://github.com/astral-sh/uv){:target="_blank" rel="noopener"}, an extremely fast Python package and project manager. Below you'll find the equivalent commands for `uv` and for the more classical `venv`/`pip` combination.

Start by creating a virtual environment:

=== "uv"
    `uv` can create the virtual environment and install the required Python version in one go.

    ```bash
    uv venv --python 3.12
    ```

=== "venv"

    Note that you will need to install the Python version manually beforehand.

    ```bash
    python -m venv .venv
    ```

That command creates a new virtual environment in a directory called `.venv`.

## Installation

Install the latest stable release from PyPI:

=== "uv"

    ```bash
    uv pip install pynxtools-raman
    ```

=== "pip"

    ```bash
    pip install pynxtools-raman
    ```

Alternatively, since `pynxtools-raman` is a `pynxtools` reader plugin, you can pull it in as an extra of `pynxtools` itself:

```bash
uv pip install pynxtools[raman]
```

Both commands install the same package; use whichever fits how you're already installing `pynxtools`.

To install the latest _development_ version instead:

=== "uv"

    ```bash
    uv pip install git+https://github.com/FAIRmat-NFDI/pynxtools-raman.git
    ```

=== "pip"

    ```bash
    pip install git+https://github.com/FAIRmat-NFDI/pynxtools-raman.git
    ```

### Installing `pynxtools-raman` with NOMAD

To use `pynxtools-raman` inside NOMAD, install it into the same Python environment as `nomad-lab`. NOMAD picks up `pynxtools-raman` automatically as a plugin: it registers the `NXraman` reader, the [Raman NOMAD app](../reference/app.md), and the metainfo schema for the application definition.

## Verify the installation

Two console scripts should now be available:

```bash
pynx convert --help      # the generic pynxtools data converter (provided by pynxtools)
pynx-raman --help        # pynxtools-raman's own command line tools
```

If both print usage information without errors, you're set up correctly.

## Next steps

Continue with [Convert your first Raman dataset](convert_your_first_dataset.md) to see the converter in action.
