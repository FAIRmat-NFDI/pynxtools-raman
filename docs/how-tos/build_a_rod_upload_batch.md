# Build a NOMAD upload batch from the Raman Open Database

This how-to covers `pynx-raman`, the command-line tool for downloading `.rod` files from the [Raman Open Database (ROD)](https://solsa.crystallography.net/rod/){:target="_blank" rel="noopener"}, converting them to NeXus, and packaging the result for a NOMAD upload. See [Reference > Command line interface](../reference/cli.md) for the full option list, and [Learn > The Raman Open Database in NOMAD](../learn/rod_database_in_nomad.md) for why this exists.

## Download a batch of `.rod` files

```shell
pynx-raman download 1000679 1000680 --output-dir rod_batch
```

`--output-dir` defaults to `rod_batch` in the current directory, and both `download` and `build-upload-batch` (below) share that same default — so a plain `pynx-raman download 1000679` followed by `pynx-raman build-upload-batch 1000679` lands in the same place instead of scattering files across two directories.

You can also pass a text file with one ROD ID per line via `--ids-file`, or use `--all` to pull the full list of known ROD IDs bundled with the package — see [Downloading all known ROD records](#downloading-all-known-rod-records) below.

Files already present in `--output-dir` are not re-downloaded; re-running the same command is safe and only fetches what's missing. Because of that, you won't even be asked for confirmation if everything you asked for is already there.

Take a look [here](https://solsa.crystallography.net/rod/result){:target="_blank" rel="noopener"} to find valid ROD IDs. Please don't trigger unnecessarily large downloads against the ROD server.

## Build a full upload batch in one step

Downloading, converting, and writing the NOMAD upload metadata file are always done in sequence for the same directory, so `build-upload-batch` does all three in one command:

```shell
pynx-raman build-upload-batch 1000679 1000680 --output-dir rod_batch
```

This:

1. downloads each `.rod` file not already in `--output-dir`,
2. converts every `.rod` file in that directory to a same-named `.nxs` file, using the `raman` reader and `NXraman` (failures are logged and skipped, not raised — one bad record doesn't stop the batch),
3. writes `nomad.json` into the same directory (see below).

Pass `-y`/`--yes` to skip the confirmation prompt — useful when scripting a large batch.

## Downloading all known ROD records

`pynxtools-raman` bundles the full list of known ROD IDs as package data, so this works right after `pip install pynxtools-raman` — no source checkout needed:

```shell
pynx-raman build-upload-batch --all --output-dir rod_batch
```

`rod_batch/` is then ready to zip and upload to NOMAD as-is.

## What `nomad.json` is for

`nomad.json` carries the citation and license for the Raman Open Database as a whole (El Mendili et al. 2019, CC0 1.0), applied to every entry in the upload. It's distinct from the per-record citation that's already written into each `.nxs` file by the reader — see [Learn > The Raman Open Database in NOMAD](../learn/rod_database_in_nomad.md#two-layers-of-citation) for how the two fit together.

NOMAD reads a `nomad.json`/`nomad.yaml` bundled inside an upload's own files as *user metadata* — comment, references, and so on — applied to every entry beneath it during the upload's initial processing. This has nothing to do with a NOMAD deployment's own `nomad.yaml` configuration file, which lives outside any upload; `pynx-raman` writes `nomad.json` specifically to avoid that naming collision.

`build-upload-batch` writes it as its last step. If the citation text ever changes, re-run the same command on the existing batch directory — already-downloaded `.rod` files are skipped, so this refreshes `nomad.json` without hitting the ROD server again.

## Analyze which CIF keys your `.rod` files contain

```shell
pynx-raman analyze-keys rod_batch
```

Counts how often each CIF key occurs across every `.rod` file in the given directory (default: `rod_batch`, same shared default as above) and writes a sorted key/count report into that same directory as `rod_key_statistics.txt`. Useful when deciding which fields are common enough to be worth mapping in [`config_file_rod.json`](../reference/rod.md).
