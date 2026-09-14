"""Vision-language runtime primitives for the Dark Cocoa runtime."""

from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class ModelStatus:
    """Deterministic model metadata."""

    model_name: str
    ready: bool
    modalities: Tuple[str, ...]


class DarkCocoaVLM:
    """Loads a deterministic vision-language runtime."""

    def __init__(self) -> None:
        self.status = ModelStatus(
            model_name="dark-cocoa-vlm",
            ready=True,
            modalities=("vision", "language", "commerce-catalog"),
        )

    def describe(self) -> str:
        return f"{self.status.model_name} ready for {', '.join(self.status.modalities)}"
