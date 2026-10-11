abstract public class SecureChannel {
    protected Cipher cipher;

    public SecureChannel(Cipher cipher) {
        this.cipher = cipher;
    }

    abstract String transmit(String data);
}
