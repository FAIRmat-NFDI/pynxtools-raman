# NOMAD integration

`pynxtools-raman` doesn't implement its own NOMAD parser or schema — that's handled generically by `pynxtools` for every NeXus application definition it knows about. What `pynxtools-raman` contributes on top is a search app tailored to Raman data. This page explains how the pieces fit together; for how to actually use the app, see [How-to > Search Raman data in NOMAD](../how-tos/search_raman_data_in_nomad.md).

## How a converted file becomes searchable

Once NOMAD has `pynxtools-raman` installed as a plugin, any `.nxs` file uploaded to it is picked up by `pynxtools`'s own `NexusParser`, which recognizes NeXus/HDF5 files generically — it doesn't need to know about `NXraman` specifically. The parser walks the HDF5 tree and populates NOMAD's metainfo structure from it, following the `NXraman` application definition to resolve group and field types.

Two things happen automatically during this:

- **Material normalization.** NOMAD's own normalizer looks for chemical formula and atom-type information on any `NXsample`-typed group in the entry and populates `results.material` (elements, Hill/IUPAC/reduced formula, ...) from it. This is what drives the periodic-table filter in the [Raman app](../reference/app.md) and is independent of anything `pynxtools-raman` itself does — it's the same mechanism NOMAD uses for every NeXus-based plugin.
- **Entry metadata.** The entry's `NXentry/definition` field (`NXraman`) is used to label the entry's type, and file-level references (such as `identifier_experiment`, mapped from a publication DOI for Raman Open Database records) become part of the searchable entry metadata.

## The Raman app

`pynxtools-raman` registers one NOMAD app entry point, `raman_app` (`src/pynxtools_raman/nomad/apps/__init__.py`), pointing at the search quantities exposed by `pynxtools`'s generic NeXus metainfo schema. The app declares which columns to show, which filters to expose in the side menu, and what the default dashboard looks like. See [Reference > Raman NOMAD app](../reference/app.md) for more information.

Because the app is built against `pynxtools`'s shared NeXus schema rather than a Raman-specific one, its search-quantity paths follow the schema's own naming convention rather than something Raman-specific. If that schema changes upstream in `pynxtools`, the app's paths need to be updated to match — there's no independent Raman schema layer in between.
