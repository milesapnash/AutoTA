abstract public class Messenger {
    public String send(String message) {
        Cipher cipher = createCipher();
        return cipher.encrypt(message);
    }

    abstract Cipher createCipher();
}
