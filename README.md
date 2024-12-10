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

## Use Example via GitHub
Download(clone) the repository via git:
```shell
git clone https://github.com/FAIRmat-NFDI/pynxtools-raman.git
```
Switch to the project root folder:
```shell
cd pynxtools-raman
```
You see 3 Folders:
- examples: contains example datasets, to show how the data conversion is done (currently 1 example from WITec and 1 example from the Raman Open Database)
- tests: contains a test procedure and files, which are required for software development
- src/pynxtools_raman: contains the source files, which contain the sub-reader function for Raman experiments. This only works in combination with the python package [pynxtools](https://github.com/FAIRmat-NFDI/pynxtools). This contains the [Multiformat Reader](https://fairmat-nfdi.github.io/pynxtools/how-tos/use-multi-format-reader.html) and the respective sub-reader functions for WITec or Raman Open Database. This also contains the config.json files in src/pynxtools_raman/config, which are necessary to map the data via the Multiformat Reader, by as well allowing individual adjustments. In this way each laboratory is able to map the data via the same reader, while each laboratory has its own individual electronic lab notebook structure.

Install the python package:
```shell
pip install .
```
**Perform a dataconversion**
for the WITec dataset via:
```shell
dataconverter examples/witec/txt/eln_data.yaml examples/witec/txt/Si-wafer-Raman-Spectrum-1.txt src/pynxtools_raman/config/config_file_witec.json --reader raman --nxdl NXraman --output new_witec_example_neuxs.nxs
```

and for the Raman Open Database dataset set via:
```shell
dataconverter examples/database/rod/rod_file_1000679.rod src/pynxtools_raman/config/config_file_rod.json --reader raman --nxdl NXraman --output new_rod_example_neuxs.nxs
```

**For Example for the Raman Open Database command:**
- You assign the reader name via `--reader raman`
- You assign the NeXus definition language (nxdl) via `--nxdl NXraman`
- You specify the name and path of the output file via `--output new_rod_example_neuxs.nxs`
- You assign an indiviualized config file via `src/pynxtools_raman/config/config_file_rod.json`. The config file is detected by its extension `.json`
- You give the file, which includes the meta and measurement data via `examples/database/rod/rod_file_1000679.rod`. The parser is specificed to detect the `.rod` file, and handle the content appropiately


## Contact person in FAIRmat for this reader
Ron Hildebrandt
