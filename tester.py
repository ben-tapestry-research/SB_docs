from decipher.beacon import api
from decipher.beacon import BeaconAPIException
from pathlib import Path
from api.forsta_api_utils import upload_project_file

def put_multipart(api, name: str, file_path: str, extra_fields: dict | None = None, content_type: str = "application/xml"):
    """
    PUT /api/v1/{name} with multipart/form-data
    Part 'contents' carries the file; optional extra form fields via data=.
    """
    api._ensureKey()  # initialize host/key like do()

    url = f"{api.host}/api/{api.version}/{name}"
    headers = {}
    headers.update(api._requestAuthHeaders)  # x-apikey (+ Cookie for session keys)
    headers.update(api.headers)              # x-requested-with, etc.
    # DO NOT set Content-Type; requests will set it with the boundary

    data = extra_fields or {}

    with open(file_path, "rb") as fh:
        files = {"contents": (Path(file_path).name, fh, content_type)}
        r = api.session.request(
            "PUT", url,
            headers=headers,
            data=data,
            files=files,
            verify=api.verifySSL,
            timeout=api.timeout,
        )

    if r.status_code != 200:
        raise BeaconAPIException(code=r.status_code, message=r.reason, body=r.content)

    # Return JSON if appropriate, else raw bytes/text
    ctype = r.headers.get("content-type", "")
    return r.json() if "application/json" in ctype or "application/vnd.api+json" in ctype else r.content



import mimetypes
from pathlib import Path
from decipher.beacon import BeaconAPIException

def upload_file(
    api,
    survey_path: str,          # e.g. "selfserve/1a/123456"
    file_path: str,            # local path to the file
    filename: str | None = None,   # e.g. "survey.xml"; defaults to basename(file_path)
    validate: bool = True,         # only applies to survey.xml
    overwrite_live: bool = False,
    location: str = "root",        # "root" or "static"
    content_type: str | None = None,
):
    forsta_api_login()

    fp = Path(file_path)
    filename = filename or fp.name
    # Build the URL path with BOTH path params:
    name = f"{survey_path}/{filename}"     # <- critical per your docs
    url  = f"{api.host}/api/{api.version}/{name}"

    # Guess content type if not provided
    if content_type is None:
        guessed, _ = mimetypes.guess_type(filename)
        content_type = guessed or "application/octet-stream"

    # Form fields (multipart text parts)
    data = {
        "validate": "true" if validate else "false",
        "overwriteLive": "true" if overwrite_live else "false",
        "location": location,  # "root" or "static"
    }

    # Auth + client headers
    headers = {}
    headers.update(api._requestAuthHeaders)
    headers.update(api.headers)  # x-requested-with, etc.

    with fp.open("rb") as fh:
        files = {"contents": (filename, fh, content_type)}
        r = api.session.request(
            "PUT", url,
            headers=headers,
            data=data,
            files=files,               # <- makes multipart/form-data
            verify=api.verifySSL,
            timeout=api.timeout,
        )

    if r.status_code != 200:
        raise BeaconAPIException(code=r.status_code, message=r.reason, body=r.content)

    ctype = r.headers.get("content-type", "")
    return r.json() if "application/json" in ctype or "application/vnd.api+json" in ctype else r.content



upload_project_file(
    project_path=f"/selfserve/2222/xml_upload_test_2", 
    filepath="xml/upload_tester.xml", 
    output_filename="survey.xml"
    )

