# Adjust the config file for your own instrument

This how-to assumes you already understand what the config file does and how its keys and values are structured — if not, read [Learn > Reader architecture](../learn/architecture.md) first. Here, we go through concrete changes you're likely to want to make, using `config_file_witec.json` as the starting point.

## Provide your own metadata via an ELN file

The WITec reader only extracts the Raman shift and intensity arrays from the raw `.txt` export; everything else — instrument, sample, user, experiment description — comes from a separate `eln_data.yaml` file that you write. Its structure should mirror the NeXus concept paths (lowercased, without the `TYPE[...]` bracket syntax); see the [example ELN file](https://github.com/FAIRmat-NFDI/pynxtools-raman/blob/main/examples/witec/txt/eln_data.yaml) that ships with the repository, or generate a fresh template with

```shell
pynx generate-eln NXraman --eln-type reader
```

which writes `raman.eln_data.yaml` in the current directory (see the [`pynxtools` CLI reference](https://fairmat-nfdi.github.io/pynxtools/reference/cli-api.html#eln-schema-generation-pynx-generate_eln){:target="_blank" rel="noopener"} for the other options).

## Stop writing a field entirely

Remove its key from the config file. If the corresponding key is still in your `eln_data.yaml`, that's fine; it's simply not picked up. If the config file doesn't reference a piece of data at all, it never ends up in the output, no matter what's in the ELN file.

## A field is missing from the output and you don't know why

Check that the key is still spelled correctly in `eln_data.yaml` — the reader looks it up by exact path. If the key is missing there entirely, the conversion still succeeds, but you'll see a warning like:

```text
No key found during eln_data processing for key '...' after it's modification to '...'.
```

## Give a field a fixed, hardcoded value

Skip the `@eln`/`@data` prefix and just write the literal value:

```json
"/ENTRY[entry]/INSTRUMENT[instrument]/beam_incident/wavelength": 532
```

This is useful for values you know are constant across all your measurements (a fixed excitation wavelength, a lab name, ...) so you don't have to repeat them in every `eln_data.yaml`.

## Name a variadic group and declare its NeXus class

Some `NXraman` concepts are *variadic*: the application definition gives them a base class but no fixed name, so a file can contain any number of instances, each named with the `NAME[instance_name]` syntax on that segment — `NAME` is the uppercase base-class placeholder from the NXDL, `instance_name` is whatever you want to call this particular one. The shipped config files already do this throughout, for example for the laser source:

```json
"/ENTRY[entry]/INSTRUMENT[instrument]/SOURCE[source_532nmlaser]/type": "@eln"
```

If your setup has a second laser, add another key with a different instance name, e.g. `SOURCE[source_808nmlaser]/type`.

This bracket syntax only works for concepts that are actually variadic in the NXDL. Fixed-name concepts — like `beam_incident`, which `NXraman`/`NXoptical_spectroscopy` already names explicitly — take no brackets; write the path with the lowercase name only, the way it already appears throughout the config file (`.../beam_incident/wavelength`, not `.../BEAM[beam_incident]/wavelength`). See the [`pynxtools` naming rules](https://fairmat-nfdi.github.io/pynxtools/learn/nexus/nexus-rules.html){:target="_blank" rel="noopener"} for the full logic behind concept names, instance names, and when brackets apply.

## Set or override a unit

Units are separate keys with the `/@units` suffix. Either point them at the ELN file, same as the value:

```json
"/ENTRY[entry]/INSTRUMENT[instrument]/beam_incident/wavelength/@units": "@eln:/ENTRY[entry]/instrument/beam_incident/wavelength/@units"
```

or hardcode them, if the unit never changes for your setup:

```json
"/ENTRY[entry]/INSTRUMENT[instrument]/beam_incident/wavelength/@units": "nm"
```

## Rename the entry

By default, entries are named `entry` (from `ENTRY[entry]` throughout the config file). To use a different name, e.g. `measurement1`, replace every occurrence of `ENTRY[entry]` with `ENTRY[measurement1]`. If you have many keys, it's easier to structure the config file as nested dictionaries instead of flat paths — see the [`pynxtools` multi-format reader guide](https://fairmat-nfdi.github.io/pynxtools/how-tos/pynxtools/use-multi-format-reader.html){:target="_blank" rel="noopener"} for that syntax.

## Add a fallback chain for a field that comes from different sources depending on the record

Some ROD records have a mineral name, others only a systematic chemical name; some have `_cod_original_formula_sum`, others only `_chemical_formula_structural`. Rather than picking one source and losing the other, `config_file_rod.json` uses a JSON-encoded list of candidates, tried in order until one resolves:

```json
"/ENTRY[entry]/SAMPLE[sample]/name": "['@data:_chemical_name_mineral','@data:_chemical_name_systematic']"
```

The same pattern works for `@eln` sources. This is the mechanism to reach for whenever "the right field to use" depends on what a specific input file actually contains.

## Point a reader at a different config file

The `.rod` and `.witec` readers each hardcode their own default config file (see [Learn > The WITec and ROD readers](../learn/readers.md)). If you're experimenting with a modified config file, pass it explicitly on the command line — it's detected by its `.json` extension and takes precedence over the default:

```shell
pynx convert examples/witec/txt/eln_data.yaml examples/witec/txt/Si-wafer-Raman-Spectrum-1.txt my_custom_config.json --reader raman --nxdl NXraman --output test.nxs
```
