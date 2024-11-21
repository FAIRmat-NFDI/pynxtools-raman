## WITEC example Raman Multiformat Reader
This is an example file to convert a .rod file from the [Raman Open Databse](https://solsa.crystallography.net/rod/) to a NeXus file.

## How to use
- 1. Go into the root folder of this repository (default "pynxtools-raman")
- 2. Copy and paste:
    ```
    dataconverter examples/database/rod/rod_file_1000679.rod examples/database/rod/config_file_rod.json --reader raman_multi --nxdl NXraman --output examples/witec/txt/new_output.nxs
    ```
- 3. Profit