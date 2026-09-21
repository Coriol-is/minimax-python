"""Token lifecycle, including the rule that keeps customers out of lockout.

Minimax locks an API application after several consecutive token requests
carrying a wrong password. Recovery is not a cooldown: the application must be
deleted and recreated, which issues new credentials and requires a redeploy.

So a credential rejection latches this authenticator. The first rejection is
the only request that ever reaches the network; every later call raises the
same error without a socket being opened. Transport failures are a different
class entirely and leave the latch untouched.
"""

from __future__ import annotations

import threading
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Protocol

import httpx

from minimax_api.errors import MinimaxAuthError, TransportError
from minimax_api.region import Region

#: Status codes from the token endpoint that mean "these credentials are wrong".
_TERMINAL_STATUSES = frozenset({400, 401, 403})


@dataclass(frozen=True)
class Credentials:
    """Both halves of Minimax authentication.

    The client half is issued by Minimax support; the user half is created by
    the subscriber in *Moj profil*. Both are secrets.
    """

    client_id: str
    client_secret: str = field(repr=False)
    username: str
    password: str = field(repr=False)


@dataclass(frozen=True)
class Token:
    """An access token and the moment it stops being usable."""

    access_token: str = field(repr=False)
    expires_at: float


class TokenStore(Protocol):
    """Where a token lives between uses.

    Implement this over a database so concurrent workers share one token,
    preventing concurrent token requests. They would otherwise race to refresh,
    and a single bad stored password multiplied across workers reaches the
    lockout threshold in one burst.

    Note: the lockout latch is per-Authenticator instance and does not travel
    through the store. A new Authenticator instance constructed with bad
    credentials will issue its own token request and receive its own latch.
    """

    def get(self) -> Token | None: ...

    def set(self, token: Token) -> None: ...


class InMemoryTokenStore:
    """Default store. Process-local, lost on restart."""

    def __init__(self) -> None:
        self._token: Token | None = None

    def get(self) -> Token | None:
        return self._token

    def set(self, token: Token) -> None:
        self._token = token


class Authenticator:
    """Obtains and caches an access token."""

    def __init__(
        self,
        *,
        credentials: Credentials,
        region: Region,
        http: httpx.Client,
        store: TokenStore | None = None,
        clock: Callable[[], float] = time.time,
        expiry_skew: float = 60.0,
    ) -> None:
        self._credentials = credentials
        self._region = region
        self._http = http
        self._store: TokenStore = store if store is not None else InMemoryTokenStore()
        self._clock = clock
        self._expiry_skew = expiry_skew
        self._latched: MinimaxAuthError | None = None
        # Guards token acquisition. httpx.Client is thread-safe, so sharing one
        # MinimaxClient (and therefore one Authenticator) across a worker pool
        # is the expected deployment. Without this lock, N threads racing
        # access_token() with no cached token each see "no token, not latched"
        # and each send their own request to the token endpoint -- with a bad
        # password, that is exactly the burst that locks the Minimax
        # application, which is the one thing this class exists to prevent.
        self._lock = threading.Lock()

    def access_token(self) -> str:
        """Return a usable token, requesting one only when necessary."""
        if self._latched is not None:
            raise self._latched

        token = self._store.get()
        if token is not None and token.expires_at - self._expiry_skew > self._clock():
            return token.access_token

        # Slow path: no usable token. Only one thread may talk to the token
        # endpoint at a time -- the checks above are re-done under the lock
        # (double-checked locking) so a thread that queues behind a winning
        # refresh uses the token that refresh just stored, instead of issuing
        # a second request, and a thread that queues behind a latching
        # failure raises without ever touching the network.
        with self._lock:
            if self._latched is not None:
                raise self._latched

            token = self._store.get()
            if token is not None and token.expires_at - self._expiry_skew > self._clock():
                return token.access_token

            token = self._request_token()
            self._store.set(token)
            return token.access_token

    def invalidate(self) -> None:
        """Drop the cached token, e.g. after an API call answered 401."""
        self._store.set(Token(access_token="", expires_at=float("-inf")))

    def _request_token(self) -> Token:
        form = {
            "grant_type": "password",
            "client_id": self._credentials.client_id,
            "client_secret": self._credentials.client_secret,
            "username": self._credentials.username,
            "password": self._credentials.password,
            "scope": self._region.scope,
        }
        try:
            response = self._http.post(
                self._region.token_url,
                data=form,
                headers={"Accept": "application/json"},
            )
        except httpx.HTTPError as error:
            # No response means the credentials were never judged. Retrying is
            # safe and does not count towards lockout.
            raise TransportError(f"token request failed to complete: {error}") from error

        if response.status_code in _TERMINAL_STATUSES:
            latched = MinimaxAuthError(
                f"token request rejected with HTTP {response.status_code}; "
                "not retrying, because repeated credential failures lock the "
                "Minimax application",
                terminal=True,
            )
            self._latched = latched
            raise latched

        if response.status_code >= 500:
            raise TransportError(f"token endpoint returned HTTP {response.status_code}")

        payload = response.json()
        access_token = payload.get("access_token")
        if response.status_code != 200 or not access_token:
            raise TransportError(
                f"token endpoint returned HTTP {response.status_code} without an access token"
            )

        expires_in = float(payload.get("expires_in", 3600))
        return Token(access_token=access_token, expires_at=self._clock() + expires_in)
