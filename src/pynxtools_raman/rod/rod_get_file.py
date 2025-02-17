import argparse

import requests

import logging

logger = logging.getLogger("pynxtools")

rod_id = 1000679


def save_rod_file_from_ROD_via_API(rod_id: int):
    url = "https://solsa.crystallography.net/rod/" + str(rod_id) + ".rod"

    logger.info(f"Initialized download of .rod file with ID '{rod_id}' from '{url}'.")

    try:
        response = requests.post(url)
        response.raise_for_status()  # Raise HTTP error for bad

        logger.info(f"Successfully received .rod file with ID '{rod_id}'")

        filename = str(rod_id)

        with open(filename + ".rod", "w", encoding="utf-8") as file:
            file.write(response.text)
        logger.info(f"Saved .rod file with ID '{rod_id}' to file '{filename}'")

    except requests.exceptions.ConnectionError as con_err:
        logger.error(f"ConnectionError occured: {con_err}")
    except requests.exceptions.HTTPError as http_err:
        logger.error(f"CHTTPError occured: {http_err}")
    except requests.exceptions.RequestException as req_exc:
        logger.error(f"RequestException occured: {req_exc}")


def trigger_rod_download():
    # Create an argument parser
    parser = argparse.ArgumentParser(description="Download a CIF file.")
    parser.add_argument(
        "rod_id",  # The argument's name
        type=str,  # Argument type (e.g., string)
        help="The name of the file to download",  # Help message
    )

    # Parse the command-line arguments
    args = parser.parse_args()

    save_rod_file_from_ROD_via_API(args.rod_id)
