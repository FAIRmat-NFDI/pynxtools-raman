# Raman Open Database reader

Reads `.rod` files — CIF-formatted records from the [Raman Open Database (ROD)](https://solsa.crystallography.net/rod/){:target="_blank" rel="noopener"}. No separate ELN file is needed: a `.rod` file carries both the spectrum and its metadata. See [Learn > The WITec and ROD parsers](../learn/readers.md#the-rod-parser) for what the parser does with the data, and [How-to > Build a NOMAD upload batch from the Raman Open Database](../how-tos/build_a_rod_upload_batch.md) for downloading and converting many records at once.

## Supported format

| Format | Extension | Parser | Source |
| ------ | --------- | ------ | ------ |
| Raman Open Database record (CIF) | `.rod` | `RodParser` (via [`gemmi`](https://gemmi.readthedocs.io/){:target="_blank" rel="noopener"}) | `src/pynxtools_raman/parsers/rod.py` |

## Example data

[`examples/database/rod/rod_file_1000679.rod`](https://github.com/FAIRmat-NFDI/pynxtools-raman/blob/main/examples/database/rod/rod_file_1000679.rod){:target="_blank" rel="noopener"} — a K-cymrite spectrum — ships with the repository.

```console
pynx convert examples/database/rod/rod_file_1000679.rod src/pynxtools_raman/config/config_file_rod.json --reader raman --nxdl NXraman --output rod_example.nxs
```

## Config file mapping

[`config_file_rod.json`](https://github.com/FAIRmat-NFDI/pynxtools-raman/blob/main/src/pynxtools_raman/config/config_file_rod.json){:target="_blank" rel="noopener"} maps most of the CIF keys onto `NXraman` concepts. Also see [Learn > The WITec and ROD parsers](../learn/readers.md#the-rod-parser) for a more detailed description, and [Learn > Reader architecture](../learn/architecture.md#config-file-values-select-where-the-data-comes-from) for understanding the config file.

Any CIF key present in a `.rod` file that cannot be matched to a NeXus concept ends up in `COLLECTION[unused_rod_keys]` in the output file — not dropped, just not (yet) structured. Run [`pynx-raman analyze-keys`](cli.md#pynx-raman-analyze-keys) over a batch of downloaded records to see which unmapped keys are common enough to be worth adding here.

## Known warnings

Some fields legitimately don't apply to every record — a mineral without a COD cross-reference has no `_cod_database_code`, for instance — which produces a `No axis name corresponding to the path ...` warning for that field. This is expected and doesn't indicate a mapping problem; it means the underlying `.rod` file simply doesn't carry that piece of data. Similarly, several fields (`raman_experiment_type`, `objective_lens/type`, `source_532nmlaser/type`) are written from open-ended CIF text that doesn't always match `NXraman`'s enumerated values exactly; the converter adds `custom=True` automatically in that case.
