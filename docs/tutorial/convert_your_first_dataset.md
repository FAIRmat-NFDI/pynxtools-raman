# Convert your first Raman dataset

## Who is this tutorial for?

Anyone who has `pynxtools-raman` installed and wants to see, hands-on, how a Raman measurement turns into a standardized `NXraman` file.

## What should you know before this tutorial?

- You should have `pynxtools-raman` installed — see the [installation guide](installation.md).
- You should have a copy of the [`pynxtools-raman` repository](https://github.com/FAIRmat-NFDI/pynxtools-raman), since this tutorial uses the example files that ship with it.

## What will you know at the end of this tutorial?

- How the pieces of a conversion — raw data, an ELN file, a config file, and the `pynx convert` command — fit together.
- What a converted `NXraman` file looks like.
- Where to go next depending on whether your data looks like the WITec example or comes from the Raman Open Database.

## The example dataset

The repository ships a small, self-contained example under `examples/witec/txt/`: a Raman spectrum of a silicon wafer, exported from a WITec Alpha instrument.

```text
examples/witec/txt/
├── Si-wafer-Raman-Spectrum-1.txt   # the raw measurement export
└── eln_data.yaml                   # metadata the raw export doesn't carry
```

Open `Si-wafer-Raman-Spectrum-1.txt` and you'll see two sections: a `[Header]` block with instrument settings as `key = value` pairs, and a `[Data]` block with comma-separated wavelength/intensity pairs. The WITec parser reads the `[Header]` block too (it's where the axis/intensity units come from), but most of what a `NXraman` entry needs — instrument, sample, user, experiment description, ... — comes from `eln_data.yaml`, since the WITec header doesn't carry it. Open that file too: it's a plain YAML structure whose keys already mirror the NeXus concepts we're about to write, e.g. `instrument.beam_incident.wavelength.value`.

## Steps

### 1. Run the conversion

From the root of the repository:

```console
pynx convert examples/witec/txt/eln_data.yaml examples/witec/txt/Si-wafer-Raman-Spectrum-1.txt src/pynxtools_raman/config/config_file_witec.json --reader raman --nxdl NXraman --output witec_example.nxs
```

You're passing four things:

- the `.yaml` **ELN file**,
- the `.txt` **raw data file**,
- the `.json` **config file**, which tells the converter how to map both of the above onto `NXraman` concepts (see [Learn > Reader architecture](../learn/architecture.md) for how this actually works),
- `--reader raman --nxdl NXraman`, selecting `pynxtools-raman`'s reader and the `NXraman` application definition.

`pynx` figures out which of the three input files is which by file extension — `.yaml` goes to the ELN handler, `.txt` to the WITec parser, `.json` becomes the config file.


!!! info "Default configuration files"
    We are explicitly passing the config file here for demonstration purposes. Note that the config file at `src/pynxtools_raman/config/config_file_witec.json` gets used by default for WITec files anyway, even if it is not passed explicitly.

### 2. Read the output

The command prints a handful of warnings — mostly about enum values that don't exactly match NeXus's open enumerations (e.g. the source type `laser`) or missing unit documentation. These are expected for this example and don't stop the conversion; see [Reference > WITec Alpha reader](../reference/witec.md) if you want to know exactly which ones to expect.

At the end you should see:

```text
The output file generated: witec_example.nxs.
```

### 3. Inspect the file

`witec_example.nxs` is a regular HDF5 file. Open it with [H5Web](https://h5web.panosc.eu/h5wasm){:target="_blank" rel="noopener"} in your browser, the VS Code H5Web extension, or any HDF5 viewer. You should find, among others:

- `entry/data/x_values_raman` and `entry/data/y_values`: the Raman shift and intensity arrays.
- `entry/instrument/beam_incident/wavelength`: `532.1`, taken straight from `eln_data.yaml`.
- `entry/sample/name`: `Silicon Wafer`.
- `entry/instrument/source_532nmlaser`: a group, because the config file wrote it with the NeXus concept syntax `SOURCE[source_532nmlaser]` (see [Learn > Reader architecture](../learn/architecture.md#config-file-keys-are-nexus-paths)).

## Where to go next

- If your own data looks like the WITec example — a raw measurement file plus metadata you supply yourself — read [How-to > Adjust the config file for your own instrument](../how-tos/adjust_the_config_file.md).
- If you're working with `.rod` files from the Raman Open Database instead, the same `pynx convert` command works with `config_file_rod.json` and no ELN file — see [How-to > Convert WITec or ROD data](../how-tos/convert_data.md). For converting many `.rod` files at once and preparing them for a NOMAD upload, see [How-to > Build a NOMAD upload batch from the Raman Open Database](../how-tos/build_a_rod_upload_batch.md).
- If you want to understand what's actually happening during the conversion, [Learn > Reader architecture](../learn/architecture.md) and [Learn > The WITec and ROD readers](../learn/readers.md) explain the design.
