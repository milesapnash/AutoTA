from abc import ABC, abstractmethod


class CertificateCheck(ABC):
    def __init__(self):
        self._next: CertificateCheck = None

    def set_next(self, check: "CertificateCheck"):
        self._next = check
        return check

    def handle(self, certificate):
        if not self.verify(certificate):
            return False
        return self._next is None or self._next.handle(certificate)

    @abstractmethod
    def verify(self, certificate):
        pass
