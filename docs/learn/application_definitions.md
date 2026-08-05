# The application definitions: NXoptical_spectroscopy and NXraman

Every file `pynxtools-raman` writes follows [`NXraman`](https://fairmat-nfdi.github.io/nexus_definitions/classes/applications/NXraman.html){:target="_blank" rel="noopener"}, a NeXus *application definition* — a formal, machine-checkable specification of which groups, fields, and attributes a file for a given kind of experiment must, may, or must not contain. That's what makes an `.nxs` file more than "HDF5 with some metadata attached": a converted ROD record and a converted WITec measurement both store their beam wavelength, sample name, and spectrum data at the same paths, so anything that understands `NXraman` — a normalizer, a search app, a plotting script — can read either one the same way.

## `NXraman` extends `NXoptical_spectroscopy`

`NXraman` doesn't define its structure from scratch; it `extends` a more general application definition, [`NXoptical_spectroscopy`](https://fairmat-nfdi.github.io/nexus_definitions/classes/applications/NXoptical_spectroscopy.html){:target="_blank" rel="noopener"}, which describes what any optical spectroscopy experiment has in common — a light source, a sample, a detector, sensors monitoring sample or beam conditions, citation groups.

`NXraman` itself adds only what's specific to Raman spectroscopy on top, for example the `raman_experiment_type` field (its allowed values are the named Raman techniques — resonant, tip-enhanced, surface-enhanced, and so on), the `scattering_configuration` field, and the `beam_incident` group.

## Where to look things up

The canonical, browsable definitions live at [fairmat-nfdi.github.io/nexus_definitions](https://fairmat-nfdi.github.io/nexus_definitions/classes/applications/NXraman.html){:target="_blank" rel="noopener"} — every field, its expected type, units, and enumeration values, with the full inheritance chain shown. That's the place to check what an `NXraman` file is *allowed* to contain; [Reference > Raman Open Database reader](../reference/rod.md) and [Reference > WITec Alpha reader](../reference/witec.md) describe what `pynxtools-raman` actually *writes* into it for each supported format.

## Standardization

## Not yet standardized

`NXraman` and `NXoptical_spectroscopy` are part of the NIAC NeXus definitions, but as of the 2025.11 release, they aren't marked as standardized yet — they're still going through NIAC's review process rather than being a frozen, stable part of the standard, so their structure can still change before that happens. See [Learn > Note on versioning](versioning.md) for how the exact definitions version used for a given conversion is recorded in the output file.

As of the [2025.11 release](https://github.com/nexusformat/definitions/releases/tag/v2025.11) of the officialNeXus definitions maintained by the NeXus International Advisory Committee (NIAC), `NXraman` and `NXoptical_spectroscopy` are standardized application definitions, i.e., part of the official NeXus standard maintained by NIAC. See [Learn > Note on versioning](versioning.md) for how the exact definitions version used for a given conversion is recorded in the output file.

## Use cases

A real-world example of `NXraman` data in the wild: the [RRUFF mineral database mirror at spectra.adma.ai](https://spectra.adma.ai/search/){:target="_blank" rel="noopener"} publishes its Raman spectra as `NXraman` files, browsable directly with H5Web, e.g. [this Anatase spectrum](https://spectra.adma.ai/search/?h5web=/RRUF/Anatase__R060277-3__Raman__514__0__ccw__Raman_Data_Processed__14960.nxs#/R060277%20Anatase_RRUF-4c1d6889-f9f1-5657-a80d-5738b50c4f9f/PROCESSED/R060277%20Anatase_1){:target="_blank" rel="noopener"}.
