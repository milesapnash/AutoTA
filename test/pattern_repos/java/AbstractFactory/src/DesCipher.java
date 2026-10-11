public class DesCipher implements Cipher {
    @Override
    public String encrypt(String plaintext) {
        return "DES(" + plaintext + ")";
    }
}
