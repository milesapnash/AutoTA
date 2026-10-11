public class CaesarCipher implements Cipher {
    @Override
    public String apply(String data) {
        return "Caesar(" + data + ")";
    }
}
