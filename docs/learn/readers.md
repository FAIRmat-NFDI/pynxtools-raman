# The WITec and ROD readers

This page explains, at a conceptual level, what each of the two sub-readers does to the data before it's written into `NXraman` — the parts that go beyond a straight config-file lookup. See [Learn > Reader architecture](architecture.md) for how the two are dispatched and how the config file mechanism works in general, and [Reference > WITec Alpha reader](../reference/witec.md) / [Reference > Raman Open Database reader](../reference/rod.md) for the exact field-by-field mapping.

## The WITec sub-reader

`witec/witec_reader.py` parses the data section of a WITec Alpha `.txt` export into raw x/y arrays. The file's header metadata isn't parsed; that has to come from the ELN file instead, which is why converting WITec data always requires one (see [How-to > Adjust the config file](../how-tos/adjust_the_config_file.md)).

WITec exports the x-axis as wavelength, but Raman spectra are conventionally reported as a shift in wavenumber relative to the excitation laser. The reader computes that conversion itself, using the laser wavelength supplied in the ELN data, and writes the result as a separate axis alongside the raw data.

## The ROD sub-reader

`rod/rod_reader.py` parses `.rod` files — CIF-formatted records from the [Raman Open Database](https://solsa.crystallography.net/rod/){:target="_blank" rel="noopener"} — using [`gemmi`](https://gemmi.readthedocs.io/){:target="_blank" rel="noopener"}'s CIF parser. Unlike WITec data, a `.rod` file is fully self-contained: it carries both the spectrum and its metadata as CIF key/value pairs, so no separate ELN file is needed.

A handful of `NXraman` fields aren't a direct one-to-one copy of a single CIF key and are derived by the reader before the config file sees them — among them the unit cell geometry, the measurement timestamp, a normalized optics type, and a couple of instrument quantities computed from other CIF fields. See [Reference > Raman Open Database reader](../reference/rod.md) for which fields these are and what they're derived from.

### Citations

The reader also turns the publication metadata a `.rod` file carries, plus the record's own ROD identifier, into two `NXcite` groups per entry — one citing the original publication, one citing the Raman Open Database record itself. See [Learn > The Raman Open Database in NOMAD](rod_database_in_nomad.md#two-layers-of-citation) for why there are two, and what each one contains.

### Fields that don't have a NeXus home yet

Not every CIF key in a `.rod` file is mapped by `config_file_rod.json` — some don't have an obvious `NXraman` concept to go into. Whatever's left over after the config file has consumed everything it references is written into a generic collection group in the output file, so the information isn't silently dropped even though it isn't (yet) structured.

### Theoretical spectra are skipped

Some `.rod` records contain a theoretical (calculated) spectrum instead of a measured one. The reader detects this and aborts the conversion for that file with a warning, rather than writing a file that looks like it contains measured data.
