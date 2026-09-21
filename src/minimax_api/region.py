"""Per-country Minimax deployments.

Minimax runs one code base behind several national deployments, each with its
own host and OAuth scope. Only the Serbian preset is verified: it is the only
organisation these authors can reach. Other countries are a configuration
change, not a code change, but they are not claimed as supported.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Region:
    """A national Minimax deployment."""

    code: str
    base_url: str
    token_url: str
    scope: str


#: Serbia. Verified against a live RS organisation on 2026-09-21.
RS = Region(
    code="RS",
    base_url="https://moj.minimax.rs/RS/API",
    token_url="https://moj.minimax.rs/RS/AUT/oauth20/token",
    scope="minimax.rs",
)
