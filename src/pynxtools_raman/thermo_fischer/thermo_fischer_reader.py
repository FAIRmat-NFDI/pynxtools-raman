import numpy as np
import datetime


def parse_jdx_file(filepath):
    """
    Read a .txt file from Witec Alpha Raman spectrometer and return a data dictionary
    which contains Raman shift and Intensity
    """
    data_dict = {}

    with open(filepath, "r") as file:
        data = file.readlines()

    # Separate metadata and measurement data
    jdx_metadata = []
    jdx_measurement_data = []
    is_measurement = False

    for line in data:
        if line.startswith("##XYDATA"):
            is_measurement = True
        elif line.startswith("##END"):
            is_measurement = False
        elif not is_measurement:
            jdx_metadata.append(line.replace("\n", ""))
        else:
            jdx_measurement_data.append(line.replace("\n", ""))

    # extract float like measruement data colums:
    jdx_data_list = []

    for line in jdx_measurement_data:
        string_list = line.split()
        float_list = [float(item) for item in string_list]
        jdx_data_list.append(float_list)

    # Transform: [[A, B], [C, D], [E, F]] into [[A, C, E], [B, D, F]]
    jdx_data_list = [list(item) for item in zip(*jdx_data_list)]

    column_counter = 0
    for column in jdx_data_list:
        if column_counter == 0:
            data_dict["data_x"] = column
        if column_counter > 0:
            data_dict[f"data_y_{column_counter}"] = column
        column_counter = column_counter + 1

    # extract key value pair from meta data:
    for i in range(len(jdx_metadata)):
        # Metadata, always starts with ##
        if jdx_metadata[i].startswith("##"):
            key, value = jdx_metadata[i].split("=")
            data_dict[key] = value
        # this covers multi-line meta data such as comments or similar. This
        # is appended to a list and then added to the dictionary
        else:
            if key in data_dict and isinstance(data_dict[key], list):
                data_dict[key].append(jdx_metadata[i])
            else:
                data_dict[key] = [jdx_metadata[i]]

    comment = data_dict["##COMMENTS"]
    for entry in comment:
        key, value = entry.split(":")
        unit = None
        if value.startswith(" "):  # Check if the string starts with a space
            value = value[1:]
        if value.find(" ") != -1:
            value, unit = value.split(" ")
        if key == "Number of sample scans":
            data_dict["Number of sample scans"] = int(value)
        if key == "Collection length":
            data_dict["Collection length"] = float(value)
            data_dict["Collection length_unit"] = unit
        if key == "Number of background scans":
            data_dict["Number of background scans"] = int(value)
            data_dict["Number of background scans_unit"] = unit
        if key == "Raman laser frequency":
            data_dict["Raman laser wavelength"] = 1e7 / float(value)
            data_dict["Raman laser wavelength_unit"] = "nm"  # assumed input is 1/cm
        if key == "Number of rejected sample scans":
            data_dict["Number of rejected sample scans"] = int(value)
        if key == "Number of rejected background scans":
            data_dict["Number of rejected background scans"] = int(value)

    time_date = data_dict["##LONGDATE"]
    time_hour = data_dict["##TIME"]
    date_time_oject = datetime.datetime.strptime(
        f"{time_date} {time_hour}", "%Y/%m/%d %H:%M:%S"
    )
    tzinfo = datetime.timezone.utc
    date_time_oject = date_time_oject.replace(tzinfo=tzinfo)
    data_dict["##LONGDATE_AND_TIME"] = date_time_oject.isoformat()

    number_y_colums = sum(1 for key in data_dict if "data_y_" in key)
    y_average = np.zeros(len(data_dict[f"data_x"]))

    for i in range(number_y_colums):
        y_average = np.array(data_dict[f"data_y_{i+1}"]) + y_average

    raman_counts = (
        np.array(y_average) / int(number_y_colums) * float(data_dict["##YFACTOR"])
    ).tolist()
    data_dict["data_y_averaged_scaled"] = raman_counts

    return data_dict
