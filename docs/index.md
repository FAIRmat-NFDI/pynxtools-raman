---
hide: toc
---

# Documentation for pynxtools-raman

`pynxtools-raman` is a free, open-source data converter for Raman spectroscopy using [NeXus](https://www.nexusformat.org/). It reads Raman data and metadata from different instrument and database formats and writes standardized
[`NXraman`](https://fairmat-nfdi.github.io/nexus_definitions/classes/applications/NXraman.html){:target="_blank" rel="noopener"}
files, an extension of [`NXoptical_spectroscopy`](https://fairmat-nfdi.github.io/nexus_definitions/classes/applications/NXoptical_spectroscopy.html){:target="_blank" rel="noopener"}, making Raman data FAIR (findable, accessible, interoperable, and reusable).
It works both as a standalone command-line converter and as a plugin for
[NOMAD](https://nomad-lab.eu/){:target="_blank" rel="noopener"}, the open-source research data management platform we develop with [FAIRmat](https://www.fairmat-nfdi.eu/fairmat/).

As of this writing, `pynxtools-raman` reads two kinds of input:

- **WITec Alpha** `.txt` exports, combined with an electronic lab notebook (ELN) file that supplies the metadata the raw export doesn't carry.
- **`.rod` files** from the [Raman Open Database (ROD)](https://solsa.crystallography.net/rod/){:target="_blank" rel="noopener"}, a public, CC0-licensed collection of reference Raman spectra for minerals and crystalline materials.

<div markdown="block" class="home-grid">
<div markdown="block">

### Tutorial

Hands-on tutorials: install the package, convert your first dataset, and development guidelines.

- [Installation guide](tutorial/installation.md)
- [Convert your first Raman dataset](tutorial/convert_your_first_dataset.md)
- [Development guide](tutorial/contributing.md)

</div>
<div markdown="block">

### How-to guides

Step-by-step recipes for specific tasks.

- [Convert WITec or ROD data from the command line](how-tos/convert_data.md)
- [Adjust the config file for your own instrument](how-tos/adjust_the_config_file.md)
- [Build a NOMAD upload batch from the Raman Open Database](how-tos/build_a_rod_upload_batch.md)
- [Search Raman data in NOMAD](how-tos/search_raman_data_in_nomad.md)

</div>
<div markdown="block">

### Learn

Background on how `pynxtools-raman` is built.

- [NXoptical_spectroscopy and NXraman](learn/application_definitions.md)
- [Reader architecture](learn/architecture.md)
- [The WITec and ROD readers](learn/readers.md)
- [NOMAD integration](learn/nomad_integration.md)
- [The Raman Open Database in NOMAD](learn/rod_database_in_nomad.md)
- [Note on versioning](learn/versioning.md)

</div>
<div markdown="block">

### Reference

References for command-line options, supported fields, and what the NOMAD app shows.

- [Command line interface](reference/cli.md)
- [WITec Alpha reader](reference/witec.md)
- [Raman Open Database reader](reference/rod.md)
- [Raman NOMAD app](reference/app.md)

</div>
</div>

<h2> Contact </h2>

For questions or suggestions:

- Open an issue on the [`pynxtools-raman` GitHub](https://github.com/FAIRmat-NFDI/pynxtools-raman/issues){:target="_blank" rel="noopener"}
- Join our [Discord channel](https://discord.gg/Gyzx3ukUw8){:target="_blank" rel="noopener"}
- Get in contact with our [lead developers](contact.md).

<h2>Project and community</h2>

- [NOMAD code guidelines](https://nomad-lab.eu/prod/v1/docs/reference/code_guidelines.html){:target="_blank" rel="noopener"}

[The work is funded by the Deutsche Forschungsgemeinschaft (DFG, German Research Foundation) - 460197019 (FAIRmat).](https://gepris.dfg.de/gepris/projekt/460197019?language=en){:target="_blank" rel="noopener"}
