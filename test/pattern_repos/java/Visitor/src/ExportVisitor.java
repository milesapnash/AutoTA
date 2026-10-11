public class ExportVisitor implements ItemVisitor {
    @Override
    public void visitKey(SecretKey key) {
        System.out.println("Exporting key " + key.getMaterial());
    }

    @Override
    public void visitCertificate(Certificate certificate) {
        System.out.println("Exporting certificate for " + certificate.getSubject());
    }
}
