"""Commerce provider metadata for the Dark Cocoa runtime."""

from dataclasses import dataclass
from typing import Dict, Tuple


@dataclass(frozen=True)
class IntegrationLibrary:
    """Describes an upstream open-source integration."""

    provider: str
    package_name: str
    category: str
    official: bool
    integration_mode: str


SHOPIFY_ADMIN_API = IntegrationLibrary(
    provider="Shopify",
    package_name="ShopifyAPI",
    category="storefront",
    official=True,
    integration_mode="python-sdk",
)

WIX_COMMERCE_API = IntegrationLibrary(
    provider="Wix",
    package_name="https-api",
    category="storefront",
    official=True,
    integration_mode="http-api",
)

VISA_DEVELOPER_PLATFORM = IntegrationLibrary(
    provider="Visa",
    package_name="visa-developer-platform",
    category="payments",
    official=True,
    integration_mode="api-client",
)

MASTERCARD_CLIENT_ENCRYPTION = IntegrationLibrary(
    provider="Mastercard",
    package_name="mastercard-client-encryption",
    category="payments",
    official=True,
    integration_mode="api-client",
)


class CommerceProviderRegistry:
    """Registry for deterministic storefront and card network metadata."""

    def __init__(self) -> None:
        self._providers: Dict[str, IntegrationLibrary] = {
            library.provider.lower(): library
            for library in (
                SHOPIFY_ADMIN_API,
                WIX_COMMERCE_API,
                VISA_DEVELOPER_PLATFORM,
                MASTERCARD_CLIENT_ENCRYPTION,
            )
        }

    def providers(self) -> Tuple[IntegrationLibrary, ...]:
        return tuple(self._providers.values())

    def storefronts(self) -> Tuple[IntegrationLibrary, ...]:
        return tuple(
            provider for provider in self._providers.values() if provider.category == "storefront"
        )

    def payment_networks(self) -> Tuple[IntegrationLibrary, ...]:
        return tuple(
            provider for provider in self._providers.values() if provider.category == "payments"
        )

    def summary(self) -> Dict[str, Tuple[str, ...]]:
        return {
            "storefronts": tuple(provider.provider for provider in self.storefronts()),
            "payments": tuple(provider.provider for provider in self.payment_networks()),
        }
