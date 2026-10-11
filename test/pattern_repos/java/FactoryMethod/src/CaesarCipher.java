public class CaesarCipher implements Cipher {
    @Override
    public String encrypt(String plaintext) {
        return "Caesar(" + plaintext + ")";
    }
}
