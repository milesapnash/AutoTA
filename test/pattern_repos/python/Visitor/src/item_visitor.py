from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from certificate import Certificate
    from secret_key import SecretKey


class ItemVisitor(ABC):
    @abstractmethod
    def visit_key(self, key: "SecretKey"):
        pass

    @abstractmethod
    def visit_certificate(self, certificate: "Certificate"):
        pass
