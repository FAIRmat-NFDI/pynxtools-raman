# Search Raman data in NOMAD

`pynxtools-raman` registers a dedicated **Raman** app in NOMAD once it's installed as a plugin (see [Learn > NOMAD integration](../learn/nomad_integration.md) for how that works, and [Reference > Raman NOMAD app](../reference/app.md) for the full list of columns and filters).

## Open the app

In a NOMAD instance that has `pynxtools-raman` installed:

1. Go to **Explore** in the top navigation.
2. Select **Raman** from the app menu (path `ramanapp`).

Only entries whose `NXentry/definition` is `NXraman` show up here — the app filters everything else out.

## Narrow down by material

The left-hand menu's **Elements** section gives you a periodic table filter, plus text filters for the Hill, IUPAC, reduced, and anonymous chemical formulas, and a histogram of the number of distinct elements per entry. These come from NOMAD's own material normalization (`results.material`), not directly from the NeXus file — so they work the same way here as in NOMAD's other search apps.

## Narrow down by measurement setup

Further menu sections let you filter by:

- **Space Group Number** — for crystalline reference samples (e.g. Raman Open Database records).
- **Raman Spectrometer Model** and **Scattering Configuration**.
- **Instruments** — name and short name.
- **Samples** — name and sample ID.
- **Authors / Origin** — the entry author (as recorded in the file), the NOMAD upload author, and affiliation.

The default dashboard plots histograms of incident wavelength, laser power, objective magnification, numerical aperture, and beam diameter across the entries matching your current filters — a quick way to see what kind of measurements a search result actually contains before opening individual entries.

## Inspect a single entry

Click any row in the results table to open that entry. The **Overview** tab shows the parsed metadata; the **Files** tab lets you open the raw `.nxs` file with NOMAD's built-in [H5Web](https://h5web.panosc.eu/){:target="_blank" rel="noopener"} viewer.

## Customize the dashboard without building a new app

The default dashboard widgets aren't fixed for the session: you can add your own search widgets on the fly and rearrange the existing ones by dragging them around. This is enough for a lot of ad hoc exploration, and doesn't require building a custom app. Once you have a layout you want to reuse, export it and share the exported view with others or re-import it later.

## This app isn't customized to your data

The Raman app ships with a fixed set of columns, filters, and dashboard widgets — it's meant to work reasonably well for any `NXraman` entry. If you need different columns or filters for your own research group's data, you can define a custom NOMAD app in your own plugin or ELN schema package; see the [NOMAD documentation on how-to write apps](https://nomad-lab.eu/prod/v1/docs/howto/plugins/types/apps.html){:target="_blank" rel="noopener"}.
