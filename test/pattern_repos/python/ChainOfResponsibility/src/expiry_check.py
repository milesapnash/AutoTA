from certificate_check import CertificateCheck


class ExpiryCheck(CertificateCheck):
    def verify(self, certificate):
        return "expired" not in certificate
