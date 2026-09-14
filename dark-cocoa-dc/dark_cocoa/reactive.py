"""Reactive processing engine for the Dark Cocoa runtime."""

from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class StreamTopology:
    """Describes the active stream pipeline."""

    stages: Tuple[str, ...]


class ReactiveEngine:
    """Provides a deterministic stream topology."""

    def __init__(self) -> None:
        self.topology = StreamTopology(
            stages=("vision-ingest", "catalog-context", "language-decoder", "checkout-events")
        )

    def is_live(self) -> bool:
        return bool(self.topology.stages)
