public class ReverseCipher implements Cipher {
    @Override
    public String encrypt(String plaintext) {
        return new StringBuilder(plaintext).reverse().toString();
    }
}
