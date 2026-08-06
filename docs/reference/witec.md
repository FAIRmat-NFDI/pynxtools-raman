# WITec Alpha reader

Reads `.txt` exports from WITec Alpha Raman spectrometers, combined with a separately supplied ELN file for the instrument/sample/user metadata the raw export doesn't carry. See [Learn > The WITec and ROD parsers](../learn/readers.md#the-witec-parser) for what the parser actually does with the data, and [How-to > Adjust the config file](../how-tos/adjust_the_config_file.md) for customizing the mapping.

## Supported format

| Format | Extension | Parser | Source |
| ------ | --------- | ------ | ------ |
| WITec Alpha ASCII export | `.txt` | `WitecParser` | `src/pynxtools_raman/parsers/witec.py` |

The parser reads the `[Data]` section of the export (comma-separated wavelength/intensity pairs) into `data/x_values` and `data/y_values`, and the `[Header]` section into scalar metadata (`XAxisUnit`, `DataUnit`, `PositionX`/`Y`/`Z`, `FileName`, `GraphName`, `SizeX`/`Y`/`Graph`, ...). `XAxisUnit` and `DataUnit` are mapped directly onto the data axes' `@units` attributes (see [Config file](#config-file) below); the rest currently has no `NXraman` home and lands in `COLLECTION[unused_witec_keys]`, same treatment as unmapped ROD CIF keys get — not dropped, just not (yet) structured.

## Example data

An example dataset ships with the repository under [`examples/witec/txt/`](https://github.com/FAIRmat-NFDI/pynxtools-raman/tree/main/examples/witec/txt){:target="_blank" rel="noopener"}: `Si-wafer-Raman-Spectrum-1.txt` (a silicon wafer measurement) and `eln_data.yaml` (its metadata).

```console
pynx convert examples/witec/txt/eln_data.yaml examples/witec/txt/Si-wafer-Raman-Spectrum-1.txt src/pynxtools_raman/config/config_file_witec.json --reader raman --nxdl NXraman --output witec_example.nxs
```

See [Tutorial > Convert your first Raman dataset](../tutorial/convert_your_first_dataset.md) for a walkthrough of this exact command.

## Config file

[`config_file_witec.json`](https://github.com/FAIRmat-NFDI/pynxtools-raman/blob/main/src/pynxtools_raman/config/config_file_witec.json){:target="_blank" rel="noopener"} maps most `NXraman` concepts to `"@eln"` — meaning the value comes directly from the ELN file you supply, at the path derived from the NeXus concept path itself (see [Learn > Reader architecture](../learn/architecture.md#config-file-values-select-where-the-data-comes-from)). The exceptions: the spectrum data (`data/x_values`, `data/x_values_raman`, `data/y_values`) and the two axis `@units` (`@attrs:XAxisUnit`, `@attrs:DataUnit`) come from the parsed `.txt` file rather than the ELN, and the Raman shift axis is computed by the parser rather than read directly from either source (see [Learn > The WITec and ROD parsers](../learn/readers.md#the-witec-parser)).

## Known warnings

Converting the shipped example currently produces a few benign warnings — values that don't exactly match one of `NXraman`'s open enumerations (the source type `laser`, for instance) and a missing unit-documentation note for `beam_incident/wavelength`. None of these stop the conversion; the values are still written correctly, with `custom=True` added automatically where an enum doesn't match exactly.
