# Reader architecture

`pynxtools-raman` is a `pynxtools` reader plugin. This page explains how it's put together — the shared reader dispatch, and the config-file mechanism that maps input data onto `NXraman` concepts. It assumes you're already roughly familiar with `pynxtools` itself; the [`pynxtools` multi-format reader documentation](https://fairmat-nfdi.github.io/pynxtools/learn/multi-format-reader.html){:target="_blank" rel="noopener"} covers the parts that are generic to all `pynxtools` plugins, not specific to Raman.

## One reader, dispatched by file extension

`pynxtools-raman` registers a single reader, `RamanReader`, as the `raman` entry point for `pynxtools`. It's built on `pynxtools`'s [`MultiFormatReader`](https://fairmat-nfdi.github.io/pynxtools/how-tos/use-multi-format-reader.html){:target="_blank" rel="noopener"}, which routes each input file to a handler based on its extension:

| Extension | Handler | What it does |
| --------- | ------- | ------------- |
| `.rod` | `handle_rod_file` | Parses a Raman Open Database record (see [The WITec and ROD parsers](readers.md#the-rod-parser)). |
| `.txt` | `handle_txt_file` | Parses a WITec Alpha export (see [The WITec and ROD parsers](readers.md#the-witec-parser)). |
| `.yaml` / `.yml` | `handle_eln_file` | Loads an ELN metadata file. |
| `.json` | `set_config_file` | Registers the config file for this conversion. |

You don't select a parser explicitly — you just pass files with the right extensions to `pynx convert`, and `RamanReader` figures out what each one is for. `.rod` and `.txt` are mutually exclusive in practice: a `.rod` file already carries its own metadata and doesn't need an ELN file, while a `.txt` (WITec) conversion needs one to supply everything the raw export doesn't.

Both `.rod` and `.txt` handlers set a default config file for their format (`config_file_rod.json` or `config_file_witec.json`, both under `src/pynxtools_raman/config/`), so you don't have to pass one explicitly unless you want to override it.

## The config file

The config file is a flat JSON dictionary. Each key is a NeXus concept path; each value tells the converter where to get the data for that path from.

```json
{
  "/ENTRY[entry]/INSTRUMENT[instrument]/beam_incident/wavelength": "@eln",
  "/ENTRY[entry]/INSTRUMENT[instrument]/beam_incident/wavelength/@units": "nm"
}
```

### Config file keys are NeXus paths

A key like `/ENTRY[entry]/INSTRUMENT[instrument]/beam_incident/wavelength` is read segment by segment:

- `ENTRY[entry]` — creates a group named `entry`, tagged `NX_class=NXentry` (the uppercase word before the brackets is the NeXus base class, minus its `NX` prefix).
- `INSTRUMENT[instrument]` — inside `entry`, a group named `instrument`, tagged `NXinstrument`.
- `beam_incident` — no brackets, so the converter looks up what class this concept has in the application definition being used (`NXraman`, which says `beam_incident` is an `NXbeam`) rather than requiring you to spell it out.
- `wavelength` — a field inside `beam_incident`.

A trailing `/@name` segment sets an attribute instead of a field — e.g. `.../wavelength/@units` sets the `units` attribute on the `wavelength` field.

### Config file values select where the data comes from

A value has the form `@<PREFIX>:<PATH>`, where `<PREFIX>` is `eln`, `attrs`, `data`, or omitted entirely:

- `@eln:<PATH>` calls `RamanReader.get_eln_data`, which looks `<PATH>` up in the parsed ELN file.
- `@attrs:<PATH>` calls `RamanReader.get_attr`, which looks `<PATH>` up in the active parser's scalar metadata — instrument settings, sample information, computed values that aren't the spectrum itself. This is what most of `config_file_rod.json` uses, since almost everything a `.rod` file carries (unit cell dimensions, instrument fields, citations, ...) is metadata *about* the measurement, not the measurement itself.
- `@data:<PATH>` calls `RamanReader.get_data`, which looks `<PATH>` up in the active parser's measurement data — the spectrum arrays themselves (intensity, Raman shift, WITec's x/y columns). Only a handful of keys in either config file use this: the actual `NXdata` fields.
- A bare literal value (no `@` prefix at all), e.g. `"nm"` or `532`, is written as-is — no lookup happens.

If `<PATH>` is omitted (just `"@eln"`, `"@attrs"`, or `"@data"`), the converter derives it automatically from the key: it strips the uppercase class names and the `[...]` brackets, so `/ENTRY[entry]/INSTRUMENT[instrument]/beam_incident/wavelength` becomes the path `entry/instrument/beam_incident/wavelength`. This works whenever your ELN file (or a parser's `attrs`/`data`) already mirrors the NeXus structure — which is the common case, and why most keys in `config_file_witec.json` are just `"@eln"` with no explicit path.

### Fallback lists

A value can also be a JSON-encoded list of `@`-prefixed candidates, tried in order until one resolves to something non-empty:

```json
"/ENTRY[entry]/SAMPLE[sample]/name": "['@attrs:_chemical_name_mineral','@attrs:_chemical_name_systematic']"
```

`config_file_rod.json` uses this for fields that different Raman Open Database records populate differently — see [How-to > Adjust the config file](../how-tos/adjust_the_config_file.md#add-a-fallback-chain-for-a-field-that-comes-from-different-sources-depending-on-the-record).

## Parser classes

`.rod` and `.txt` files are each parsed by a small class — `RodParser` and `WitecParser` — that both subclass a shared internal base, `_RamanParser` (`src/pynxtools_raman/parsers/base.py`). Each parser implements:

- `matches_file(file)` — a cheap structural check (not just an extension check) that a given file actually looks like this parser's format. `RamanReader` calls this before parsing, so a `.txt` file that isn't actually a WITec export gets skipped with a warning rather than mis-parsed.
- `_parse(file)` — populates two dicts: `attrs` (scalar metadata, backing `@attrs:`) and `data` (measurement arrays, backing `@data:`).
- `post_process(eln_data)` — derives fields that need context only available after all input files (including the ELN) have been read; see below.

`RamanReader` doesn't know the details of either format. It just instantiates the parser matching the file extension, calls `.parse()`, and exposes the result through `get_attr`/`get_data`. Any `attrs` entry not referenced by the config file is written into a `COLLECTION[unused_rod_keys]` or `COLLECTION[unused_witec_keys]` catch-all group in the output, so nothing is silently dropped — see [Reference > Raman Open Database reader](../reference/rod.md) and [Reference > WITec Alpha reader](../reference/witec.md).

## Post-processing

Both parsers can override `post_process(eln_data)`. This is called once, after every input file (including the ELN) has been parsed, before the config file is applied — to compute values that don't exist as a single field in the source data. `WitecParser` uses this to turn the measured wavelength axis and the laser wavelength (from the ELN) into a Raman shift axis; `RodParser` uses it to convert a spectral resolution given in wavenumbers into a wavelength-domain resolution, and to convert a diffraction grating's groove density into a grating period. See [Learn > The WITec and ROD readers](readers.md) for the details of each.
