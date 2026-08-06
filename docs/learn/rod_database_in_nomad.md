# The Raman Open Database in NOMAD

The [Raman Open Database (ROD)](https://solsa.crystallography.net/rod/){:target="_blank" rel="noopener"} is a public, [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/){:target="_blank" rel="noopener"}-licensed collection of reference Raman spectra, mostly of minerals and other crystalline materials, cross-referenced with the [Crystallography Open Database (COD)](https://www.crystallography.net/cod/){:target="_blank" rel="noopener"}. `pynxtools-raman` can read every `.rod` record and bundles tooling to turn the whole database into one NOMAD upload — see [How-to > Build a NOMAD upload batch from the Raman Open Database](../how-tos/build_a_rod_upload_batch.md).

## Two layers of citation

Because this data is being redistributed rather than originally produced, it carries citation information at two levels, and the tooling keeps them separate on purpose:

**Per record**, inside every `.nxs` file, the reader writes two `citeID` (`NXcite`) groups (see [Learn > The WITec and ROD readers](readers.md#citations)):

- `citeID[cite_publication]` — author, DOI, and description of the original paper reporting that specific spectrum, built from the publication metadata the `.rod` record itself carries.
- `citeID[cite_rod]` — a link back to the record's page on the ROD website, plus a note on the CC0 license and a request to cite the database (see below).

**For the batch as a whole**, `pynx-raman build-upload-batch` writes a `nomad.json` file that NOMAD applies as upload-wide metadata: a comment and a set of references citing the ROD project itself,

> El Mendili, Y. et al. (2019). Raman Open Database: first interconnected Raman-X-ray diffraction open-access resource for material identification. *J. Appl. Cryst.* 52, 618-625. [doi:10.1107/S1600576719004229](https://doi.org/10.1107/S1600576719004229)

and its CC0 1.0 license.

<!-- ## Draft: publishing the database on NOMAD

!!! warning "This section is a plan, not a shipped feature"
    Everything else on this page describes what `pynxtools-raman` can already do today. What follows is how we currently intend to use that tooling to bring the Raman Open Database onto NOMAD's central deployment — it isn't done yet, and details may still change.

The Raman Open Database was previously processed and uploaded to a FAIRmat-internal Oasis instance used for testing experimental datasets, as a way to validate the reader against the whole database before committing to anything more permanent. The plan is to bring that same dataset to NOMAD's central deployment, so it's findable and citable by anyone, not just people with access to the internal testing Oasis.

Concretely, the intended workflow is a pilot batch first — a handful of records covering different mineral classes and edge cases (missing publication metadata, records without a mineral name, records that turn out to contain a theoretical rather than measured spectrum) — uploaded and checked before running the same pipeline over the full ~1,100 known records. `pynx-raman build-upload-batch --all` produces exactly this batch, and `pynx-raman upload` (see [How-to > Build a NOMAD upload batch from the Raman Open Database](../how-tos/build_a_rod_upload_batch.md#upload-the-batch-to-nomad)) uploads it, leaving it unpublished until someone with a NOMAD account reviews the result.

The person who runs the upload becomes its NOMAD author, as with any NOMAD upload; there's no special "database author" role in NOMAD. Attribution to the actual originators of the data works entirely through the citation mechanism above: the per-record `citeID[cite_publication]` groups credit the scientists who measured and published each spectrum, and both the per-record `citeID[cite_rod]` group and the upload-wide `nomad.json` credit the Raman Open Database project and its CC0 license.

Once published, anyone would be able to find these entries through the [Raman app](../reference/app.md) — searching by mineral, chemical formula, or space group, the same way as for any other Raman data in NOMAD — and follow the citation information back to both the original measurement and the database that collected it. -->
