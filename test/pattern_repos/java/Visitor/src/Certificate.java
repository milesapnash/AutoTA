public class Certificate implements CryptoItem {
    private String subject;
    private int daysValid;

    public Certificate(String subject, int daysValid) {
        this.subject = subject;
        this.daysValid = daysValid;
    }

    public String getSubject() {
        return subject;
    }

    public int getDaysValid() {
        return daysValid;
    }

    @Override
    public void accept(ItemVisitor visitor) {
        visitor.visitCertificate(this);
    }
}
