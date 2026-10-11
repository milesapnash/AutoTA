public class XorCipher implements Cipher {
    @Override
    public String apply(String data) {
        return "XOR(" + data + ")";
    }
}
