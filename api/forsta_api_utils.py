from pathlib import Path
import sys
import os
from dotenv import load_dotenv
from decipher.beacon import api, BeaconAPIException
import json
import pandas as pd
import xml.etree.ElementTree as ET
import io
import openpyxl
import string
import secrets

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


# TODO: split out into helper functions - this is gross
def download_project_file(
    project_path: str,
    kind: str,
    save_to_disk: bool = True,
    output_dir: str = "",
    allow_load_from_disk: bool = True,
) -> object:
    """
    Downloads a file from the Forsta API, or loads it from disk if already downloaded.

    Args:
        project_path (str): The Decipher project path (e.g. 'selfserve/2222/240519')
        kind (str): The type of download requested from Forsta API (e.g. "datamap_json", "datamap_xlsx", "data", "summary", "xml")
        save_to_disk (bool): Whether to save the downloaded file to disk.
        output_dir (str): OPTIONAL - the directory to save the file to (defaults to current working directory if unspecified)

    Returns:
        response (object): The downloaded file as a JSON object, Pandas DataFrame, Workbook, or XML Element.
    """

    project_name = get_survey_info(project_path, info="title")

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
    safe_project_name = clean_filename(project_name)  # kept as-is per your version
    file_name = f"{proj_id}_{kind}_confidential.{format_type}"
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
        print(f"Downloading {kind} for project {project_name}...")
        response = api.get(
            api_path,
            format=None if format_type == "xml" else format_type,
            cond=cond,
            split=split,
        )

        # Parse & strip XML - sorting the namespace issue too (was causing problems when downlading)
        if format_type == "xml":
            from io import BytesIO

            buf = BytesIO(response)

            # 1) collect prefix->URI mappings
            nsmap = {}
            for event, payload in ET.iterparse(buf, events=("start-ns",)):
                prefix, uri = payload
                nsmap[prefix or ""] = uri  # '' = default namespace

            # 2) register them
            for p, u in nsmap.items():
                if p == "xml":  # reserved
                    continue
                ET.register_namespace(p, u)

            # 3) rewind and parse the actual tree
            buf.seek(0)
            root = ET.fromstring(buf.read())
            for el in root.iter():
                for k in list(el.attrib):
                    if k == "id":  # catches xml:id and other namespaces
                        del el.attrib[k]

        # Save to disk if required
        if save_to_disk:
            if format_type == "xml":
                ET.ElementTree(root).write(
                    full_path, encoding="utf-8", xml_declaration=True
                )
            elif format_type == "xlsx":
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
                                f"Empty data file for project {project_name}!"
                            )
                        f.write(decoded)

        # Return in-memory object
        if format_type == "json":
            return response
        elif format_type == "csv":
            return pd.read_csv(io.StringIO(response.decode("latin1")), low_memory=False)
        elif format_type == "xlsx":
            return openpyxl.load_workbook(io.BytesIO(response))
        elif format_type == "xml":
            return root

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
    avail_info_types = [
        "lastSurveyEdit",
        "sampleSources",
        "isRetired",
        "groups",
        "closedDate",
        "createdBy",
        "questions",
        "owner",
        "total",
        "finishTime",
        "retention",
        "compat",
        "archived",
        "isDeprecated",
        "medianQtime",
        "state",
        "dateLaunched",
        "type",
        "today",
        "category",
        "description",
        "tags",
        "myAccess",
        "averageQtime",
        "otherLanguages",
        "qualified",
        "myEdit",
        "lastAccessBy",
        "startTime",
        "accessed",
        "active",
        "path",
        "hasProjectParameters",
        "matched",
        "lang",
        "lastEditBy",
        "isCATI",
        "lastEdit",
        "hasDashboard",
        "lastAccess",
        "createdOn",
        "clickthrough",
        "favorite",
        "keep",
        "hasSavedReport",
        "lastQuotaEdit",
        "directory",
        "title",
    ]

    if info not in avail_info_types:
        raise ValueError("Invalid info type specified")

    forsta_api_login()
    api_path = f"/rh{API_PREFIX}/{project_path}"
    response = api.get(api_path)
    return response[info]


def upload_project_file(project_path: str, filepath: str, output_filename: str):
    """Upload a file to a survey (eg an xml file). Have to do this manually to bypass issue with Decipher beacon API
    Args:
        project_path (str): The Decipher project path (e.g. 'selfserve/2222/240519')
        filepath (str): The local path to the file to be uploaded
        output_filename (str): The name the file should have when uploaded to the survey (e.g. 'survey.xml')

        Returns:
            response (object): The API response as a JSON object."""

    api_path = f"{API_PREFIX}/{project_path}/files/{output_filename}"

    forsta_api_login()
    fp = Path(filepath)

    # e.g. https://uk.focusvision.com//api/v1//surveys//surveys/selfserve/2222/xml_upload_test_2/files/survey.xml
    url = f"{api.host}/api/{api.version}/{api_path}"

    if "xml" in filepath:
        content_type = "text/xml"

    headers = {}
    data = {}
    # e.g. {'x-apikey': 'API_KEY'}
    headers.update(api._requestAuthHeaders)
    # e.g. 'x-requested-with': 'decipher.beacon 29.2.0'
    headers.update(api.headers)

    with fp.open("rb") as fh:
        # {'contents': ('survey.xml', <_io.BufferedReader name='xml\\upload_tester.xml'>, 'text/xml')}
        files = {"contents": (output_filename, fh, content_type)}

        r = api.session.request(
            method="PUT",
            url=url,
            headers=headers,
            data=data,
            files=files,  # multipart form data consutrction
            verify=api.verifySSL,
            timeout=api.timeout,
        )

    # Failure status
    if r.status_code != 200:
        error_text = extract_beacon_error(body=r.content, filepath=fp)
        raise BeaconAPIException(
            code=r.status_code, message=f"{error_text}", body=r.content
        )

    return r.json()


def extract_beacon_error(body: str, filepath: str) -> str:
    """
    When uploading an XML, if an error is returned it needs to be unpacked, so we can give a descriptive error to the user.
    This function does that job and returns a nicely formatted error message

    Args:
        body (str): The content body returned by the Forsta API (JSON formatted as a string)
        filepath (str): filepath of the XML that caused the error (so we can extract the line that caused the error)

    Returns:
        final_message (str): A descriptive error message
    """

    # The response schema: https://docs.developer.focusvision.com/docs/decipher/api#tag/Survey-Files/operation/updateSurveyFile

    data = json.loads(body)

    print(data)

    main_message = data.get("$error")
    errors = []

    extra = data.get("extra")

    # Loop through the error messages
    # FROM THE FORSTA docs:
    # If an invalid file is uploaded, the 400 error code is returned.
    # If an error is returned from a survey.xml, the body will contain a list of errors in the extra property.
    # This will be an array of error objects
    for e in extra:
        t = e.get("type")
        ln = e.get("line")

        if t == "survey":
            m = e.get("error")
        elif t == "parse":
            m = e.get("message")

        # Fetch line from XML (to show in error message)
        xml_line = fetch_xml_line(filepath, ln)

        final_error = f"{t} error @ line {ln} of XML: {xml_line} :\n{m}"
        errors.append(final_error)

    final_message = main_message + "\n" + "\n\n".join(errors)

    return final_message


def fetch_xml_line(filepath: Path, line_number: str) -> str:
    """Returns a given line of XML from a file

    Args:
        filepath (Path): The filepath to the desired XML file
        line_number (str): The line number to return

    Returns:
        str: The line of XML at line_number
    """
    # Read the XML file and make a list where each element is each line
    lines = filepath.read_text().splitlines()

    try:
        # We go one line further back as the error normally says its triggered on the line after the actual error
        # strip leading spaces (as XML is intented)
        return lines[line_number - 2].lstrip()
    except:
        return "Unable to fetch line"


# TODO: finish this
def create_survey(survey_name: str) -> str:

    forsta_api_login()

    # Generate a random project path consisting of 3 letters, followed by 3 numbers
    rand_letters = [secrets.choice(string.ascii_lowercase) for _ in range(3)]
    rand_nums = [secrets.choice(string.digits) for _ in range(3)]
    survey_path = "".join(rand_letters) + "".join(rand_nums)

    # resp = api.post('/rh/companies/self/surveys', name=survey_name, ptype="beacon", prefPath=survey_path)

    # Load the survey template
    tree = ET.parse("xml/survey_template.xml")
    root = tree.getroot()
    root.set("alt", "survey_name")
    tree.write("output.xml", encoding="utf-8", xml_declaration=True)

    return 0


def fetch_modules() -> list:
    """
    Retrieve a list of modules from Decipher
    """
    forsta_api_login()
    # See: https://docs.developer.focusvision.com/docs/decipher/api#tag/Surveys
    survey_list = api.get(
        "/rh/companies/all/surveys", query=f"'[MODULES]'", select="title,path"
    )
    return survey_list
