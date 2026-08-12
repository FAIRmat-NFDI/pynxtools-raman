# Build a NOMAD upload batch from the Raman Open Database

This how-to covers how to use the command-line tool `pynx-raman` for downloading `.rod` files from the [Raman Open Database (ROD)](https://solsa.crystallography.net/rod/){:target="_blank" rel="noopener"}, converting them to NeXus, packaging the result, and uploading it to NOMAD. See [Reference > Command line interface](../reference/cli.md) for the full option list, and [Learn > The Raman Open Database in NOMAD](../learn/rod_database_in_nomad.md) for why this exists.

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

You're asked for confirmation before downloading (if any files are missing) and again before converting (if doing so would overwrite `.nxs` files from a previous run) — re-running the command on a directory you've already built into is safe, but not silent. Pass `-y`/`--yes` to skip both confirmation prompts — useful when scripting a large batch.

## Downloading all known ROD records

`pynxtools-raman` bundles the full list of known ROD IDs as package data, so this works right after `pip install pynxtools-raman` — no source checkout needed:

```shell
pynx-raman build-upload-batch --all --output-dir rod_batch
```

`rod_batch/` is then ready for `pynx-raman upload` (below).

## Upload the batch to NOMAD

```shell
pynx-raman upload --output-dir rod_batch
```

Zips `--output-dir`'s contents, uploads the archive to NOMAD, and waits for processing to finish, printing the entry count and any errors. This requires:

- the `pynxtools-raman[upload]` extra installed (`pip install pynxtools-raman[upload]`), which pulls in [`nomad-utility-workflows`](https://pypi.org/project/nomad-utility-workflows/){:target="_blank" rel="noopener"},
- `NOMAD_USERNAME` and `NOMAD_PASSWORD` set in the environment.

By default the upload stays unpublished, sitting in staging where you can review it in the NOMAD web UI. Pass `--publish` to publish it automatically once processing succeeds — this asks for confirmation unless you also pass `-y`/`--yes`, since publishing is not reversible. Use `--upload-name` to give the upload a name, and `--nomad-url` to target a deployment other than the central NOMAD (e.g. an Oasis used for piloting a batch before it goes to the central deployment).

Every upload also gets an auto-generated `README.md`, describing what the Raman Open Database is and listing the `.nxs` files it contains, alongside the machine-readable `nomad.json` (see below).

### Upload in batches

For a large `--output-dir` (e.g. the full ROD dataset), uploading everything as a single NOMAD upload is operationally awkward — harder to review, and a problem with one entry risks the whole upload. Pass `--batch-size` to split the directory's `.nxs` files into multiple uploads of at most that many entries each:

```shell
pynx-raman upload --output-dir rod_batch --batch-size 100
```

Each batch is staged into its own temporary directory — with its own `README.md` listing just that batch's files, plus a copy of `nomad.json` — then zipped, uploaded, and waited on in turn. If `--upload-name` is given, each batch's name gets a `(batch i/N)` suffix so they stay distinguishable in the NOMAD UI. `--publish` asks for confirmation once, covering all batches, not once per batch.

## What `nomad.json` is for

`nomad.json` carries the citation and license for the Raman Open Database as a whole (El Mendili et al. 2019, CC0 1.0), applied to every entry in the upload. It's distinct from the per-record citation that's already written into each `.nxs` file by the reader — see [Learn > The Raman Open Database in NOMAD](../learn/rod_database_in_nomad.md#two-layers-of-citation) for how the two fit together.

NOMAD reads a `nomad.json`/`nomad.yaml` bundled inside an upload's own files as *user metadata* — comment, references, and so on — applied to every entry beneath it during the upload's initial processing. This has nothing to do with a NOMAD deployment's own `nomad.yaml` configuration file, which lives outside any upload; `pynx-raman` writes `nomad.json` specifically to avoid that naming collision.

`build-upload-batch` writes it as its last step. If the citation text ever changes, re-run the same command on the existing batch directory — already-downloaded `.rod` files are skipped, so this refreshes `nomad.json` without hitting the ROD server again.

## Reprocessing the full database

!!! danger "Documentation, not a runbook"
    The script below is shown to document the full reprocessing pipeline end to end, not as something to run casually. It deliberately never passes `--publish`: publishing is not reversible, and re-publishing the same ROD records creates duplicate public entries in NOMAD. Only add `--publish` if you specifically intend to publish, understand the consequences, and are not going to be one of many people independently re-running this same script against the same records. If in doubt, leave uploads in staging and ask first.

The commands above compose into a single script for building and uploading the entire ROD dataset (or a defined subset of it) — this is roughly the pilot script used to validate the pipeline end to end against a NOMAD Oasis before any larger run:

```shell
#!/usr/bin/env bash
set -euo pipefail

OUTPUT_DIR="${OUTPUT_DIR:-rod_batch}"
NOMAD_URL="${NOMAD_URL:-https://nomad-lab.eu/prod/v1/api/v1}"
BATCH_SIZE="${BATCH_SIZE:-100}"

echo "Checking NOMAD credentials against $NOMAD_URL..."
if ! NOMAD_URL="$NOMAD_URL" python3 -c "
import os
from nomad_utility_workflows.utils.core import NOMAD_USERNAME, get_authentication_token
get_authentication_token(url=os.environ['NOMAD_URL'])
print(f'Auth OK for user {NOMAD_USERNAME}.')
"; then
    echo "Auth check failed -- check NOMAD_USERNAME/NOMAD_PASSWORD." >&2
    exit 1
fi

pynx-raman build-upload-batch --all --output-dir "$OUTPUT_DIR" --yes

pynx-raman upload \
    --output-dir "$OUTPUT_DIR" \
    --nomad-url "$NOMAD_URL" \
    --batch-size "$BATCH_SIZE" \
    --upload-name "ROD database ($(date +%Y-%m-%d))"
```

`NOMAD_USERNAME`/`NOMAD_PASSWORD` must be set beforehand, either exported in the shell or via a `.env` file in the working directory (`nomad-utility-workflows` reads them through `python-decouple`, which checks a `.env` file before falling back to the real environment). The auth check fails fast, before any files are built, if credentials are missing or wrong.

## Analyze which CIF keys your `.rod` files contain

```shell
pynx-raman analyze-keys rod_batch
```

Counts how often each CIF key occurs across every `.rod` file in the given directory (default: `rod_batch`, same shared default as above) and writes a sorted key/count report into that same directory as `rod_key_statistics.txt`. Useful when deciding which fields are common enough to be worth mapping in [`config_file_rod.json`](../reference/rod.md).
