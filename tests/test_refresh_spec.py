"""The drift check must ignore cosmetic edits to vendor prose.

Minimax re-indents the HTML inside `description`/`summary` from time to time.
Nothing in the generated client depends on those strings, so such an edit is
not API drift and must not turn the scheduled check red.
"""

import copy
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from refresh_spec import spec_diff  # noqa: E402

PROSE = "  Performs a custom action on inbox.\r\n      <div><br/><ul>\r\n  <li>approve</li>"

OPERATION: dict[str, Any] = {
    "paths": {
        "/api/orgs/{organisationId}/inbox/{inboxId}/actions/{actionName}": {
            "put": {
                "summary": PROSE,
                "description": PROSE,
                "operationId": "Inbox_Put",
                "parameters": [{"name": "actionName", "in": "path", "type": "string"}],
            }
        }
    }
}


def test_whitespace_only_prose_changes_are_not_drift() -> None:
    live = copy.deepcopy(OPERATION)
    put = live["paths"]["/api/orgs/{organisationId}/inbox/{inboxId}/actions/{actionName}"]["put"]
    put["summary"] = "Performs a custom action on inbox.\r\n<div>\r\n<br/><ul>\r\n<li>approve</li>"
    put["description"] = "Performs a custom action on inbox. <div> <br/> <ul> <li>approve</li>"

    assert spec_diff(OPERATION, live, fromfile="committed") == []


def test_a_reworded_description_is_still_reported() -> None:
    live = copy.deepcopy(OPERATION)
    put = live["paths"]["/api/orgs/{organisationId}/inbox/{inboxId}/actions/{actionName}"]["put"]
    put["description"] = "Performs a custom action on inbox. <div><br/><ul> <li>reject</li>"

    assert spec_diff(OPERATION, live, fromfile="committed") != []


def test_a_changed_parameter_is_still_reported() -> None:
    live = copy.deepcopy(OPERATION)
    put = live["paths"]["/api/orgs/{organisationId}/inbox/{inboxId}/actions/{actionName}"]["put"]
    put["parameters"][0]["type"] = "integer"

    assert spec_diff(OPERATION, live, fromfile="committed") != []
