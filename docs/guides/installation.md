# Installation of pynxtools

for the latest development version.

Download the repository via git clone:
```shell
git clone https://github.com/FAIRmat-NFDI/pynxtools-raman.git
```
Switch to the project root folder:
```shell
cd pynxtools-raman
```
You see three Folders:
- examples: contains example datasets to show how the data conversion is done (currently one example from WITec and one example from the Raman Open Database)
- tests: contains a test procedure and files, which are required for software development
- src/pynxtools_raman: source files, which contain the sub-reader function for Raman experiments. This only works in combination with the Python package [pynxtools](https://github.com/FAIRmat-NFDI/pynxtools). This is a specialization of the [Multiformat Reader](https://fairmat-nfdi.github.io/pynxtools/how-tos/use-multi-format-reader.html). There are as well sub-reader functions for a WITec device and files from the [Raman Open Database](https://solsa.crystallography.net/rod/new.html?CODSESSION=f4b7fb6d2jsataebeph9qkchue). In addition, config.json files are located in src/pynxtools_raman/config. These are necessary to map the input data via the Multiformat Reader to the NeXus concepts. These config files allow individual adjustments, as different laboratories may have different electronic lab notebook structures.

Consider setting up an invididual [python environment](https://realpython.com/python-virtual-environments-a-primer/), to seperate the python fuctnionalities of this package from the python funtionalities of your operating system:
For Ubuntu-based systems:
```shell
python -m venv .pyenv
source .pyenv/bin/activate
```
Verify its location via:
```shell
which python
```
It should point to the python folder, you created above with the name `.pyenv`.


Install the python package:
```shell
pip install .
```

You then can check if pynxtools-raman is installed via:
```shell
pip list
```