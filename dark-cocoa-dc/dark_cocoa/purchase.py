"""Deterministic purchase flow for in-store pickup orders."""

from dataclasses import dataclass

from .auth import GuardianAuthService
from .certificate_registry import CertificateAuthorityRegistry
from .commerce import CommerceProviderRegistry


@dataclass(frozen=True)
class PickupOrder:
    """Represents an in-store pickup order."""

    order_id: str
    domain: str
    storefront: str
    payment_network: str
    sku: str
    quantity: int
    pickup_location: str
    pickup_status: str


class PickupOrderService:
    """Creates a deterministic local pickup order when the domain is trusted."""

    def __init__(self, auth_service: GuardianAuthService) -> None:
        self.auth_service = auth_service
        self.registry = CommerceProviderRegistry()
        self.certificates = CertificateAuthorityRegistry()

    def create_pickup_order(
        self,
        domain: str = "nova.com",
        sku: str = "technology-bundle",
        quantity: int = 1,
        pickup_location: str = "Nova Store",
    ) -> PickupOrder:
        if quantity < 1:
            raise ValueError("quantity must be at least 1")
        if not self.certificates.contains(domain):
            raise ValueError(f"Untrusted commerce domain: {domain}")

        self.auth_service.issue_session_token(subject="pickup-order")

        storefront = self.registry.storefronts()[0].provider
        payment_network = self.registry.payment_networks()[0].provider

        return PickupOrder(
            order_id="pickup-nova-001",
            domain=domain,
            storefront=storefront,
            payment_network=payment_network,
            sku=sku,
            quantity=quantity,
            pickup_location=pickup_location,
            pickup_status="ready-for-store-pickup",
        )
