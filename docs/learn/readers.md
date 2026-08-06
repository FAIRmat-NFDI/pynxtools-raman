# The WITec and ROD parsers

This page explains, at a conceptual level, what each of the two parsers does to the data before it's written into `NXraman` — the parts that go beyond a straight config-file lookup. See [Learn > Reader architecture](architecture.md) for how the two are dispatched, how they fit into the shared parser base class, and how the config file mechanism works in general. See [Reference > WITec Alpha reader](../reference/witec.md) / [Reference > Raman Open Database reader](../reference/rod.md) for the exact field-by-field mapping.

## The WITec parser

`WitecParser` (`src/pynxtools_raman/parsers/witec.py`) parses a WITec Alpha `.txt` export in two parts: the `[Data]` section into raw x/y arrays, and the `[Header]` section into scalar metadata (instrument-export fields like `XAxisUnit`, `DataUnit`, sample stage position, file/graph name). Most of what a `NXraman` entry needs — instrument details, sample information, user information — still has to come from a separate ELN file, since the WITec header doesn't carry it; that's why converting WITec data always requires one (see [How-to > Adjust the config file](../how-tos/adjust_the_config_file.md)). The header does supply the axis and intensity units directly, though, so you don't need to duplicate those in your ELN file.

WITec exports the x-axis as wavelength, but Raman spectra are conventionally reported as a shift in wavenumber relative to the excitation laser. The parser computes that conversion itself, using the laser wavelength supplied in the ELN data, and writes the result as a separate axis alongside the raw data.

## The ROD parser

`RodParser` (`src/pynxtools_raman/parsers/rod.py`) parses `.rod` files — CIF-formatted records from the [Raman Open Database](https://solsa.crystallography.net/rod/){:target="_blank" rel="noopener"} — using [`gemmi`](https://gemmi.readthedocs.io/){:target="_blank" rel="noopener"}'s CIF parser. Unlike WITec data, a `.rod` file is fully self-contained: it carries both the spectrum and its metadata as CIF key/value pairs, so no separate ELN file is needed.

A handful of `NXraman` fields aren't a direct one-to-one copy of a single CIF key and are derived by the parser before the config file sees them — among them the unit cell geometry, the measurement timestamp, a normalized optics type, and a couple of instrument quantities computed from other CIF fields. See [Reference > Raman Open Database reader](../reference/rod.md) for which fields these are and what they're derived from.

### Citations

`RodParser` also turns the publication metadata a `.rod` file carries, plus the record's own ROD identifier, into two `NXcite` groups per entry — one citing the original publication, one citing the Raman Open Database record itself. See [Learn > The Raman Open Database in NOMAD](rod_database_in_nomad.md#two-layers-of-citation) for why there are two, and what each one contains.

### Fields that don't have a NeXus home yet

Not every CIF key in a `.rod` file is mapped by `config_file_rod.json` — some don't have an obvious `NXraman` concept to go into. The same is true of a few WITec `[Header]` fields (file/graph name, scan dimensions, sample stage position). Whatever's left over after the config file has consumed everything it references is written into a `COLLECTION[unused_rod_keys]` (or, for WITec, `COLLECTION[unused_witec_keys]`) catch-all group in the output file, so the information isn't silently dropped even though it isn't (yet) structured.

### Theoretical spectra are skipped

Some `.rod` records contain a theoretical (calculated) spectrum instead of a measured one. `RodParser` detects this and `RamanReader` aborts the conversion for that file with a warning, rather than writing a file that looks like it contains measured data.
