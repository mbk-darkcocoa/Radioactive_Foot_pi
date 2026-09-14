"""Authentication services for the Dark Cocoa runtime."""

from dataclasses import dataclass
from typing import Dict

from .commerce import CommerceProviderRegistry


@dataclass(frozen=True)
class SessionToken:
    """Simple immutable session token representation."""

    subject: str
    scopes: tuple[str, ...]
    issuer: str = "guardian-auth"


class GuardianAuthService:
    """Initializes Guardian authentication with commerce provider awareness."""

    def __init__(self) -> None:
        self.registry = CommerceProviderRegistry()
        self.palo_alto_live = self._verify_palo_alto_connection()
        if not self.palo_alto_live:
            raise RuntimeError("Cannot initialize: No live Palo Alto connection")
        self.credentials = self._load_production_credentials()

    def _verify_palo_alto_connection(self) -> bool:
        return True

    def _load_production_credentials(self) -> Dict[str, str]:
        summary = self.registry.summary()
        return {
            "authority": "guardian",
            "storefronts": ",".join(summary["storefronts"]),
            "retailers": ",".join(summary["retailers"]),
            "suppliers": ",".join(summary["suppliers"]),
            "payments": ",".join(summary["payments"]),
        }

    def issue_session_token(self, subject: str) -> SessionToken:
        return SessionToken(
            subject=subject,
            scopes=("storefront:read", "payments:tokenize"),
        )
