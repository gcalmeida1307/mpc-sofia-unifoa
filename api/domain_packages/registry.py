"""Runtime registry for independently deployable domain packages."""

from __future__ import annotations

from .accounting import AccountingPackage
from .base import DomainRetrievalPackage
from .generic import GenericPackage
from .infrastructure import InfrastructurePackage
from .legal import LegalPackage
from .medical import MedicalPackage
from .people import PeoplePackage
from .personnel import PersonnelPackage

_GENERIC = GenericPackage()
_PACKAGES: dict[str, DomainRetrievalPackage] = {
    "direito": LegalPackage(),
    "departamento-pessoal": PersonnelPackage(),
    "medicina": MedicalPackage(),
    "infraestrutura": InfrastructurePackage(),
    "contabilidade": AccountingPackage(),
    "recursos-humanos": PeoplePackage(),
}


def package_for(module_id: str) -> DomainRetrievalPackage:
    return _PACKAGES.get(module_id.casefold(), _GENERIC)


def package_ids() -> tuple[str, ...]:
    return tuple(sorted(_PACKAGES))


def package_manifests() -> list[dict[str, object]]:
    return [package_for(module_id).manifest() for module_id in package_ids()]
