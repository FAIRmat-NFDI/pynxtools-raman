# Convert WITec or ROD data from the command line

This is the terse reference version of [Tutorial > Convert your first Raman dataset](../tutorial/convert_your_first_dataset.md) — copy-paste commands, no explanations.

## WITec Alpha `.txt` export + ELN

```shell
pynx convert examples/witec/txt/eln_data.yaml examples/witec/txt/Si-wafer-Raman-Spectrum-1.txt src/pynxtools_raman/config/config_file_witec.json --reader raman --nxdl NXraman --output witec_example.nxs
```

## A single Raman Open Database `.rod` file

```shell
pynx convert examples/database/rod/rod_file_1000679.rod src/pynxtools_raman/config/config_file_rod.json --reader raman --nxdl NXraman --output rod_example.nxs
```

No ELN file is needed here — `.rod` files already carry their own metadata, and the reader picks `config_file_rod.json` automatically once it sees a `.rod` input (passing the config file explicitly, as above, still works and is harmless).

## What each flag does

- `--reader raman` — selects the `pynxtools-raman` reader.
- `--nxdl NXraman` — the application definition the output should conform to.
- `--output <file>.nxs` — where to write the result.
- the `.json` file — the [config file](../learn/architecture.md#the-config-file) that maps input data onto `NXraman` concepts. Detected by its `.json` extension.
- the `.txt`/`.rod`/`.yaml` files — raw data and (for WITec) the ELN file, detected by their extensions.

## Converting many `.rod` files at once

For batches of ROD records — and for preparing a NOMAD upload out of them — use `pynx-raman build-upload-batch` instead of calling `pynx convert` in a loop; see [How-to > Build a NOMAD upload batch from the Raman Open Database](build_a_rod_upload_batch.md).

## Inspect the result

Open the generated `.nxs` file with [H5Web](https://h5web.panosc.eu/h5wasm){:target="_blank" rel="noopener"}, the VS Code H5Web extension, or any HDF5 viewer.
