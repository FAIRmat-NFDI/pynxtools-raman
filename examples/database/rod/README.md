## Raman Open Database Reader
This is an example file to convert a .rod file from the [Raman Open Database](https://solsa.crystallography.net/rod/) to a NeXus file.

## How to use

- 1. Go into the root folder of this repository (default "pynxtools-raman")
- 2. Copy and paste:
    ```
    pynx convert examples/database/rod/rod_file_1000679.rod src/pynxtools_raman/config/config_file_rod.json --reader raman --nxdl NXraman --output examples/database/rod/rod_example_nexus.nxs
    ```
- 3. Inspect the created NeXus file. Some warnings may be present.

## Yet unassigned fields / ToDo-List:

### Publication and ROD citation data

Now mapped into two `citeID(NXcite)` instances (`cite_publication`, `cite_rod`) via `build_citation_fields()` in `rod_reader.py`, populating `author`/`doi`/`description`.

### ROD data

'_rod_data_source.file': 'k-cymrite.rod',
'_rod_data_source.block': '/var/www/html/rod/tmp/uploads/1571122279.3252-A619ABAF81C5BA8B.rod',

### RAMAN data

'_raman_measurement_device.configuration': 'simple', # other options triple, other ? Does not make snse trippme monochromator, filter?
'_raman_measurement_device.resolution': '1',        # given in 1/cm. But no field in NXoptical_spec
'_raman_measurement_device.microscope_system': 'dispersive',    # dispersive FTIR or other
'_raman_determination.method': 'experimental', # can not yet be described in NeXus
'_raman_measurement.range_min': '50.000', # not yet in NeXus
'_raman_measurement.range_max': '1400.643', # Not yet in NeXus
'_raman_measurement_device_calibration.standard': 'other', # description of device calibration
'_raman_measurement_device_calibration.standard_details': 'Plasma lines are used.',

'_raman_measurement_device.direction_polarization': 'unoriented', # does not make really sense. Only specific entries could be used in NeXus
'_raman_measurement_device.location': "'Institute for Planetary Materials, Okayama University'",

### SAMPLE

'_cod_original_formula_sum': "'O9 Si3 Al K H2'",
But there is also: (#BUT)
'_raman_measurement.environment_details': 'The sample was measured in air.', #BUT '_raman_measurement.environment': 'Air', was included!
'_chemical_formula_sum': "'Al H2 K O9 Si3'", #BUT '_chemical_formula_structural': "'NaAlSi3O8 H2O'",
'_chemical_name_mineral': 'K-cymrite', # BUT'_chemical_name_systematic': "'hydrous sodium alumino-silicate'",
'_chemical_compound_source': "'synthesized at 5 GPa and 800 C'",

'_[local]_chemical_compound_color': 'white', should go to 

### NXfit?

'_raman_measurement.background_subtraction': 'no',
'_raman_measurement.background_subtraction_details': 'No background subtraction method was applied.',
'_raman_measurement.baseline_correction': 'no',
'_raman_measurement.baseline_correction_details': 'No baseline correction method was applied.',
