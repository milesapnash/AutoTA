public interface ItemVisitor {
    void visitKey(SecretKey key);

    void visitCertificate(Certificate certificate);
}
