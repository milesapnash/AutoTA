public class SignatureCheck extends CertificateCheck {
    @Override
    boolean verify(String certificate) {
        return certificate.endsWith("signed");
    }
}
