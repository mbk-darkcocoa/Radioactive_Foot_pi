"""Compute management for the Dark Cocoa runtime."""

from dataclasses import dataclass
from typing import Dict

from .commerce import CommerceProviderRegistry


@dataclass(frozen=True)
class ComputeProfile:
    """Runtime infrastructure profile."""

    region: str
    providers: tuple[str, ...]
    deterministic_mode: bool


class CloudComputeManager:
    """Initializes compute metadata for commerce-aware workloads."""

    def __init__(self) -> None:
        registry = CommerceProviderRegistry()
        summary = registry.summary()
        self.profile = ComputeProfile(
            region="local-sandbox",
            providers=summary["storefronts"] + summary["payments"],
            deterministic_mode=True,
        )

    def status(self) -> Dict[str, object]:
        return {
            "region": self.profile.region,
            "providers": self.profile.providers,
            "deterministic_mode": self.profile.deterministic_mode,
        }
