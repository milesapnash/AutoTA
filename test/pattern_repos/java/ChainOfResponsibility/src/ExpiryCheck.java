public class ExpiryCheck extends CertificateCheck {
    @Override
    boolean verify(String certificate) {
        return !certificate.contains("expired");
    }
}
