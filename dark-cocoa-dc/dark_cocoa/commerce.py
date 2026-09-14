"""Commerce provider metadata for the Dark Cocoa runtime."""

from dataclasses import dataclass
from typing import Dict, Tuple


@dataclass(frozen=True)
class IntegrationLibrary:
    """Describes a retailer, supplier, or payment integration target."""

    provider: str
    integration_name: str
    category: str
    official: bool
    integration_mode: str
    channels: Tuple[str, ...]
    capabilities: Tuple[str, ...]
    documentation_url: str
    notes: str = ""


SHOPIFY_ADMIN_API = IntegrationLibrary(
    provider="Shopify",
    integration_name="ShopifyAPI",
    category="storefront",
    official=True,
    integration_mode="python-sdk",
    channels=("web", "mobile", "pos"),
    capabilities=("catalog", "checkout", "inventory", "pickup"),
    documentation_url="https://shopify.dev",
)

WIX_COMMERCE_API = IntegrationLibrary(
    provider="Wix",
    integration_name="Wix REST API",
    category="storefront",
    official=True,
    integration_mode="http-api",
    channels=("web", "mobile"),
    capabilities=("catalog", "checkout", "content"),
    documentation_url="https://dev.wix.com/",
)

VISA_DEVELOPER_PLATFORM = IntegrationLibrary(
    provider="Visa",
    integration_name="Visa Developer Platform",
    category="payments",
    official=True,
    integration_mode="api-client",
    channels=("web", "mobile", "pos"),
    capabilities=("tokenization", "payments", "risk"),
    documentation_url="https://developer.visa.com/",
)

MASTERCARD_CLIENT_ENCRYPTION = IntegrationLibrary(
    provider="Mastercard",
    integration_name="Mastercard Client Encryption",
    category="payments",
    official=True,
    integration_mode="api-client",
    channels=("web", "mobile", "pos"),
    capabilities=("tokenization", "encryption", "payments"),
    documentation_url="https://developer.mastercard.com/",
)

APPLE_RETAIL_DEV = IntegrationLibrary(
    provider="Apple",
    integration_name="Apple Pay JS / PassKit",
    category="retailer",
    official=True,
    integration_mode="developer-platform",
    channels=("web", "mobile", "wallet"),
    capabilities=("payments", "wallet", "pickup-notifications"),
    documentation_url="https://developer.apple.com/",
    notes="Public developer access centers on Apple Pay and platform APIs rather than a public retail catalog API.",
)

BEST_BUY_DEVELOPER_API = IntegrationLibrary(
    provider="Best Buy",
    integration_name="Best Buy Developer APIs",
    category="retailer",
    official=True,
    integration_mode="http-api",
    channels=("web", "mobile", "store"),
    capabilities=("catalog", "store-lookup", "availability"),
    documentation_url="https://developer.bestbuy.com/",
)

TARGET_PARTNER_DATA = IntegrationLibrary(
    provider="Target",
    integration_name="Target Plus Partner",
    category="retailer",
    official=True,
    integration_mode="partner-program",
    channels=("web", "marketplace", "store"),
    capabilities=("partner-onboarding", "assortment", "fulfillment"),
    documentation_url="https://partners.target.com/",
    notes="No general public retail API is exposed in the same way as Shopify or Best Buy.",
)

SQUARE_RETAIL_PLATFORM = IntegrationLibrary(
    provider="Square",
    integration_name="Square Developer Platform",
    category="supplier",
    official=True,
    integration_mode="api-platform",
    channels=("web", "mobile", "pos", "terminal"),
    capabilities=("orders", "payments", "catalog", "inventory", "pickup"),
    documentation_url="https://developer.squareup.com/",
)

CLOVER_RETAIL_PLATFORM = IntegrationLibrary(
    provider="Clover",
    integration_name="Clover Developer Platform",
    category="supplier",
    official=True,
    integration_mode="api-platform",
    channels=("pos", "device", "store"),
    capabilities=("payments", "device-apps", "inventory", "receipts"),
    documentation_url="https://www.clover.com/developers",
)


class CommerceProviderRegistry:
    """Registry for deterministic storefront, retailer, supplier, and payment metadata."""

    def __init__(self) -> None:
        self._providers: Dict[str, IntegrationLibrary] = {
            library.provider.lower(): library
            for library in (
                SHOPIFY_ADMIN_API,
                WIX_COMMERCE_API,
                APPLE_RETAIL_DEV,
                BEST_BUY_DEVELOPER_API,
                TARGET_PARTNER_DATA,
                SQUARE_RETAIL_PLATFORM,
                CLOVER_RETAIL_PLATFORM,
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

    def online_retailers(self) -> Tuple[IntegrationLibrary, ...]:
        return tuple(
            provider for provider in self._providers.values() if provider.category == "retailer"
        )

    def in_store_suppliers(self) -> Tuple[IntegrationLibrary, ...]:
        return tuple(
            provider for provider in self._providers.values() if provider.category == "supplier"
        )

    def payment_networks(self) -> Tuple[IntegrationLibrary, ...]:
        return tuple(
            provider for provider in self._providers.values() if provider.category == "payments"
        )

    def get(self, provider_name: str) -> IntegrationLibrary:
        return self._providers[provider_name.lower()]

    def summary(self) -> Dict[str, Tuple[str, ...]]:
        return {
            "storefronts": tuple(provider.provider for provider in self.storefronts()),
            "retailers": tuple(provider.provider for provider in self.online_retailers()),
            "suppliers": tuple(provider.provider for provider in self.in_store_suppliers()),
            "payments": tuple(provider.provider for provider in self.payment_networks()),
        }
