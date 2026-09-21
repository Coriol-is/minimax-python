"""Fixtures for the opt-in live tests.

Live tests need real credentials and spend from the organisation's daily
request budget of 1,000. They are excluded by default (see `addopts` in
pyproject.toml); run them with `uv run pytest -m live`.
"""

from __future__ import annotations

import os
from collections.abc import Generator
from pathlib import Path

import pytest

from minimax_api import Credentials, MinimaxClient


def _load_dotenv() -> None:
    path = Path(__file__).resolve().parent.parent / ".env"
    if not path.exists():
        return
    contents = path.read_text()
    for line in contents.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


@pytest.fixture(scope="session")
def live_client() -> Generator[MinimaxClient, None, None]:
    _load_dotenv()
    required = (
        "MINIMAX_CLIENT_ID",
        "MINIMAX_CLIENT_SECRET",
        "MINIMAX_USERNAME",
        "MINIMAX_PASSWORD",
        "MINIMAX_ORGANISATION_ID",
    )
    missing = [name for name in required if not os.environ.get(name)]
    if missing:
        pytest.skip(f"live tests need {', '.join(missing)} in .env")

    client = MinimaxClient(
        credentials=Credentials(
            client_id=os.environ["MINIMAX_CLIENT_ID"],
            client_secret=os.environ["MINIMAX_CLIENT_SECRET"],
            username=os.environ["MINIMAX_USERNAME"],
            password=os.environ["MINIMAX_PASSWORD"],
        ),
        organisation_id=int(os.environ["MINIMAX_ORGANISATION_ID"]),
    )
    yield client
    client.close()
