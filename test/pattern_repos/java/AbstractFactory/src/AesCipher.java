public class AesCipher implements Cipher {
    @Override
    public String encrypt(String plaintext) {
        return "AES(" + plaintext + ")";
    }
}
