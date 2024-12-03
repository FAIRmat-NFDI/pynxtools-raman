
#rework this file later
KEY_MAP: Dict[str, str] = {
    "number_of_regions": "no_of_regions",
    "version": "software_version",
    "dimension_name": "energy_units",
    "dimension_size": "energy_size",
    "dimension_scale": "energy_axis",
    "number_of_sweeps": "no_of_scans",
    "energy_unit": "energy_scale_2",
    "low_energy": "start_energy",
    "high_energy": "stop_energy",
    "energy_step": "step_size",
    "step_time": "dwell_time",
    "detector_first_x-_channel": "detector_first_x_channel",
    "detector_last_x-_channel": "detector_last_x_channel",
    "detector_first_y-_channel": "detector_first_y_channel",
    "detector_last_y-_channel": "detector_last_y_channel",
    "file": "data_file",
    "sequence": "sequence_file",
    "spectrum_name": "spectrum_type",
    "instrument": "instrument_name",
    "location": "vendor",
    "user": "user_name",
    "sample": "sample_name",
    "comments": "spectrum_comment",
    "date": "start_date",
    "time": "start_time",
}

VALUE_MAP = {
    "no_of_regions": int,
    "energy_size": int,
    "pass_energy": float,
    "no_of_scans": int,
    "excitation_energy": float,
    "center_energy": float,
    "start_energy": float,
    "stop_energy": float,
    "step_size": float,
    "dwell_time": float,
    "detector_first_x_channel": int,
    "detector_last_x_channel": int,
    "detector_first_y_channel": int,
    "detector_last_y_channel": int,
    "time_per_spectrum_channel": float,
    "energy_units": _extract_energy_units,
    "energy_axis": _separate_dimension_scale,
    "energy_scale": convert_energy_type,
    "energy_scale_2": convert_energy_type,
    "acquisition_mode": convert_energy_scan_mode,
    "time_per_spectrum_channel": float,
    "manipulator_r1": float,
    "manipulator_r2": float,
}

UNITS: dict = {
    "energydispersion/pass_energy": "eV",
    "beam_xray/excitation_energy": "eV",
    "region/energy_axis": "eV",
    "region/center_energy": "eV",
    "region/start_energy": "eV",
    "region/stop_energy": "eV",
    "region/step_size": "eV",
    "detector/dwell_time": "eV",
    "region/time_per_spectrum_channel": "s",
}


def _get_key_value_pair(line: str):
    """
    Split the line at the '=' sign and return a
    key-value pair. The values are mapped according
    to the desired format.

    Parameters
    ----------
    line : str
        One line from the input file.

    Returns
    -------
    Tuple[str, object]
        A tuple containing:
        - key : str
            Anything before the '=' sign, mapped to the desired
            key format.
        - value : object
            Anything after the '=' sign, mapped to the desired
            value format and type.

    """
    try:
        key, value = line.split("=")
        key = convert_pascal_to_snake(key)
        key = KEY_MAP.get(key, key)
        if "dimension" in key:
            key_part = f"dimension_{key.rsplit('_')[-1]}"
            key = KEY_MAP.get(key_part, key_part)
        value = _re_map_single_value(key, value, VALUE_MAP)

    except ValueError:
        key, value = "", ""

    return key, value