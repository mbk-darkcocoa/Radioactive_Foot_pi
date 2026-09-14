"""Certificate registry for approved commerce domains."""

from dataclasses import dataclass
from typing import Dict


NOVA_COM_PEM = """-----BEGIN CERTIFICATE-----
MIIDSjCCAjKgAwIBAgIUcad3LWap5laQGuu7qouc8LNf6OswDQYJKoZIhvcNAQEL
BQAwEzERMA8GA1UEAwwIbm92YS5jb20wHhcNMjYwOTE0MTQyMjExWhcNMjcwOTE0
MTQyMjExWjATMREwDwYDVQQDDAhub3ZhLmNvbTCCASIwDQYJKoZIhvcNAQEBBQAD
ggEPADCCAQoCggEBAJtMHW16srQxrxBbX+I0Kwaiuj2E2s5yzR3Vwcf5VtjRvsID
05EDTm/go2gS3dypIXhrW+sVnVelYsxAFlVAAtGl5twh1pRxj3O0DzT3d6p08/0t
dl7gIWAqYT/Rfqi1zXK6kQn3uxJ77wbOlEcVmHMayLHft8Z+VFZ2N/DEvUiVK4xl
bqMEgl2FXi8lm61TVMy3wnpimkKyWAtmxEmU2ymOi/WB5kHX/tQaDLVycwjEnt6c
HqoW6DtCjVtcQRYp1iiih9e7Zxr8wbLUOyUyM4hCQwr+pwT/Fs+ma4PED4WsXwoH
j6FGQIhctZJFh/qQEFD6dzxIdl6SD+1XkZx7CHkCAwEAAaOBlTCBkjAdBgNVHQ4E
FgQUbgoHqsdNAP1PNanVK2Oc7Fe8DzQwHwYDVR0jBBgwFoAUbgoHqsdNAP1PNanV
K2Oc7Fe8DzQwDwYDVR0TAQH/BAUwAwEB/zA/BgNVHREEODA2gghub3ZhLmNvbYIM
33d3Lm5vdmEuY29tghBub3ZhLWNkLWRucy1jYW5lggpnaXRodWIuY29tMA0GCSqG
SIb3DQEBCwUAA4IBAQAT5YSCI/3mu87xHqbaykv+jvp9d+98cDw4YnNfWjblKVO9
I8Ko1JQXIDKQ9YRQYSvGMREQpSA8Kp8kGCY1zw+VQWZwHzfUfQPolFJ1mXkhpu/o
YdpFED0OciqJB3BOh1tStCqI9jZO2IiTE4Dx2I2F0V52M/vGMG0uH3xry/y4hLwZ
0eCh3YXCecS0uxoa8epyHDKoxu9JoI0cU2r/eHJsAveRo6DhpnmBMftjgc2XmCff
izXkKJI10upRynprEtm2LwW9pz+aSSNxC0Kj4C1HqxE9GJkDbV+Wc9+piytx/I1O
HcsS2r1W8THt6V/8rq+GhIrLu7tpjMQ+IDrpPMCt
-----END CERTIFICATE-----"""


@dataclass(frozen=True)
class DomainCertificate:
    """PEM certificate metadata for a commerce domain."""

    domain: str
    pem: str
    subject_common_name: str
    issuer_common_name: str


class CertificateAuthorityRegistry:
    """Provides approved domain certificates for deterministic runtime use."""

    def __init__(self) -> None:
        self._certificates: Dict[str, DomainCertificate] = {
            "nova.com": DomainCertificate(
                domain="nova.com",
                pem=NOVA_COM_PEM,
                subject_common_name="nova.com",
                issuer_common_name="nova.com",
            )
        }

    def get(self, domain: str) -> DomainCertificate:
        return self._certificates[domain.lower()]

    def contains(self, domain: str) -> bool:
        return domain.lower() in self._certificates
