[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
![](https://github.com/FAIRmat-NFDI/pynxtools-raman/actions/workflows/pytest.yml/badge.svg)
![](https://github.com/FAIRmat-NFDI/pynxtools-raman/actions/workflows/pylint.yml/badge.svg)
![](https://github.com/FAIRmat-NFDI/pynxtools-raman/actions/workflows/publish.yml/badge.svg)
![](https://img.shields.io/pypi/pyversions/pynxtools-raman)
![](https://img.shields.io/pypi/l/pynxtools-raman)
![](https://img.shields.io/pypi/v/pynxtools-raman)
![](https://coveralls.io/repos/github/FAIRmat-NFDI/pynxtools_raman/badge.svg?branch=main)

# A reader for raman data

## Installation

It is recommended to use python 3.11 with a dedicated virtual environment for this package.
Learn how to manage [python versions](https://github.com/pyenv/pyenv) and
[virtual environments](https://realpython.com/python-virtual-environments-a-primer/).

This package is a reader plugin for [`pynxtools`](https://github.com/FAIRmat-NFDI/pynxtools) and thus should be installed together with `pynxtools`:


```shell
pip install pynxtools[raman]
```

for the latest development version.

## Purpose
This reader plugin for [`pynxtools`](https://github.com/FAIRmat-NFDI/pynxtools) is used to translate diverse file formats from the scientific community and technology partners
within the field of raman into a standardized representation using the
[NeXus](https://www.nexusformat.org/) application definition [NXraman](https://fairmat-nfdi.github.io/nexus_definitions/classes/contributed_definitions/NXraman.html#nxraman).

## Docs
Extensive documentation of this pynxtools plugin is available [here](https://fairmat-nfdi.github.io/pynxtools-raman/). You can find information about getting started, how-to guides, the supported file formats, how to get involved, and much more there.


## Contact person in FAIRmat for this reader
Ron Hildebrandt
