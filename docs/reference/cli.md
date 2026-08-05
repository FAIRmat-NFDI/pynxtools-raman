# Command line interface

`pynxtools-raman` provides its command-line tools under a single `pynx-raman` entry point, mirroring the top-level [`pynx` dispatcher](https://fairmat-nfdi.github.io/pynxtools/reference/cli-api.html){:target="_blank" rel="noopener"} of `pynxtools` itself. This page documents the current API; see [How-to > Build a NOMAD upload batch from the Raman Open Database](../how-tos/build_a_rod_upload_batch.md) for usage examples.

The generic `pynx convert` command (provided by `pynxtools`, not by this package) is what actually performs a conversion — see [How-to > Convert WITec or ROD data](../how-tos/convert_data.md) and the [`pynxtools` CLI reference](https://fairmat-nfdi.github.io/pynxtools/reference/cli-api.html#data-conversion-pynx-convert){:target="_blank" rel="noopener"}.

## Download ROD files

Downloads a batch of `.rod` files from the Raman Open Database.

::: mkdocs-click
    :module: pynxtools_raman.rod.rod_batch
    :command: download_rod_files_cli
    :prog_name: pynx-raman download
    :depth: 2
    :style: table

## Build a NOMAD upload batch for ROD files

Downloads, converts, and stamps a batch of Raman Open Database records with NOMAD upload metadata in one step — see [Learn > The Raman Open Database in NOMAD](../learn/rod_database_in_nomad.md).

::: mkdocs-click
    :module: pynxtools_raman.rod.rod_batch
    :command: build_rod_upload_batch
    :prog_name: pynx-raman build-upload-batch
    :depth: 2
    :style: table

## Analyze CIF keys in ROD files

Counts how often each CIF key occurs across a directory of `.rod` files — useful when deciding what to add to [`config_file_rod.json`](rod.md).

::: mkdocs-click
    :module: pynxtools_raman.rod.rod_stats
    :command: analyze_rod_keys
    :prog_name: pynx-raman analyze-keys
    :depth: 2
    :style: table
