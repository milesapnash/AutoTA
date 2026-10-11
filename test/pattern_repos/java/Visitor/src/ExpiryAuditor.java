public class ExpiryAuditor implements ItemVisitor {
    @Override
    public void visitKey(SecretKey key) {
        System.out.println("Keys do not expire");
    }

    @Override
    public void visitCertificate(Certificate certificate) {
        System.out.println(certificate.getSubject() + " expires in " + certificate.getDaysValid() + " days");
    }
}
