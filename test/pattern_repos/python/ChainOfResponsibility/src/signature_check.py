from certificate_check import CertificateCheck


class SignatureCheck(CertificateCheck):
    def verify(self, certificate):
        return certificate.endswith("signed")
