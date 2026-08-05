# Raman NOMAD app

`pynxtools-raman` registers a NOMAD app, defined in `src/pynxtools_raman/nomad/apps/__init__.py`. See [Learn > NOMAD integration](../learn/nomad_integration.md) for how it fits into NOMAD's generic NeXus parsing, and [How-to > Search Raman data in NOMAD](../how-tos/search_raman_data_in_nomad.md) for a walkthrough of using it.

| | |
| --- | --- |
| Label | Raman |
| URL path | `ramanapp` |
| Category | Experiment |
| Locked filter | `NXentry/definition` = `NXraman` |

## Result table columns

- Entry ID
- Material name (`SAMPLE/name`)
- Space group number (`SAMPLE/space_group`)
- Unit cell volume (`SAMPLE/unit_cell_volume`)
- Long name (`ENTRY/title`)

## Side menu filters

| Section | Filters |
| ------- | ------- |
| Elements | Periodic table, Hill/IUPAC/reduced/anonymous chemical formula, number-of-elements histogram (from NOMAD's `results.material`) |
| Space Group Number | `SAMPLE/space_group` |
| Raman Spectrometer Model | `INSTRUMENT/device_information/model` |
| Scattering Configuration | `INSTRUMENT/scattering_configuration` |
| Instruments | Name, short name |
| Samples | Name, sample ID |
| Authors / Origin | Entry author, NOMAD upload author, affiliation |

Plus histograms of entry start time and upload creation time.

## Default dashboard

Histograms of incident wavelength, laser power, objective magnification, numerical aperture, and beam diameter, across the entries matching the current filters.
