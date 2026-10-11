abstract public class CertificateCheck {
    private CertificateCheck next;

    public CertificateCheck setNext(CertificateCheck next) {
        this.next = next;
        return next;
    }

    public boolean handle(String certificate) {
        if (!verify(certificate)) {
            return false;
        }
        return next == null || next.handle(certificate);
    }

    abstract boolean verify(String certificate);
}
