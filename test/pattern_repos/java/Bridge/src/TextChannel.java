public class TextChannel extends SecureChannel {
    public TextChannel(Cipher cipher) {
        super(cipher);
    }

    @Override
    String transmit(String data) {
        return "text:" + cipher.apply(data);
    }
}
