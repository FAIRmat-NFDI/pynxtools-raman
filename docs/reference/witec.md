# WITec Alpha reader

Reads `.txt` exports from WITec Alpha Raman spectrometers, combined with a separately supplied ELN file for everything the raw export doesn't carry. See [Learn > The WITec and ROD readers](../learn/readers.md#the-witec-sub-reader) for what the reader actually does with the data, and [How-to > Adjust the config file](../how-tos/adjust_the_config_file.md) for customizing the mapping.

## Supported format

| Format | Extension | Parser | Source |
| ------ | --------- | ------ | ------ |
| WITec Alpha ASCII export | `.txt` | `parse_txt_file` | `src/pynxtools_raman/witec/witec_reader.py` |

The parser reads the `[Data]` section of the export (comma-separated wavelength/intensity pairs) into `data/x_values` and `data/y_values`. The `[Header]` section is not parsed; that metadata must be supplied via the ELN file.

## Example data

An example dataset ships with the repository under [`examples/witec/txt/`](https://github.com/FAIRmat-NFDI/pynxtools-raman/tree/main/examples/witec/txt){:target="_blank" rel="noopener"}: `Si-wafer-Raman-Spectrum-1.txt` (a silicon wafer measurement) and `eln_data.yaml` (its metadata).

```console
pynx convert examples/witec/txt/eln_data.yaml examples/witec/txt/Si-wafer-Raman-Spectrum-1.txt src/pynxtools_raman/config/config_file_witec.json --reader raman --nxdl NXraman --output witec_example.nxs
```

See [Tutorial > Convert your first Raman dataset](../tutorial/convert_your_first_dataset.md) for a walkthrough of this exact command.

## Config file

[`config_file_witec.json`](https://github.com/FAIRmat-NFDI/pynxtools-raman/blob/main/src/pynxtools_raman/config/config_file_witec.json){:target="_blank" rel="noopener"} maps almost every `NXraman` concept to `"@eln"` — meaning the value comes directly from the ELN file you supply, at the path derived from the NeXus concept path itself (see [Learn > Reader architecture](../learn/architecture.md#config-file-values-select-where-the-data-comes-from)). The exceptions are the spectrum data (`data/x_values`, `data/x_values_raman`, `data/y_values`), which come from the parsed `.txt` file, and the Raman shift axis, which the reader computes rather than reading directly (see [Learn > The WITec and ROD readers](../learn/readers.md#the-witec-sub-reader)).

## Known warnings

Converting the shipped example currently produces a few benign warnings — values that don't exactly match one of `NXraman`'s open enumerations (the source type `laser`, for instance) and a missing unit-documentation note for `beam_incident/wavelength`. None of these stop the conversion; the values are still written correctly, with `custom=True` added automatically where an enum doesn't match exactly.
