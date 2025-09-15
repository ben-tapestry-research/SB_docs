from api.forsta_api_utils import download_project_file, upload_project_file
from decipher.beacon import BeaconAPIException
import json

from xml.etree import ElementTree as ET
project_path = '/selfserve/2222/xml_upload'


def parse_beacon_error_body(body) -> str:
    # normalize to text
    if isinstance(body, (bytes, bytearray)):
        raw = body.decode("utf-8", errors="replace")
    elif isinstance(body, str):
        raw = body
    else:
        return f"(unreadable response body of type {type(body).__name__})"

    # try JSON
    try:
        payload = json.loads(raw)
        # common shapes: {"errors": [...]}, {"error": "..."} , {"message": "..."}
        if isinstance(payload, dict):
            parts = []
            if "errors" in payload:
                errs = payload["errors"]
                if isinstance(errs, (list, tuple)):
                    parts.extend(str(e) if not isinstance(e, dict) else e.get("message") or e.get("detail") or json.dumps(e) for e in errs)
                else:
                    parts.append(str(errs))
            if "error" in payload:
                parts.append(str(payload["error"]))
            if "message" in payload:
                parts.append(str(payload["message"]))
            if parts:
                return " | ".join(p for p in parts if p)
        # fallback: pretty JSON
        return json.dumps(payload, indent=2)
    except Exception:
        pass

    # try XML
    try:
        root = ET.fromstring(raw)
        tags = ("error", "errors", "message", "detail", "Description", "Message", "Reason")
        msgs = []
        for tag in tags:
            for el in root.iter(tag):
                if (txt := (el.text or "").strip()):
                    msgs.append(txt)
        if msgs:
            return " | ".join(msgs)
    except Exception:
        pass

    # as-is
    return raw














download_project_file(project_path, "xml")
try:
    upload_response = upload_project_file(project_path, "xml/xml_upload_XML Upload Test_data_confidential.xml")
except BeaconAPIException as e:
     detail = parse_beacon_error_body(e.body)
     raise RuntimeError(f"Upload failed ({e.code} {e.message}): {detail}") from e


print(upload_response.extra)