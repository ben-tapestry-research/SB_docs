from pathlib import Path
import sys
import os
from dotenv import load_dotenv
from decipher.beacon import api
import json
import pandas as pd
import xml.etree.ElementTree as ET
import io
import openpyxl
# TODO: Upload XML

API_PREFIX = f"/surveys"

def resource_path(relative_path: str) -> str:
    """
    Gets the local path where program is running (used locally and when packaged into .exe)

    Args:
        relative_path (str): The filename of the file to be loaded (e.g. keys.env)

    Returns:
        resource_path (str): The full path to the file.
    """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def forsta_api_login() -> None:
    """
    Authenticates to the Forsta API using the API key in the environment vars.
    """
    env_path = resource_path("keys.env")
    if os.path.exists(env_path):
        load_dotenv(dotenv_path=env_path)
        print(f"[INFO] Loaded keys from {env_path}")
    else:
        print(
            f"[WARNING] keys.env not found at {env_path}, using system environment vars."
        )

    # Try to get the key from environment vars
    forsta_api_key = os.getenv("FORSTA_API")

    if not forsta_api_key:
        raise EnvironmentError(
            "FORSTA_API key not found. Ensure keys.env is present or the environment variable is set."
        )

    # Finally perform login
    api.login(key=forsta_api_key, host="https://uk.focusvision.com/")
    print("[INFO] Logged into Forsta API successfully.")


def clean_filename(filename: str) -> str:
    """
    Removes invalid characters from filename
    """
    # Replace invalid characters with underscores
    invalid_chars = r'[<>:"/\\|?*[]'
    for char in invalid_chars:
        filename = filename.replace(char, "")
    return filename


def download_project_file(project_path: str, kind: str, save_to_disk: bool = True, output_dir: str = "", allow_load_from_disk: bool = True) -> object:
    """
    Downloads a file from the Forsta API, or loads it from disk if already downloaded.

    Args:
        project_path (str): The Decipher project path (e.g. 'selfserve/2222/240519')
        kind (str): The type of download requested from Forsta API (e.g. "datamap_json", "datamap_xlsx", "data", "summary")
        save_to_disk (boolean): Whether to save the downloaded file to disk.
        output_dir (str): OPTIONAL - the directory to save the file to (defaults to current working directory if unspecified)

    Returns:
        response (object): The downloaded file as a JSON object or Pandas DataFrame.
    """

    project_name = get_survey_info(project_path,info="title")

    # The allowed types of download
    if kind not in ["datamap_json", "datamap_xlsx", "data", "summary", "xml"]:
        raise ValueError("Invalid download requested from Forsta API!")

    cond = split = None

    if kind.startswith("datamap"):
        api_path = f"{API_PREFIX}/{project_path}/datamap"
        format_type = kind.split("_")[1]  # either json or xlsx
    elif kind == "data":
        api_path = f"{API_PREFIX}/{project_path}/data"
        cond = "qualified"
        format_type = "csv"
    elif kind == "summary":
        api_path = f"{API_PREFIX}/{project_path}/summary/completions"
        format_type = "json"
    elif kind == "xml":
        api_path = f"{API_PREFIX}/{project_path}/files/survey.xml"
        format_type = "xml"

    save_dir = output_dir if output_dir != "" else kind
    os.makedirs(save_dir, exist_ok=True)

    proj_id = project_path.split("/")[-1] if "/" in project_path else project_path
    
    # Clean the project name and create filename
    safe_project_name = clean_filename(project_name)
    file_name = f"{proj_id}_{safe_project_name}_data_confidential.{format_type}"
    full_path = os.path.join(save_dir, file_name)

    # Load from disk if the file already exists and we allowed it
    if allow_load_from_disk and os.path.exists(full_path):
        print(f"Loading existing {kind} file from {full_path}...")
        with open(full_path, "r", encoding="utf-8") as f:
            if format_type == "json":
                return json.load(f)
            elif format_type == "csv":
                return pd.read_csv(f, low_memory=False)
            elif format_type == "xml":
                tree = ET.parse(full_path)
                root = tree.getroot()
                return root

    # Download from API
    try:
        forsta_api_login()
        # TODO: add printing of project name (using API method in this file)
        print(f"Downloading {kind} for project {project_name}...")
        response = api.get(
            api_path,
            format=None if format_type == "xml" else format_type,
            cond=cond,
            split=split,
        )

        # Save to disk if required
        if save_to_disk:
            os.makedirs(kind, exist_ok=True)

            if format_type in ["xlsx", "xml"]:
                with open(full_path, "wb") as f:
                    f.write(response)  # response is already in bytes
            else:
                with open(full_path, "w", encoding="utf-8") as f:
                    if format_type == "json":
                        json.dump(response, f, indent=2)
                    elif format_type == "csv":
                        decoded = response.decode("latin1").strip()
                        if not decoded:
                            raise ValueError(
                                f"Empty data file for project {project_name}!")
                        f.write(decoded)

            # print(f"{kind.capitalize()} saved to {full_path}")

        # Return in-memory object
        if format_type == "json":
            return response
        elif format_type == "csv":
            # DataFrame
            return pd.read_csv(io.StringIO(response.decode("latin1")), low_memory=False)
        elif format_type == "xlsx":
            return openpyxl.load_workbook(io.BytesIO(response))  # DataFrame
        elif format_type == "xml":
            return ET.fromstring(response)

    except Exception as e:
        print(f"Failed to download {kind} for project {project_name}: {e}")
        raise



def get_survey_info(project_path: str, info: str) -> str:
    """Fetches info for a given survey path (e.g. "/selfserve/2222/231312")

    Args:
        project_path (str): The survey path (e.g. "/selfserve/2222/231324")
        info (str): The desired information (e.g. "title")

    Raises:
        ValueError: If invalid info type passed as argument

    Returns:
        str: The information fetched from the API
    """

    # As specified by Forsta API response (https://docs.developer.focusvision.com/docs/decipher/api#tag/Surveys/operation/getRHSurvey)
    avail_info_types = ['lastSurveyEdit', 'sampleSources', 'isRetired', 'groups', 'closedDate', 'createdBy', 'questions', 'owner', 'total', 'finishTime', 'retention', 'compat', 'archived', 'isDeprecated', 'medianQtime', 'state', 'dateLaunched', 'type', 'today', 'category', 'description', 'tags', 'myAccess', 'averageQtime',
                        'otherLanguages', 'qualified', 'myEdit', 'lastAccessBy', 'startTime', 'accessed', 'active', 'path', 'hasProjectParameters', 'matched', 'lang', 'lastEditBy', 'isCATI', 'lastEdit', 'hasDashboard', 'lastAccess', 'createdOn', 'clickthrough', 'favorite', 'keep', 'hasSavedReport', 'lastQuotaEdit', 'directory', 'title']

    if info not in avail_info_types:
        raise ValueError("Invalid info type specified")

    forsta_api_login()
    api_path = f"/rh{API_PREFIX}/{project_path}"
    response = api.get(api_path)
    return response[info]


def upload_project_file(project_path: str, filepath: str):

    api_path = f"{API_PREFIX}/{project_path}/files/survey.xml"

    forsta_api_login()
    
    xml_path = Path(filepath)

    with xml_path.open("rb") as f:
        data = f.read()
    print(data)

    return api.put(api_path, filename="survey.xml", contents=data)