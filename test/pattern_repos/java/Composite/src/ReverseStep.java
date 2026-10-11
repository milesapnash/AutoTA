public class ReverseStep implements CryptoStep {
    @Override
    public String apply(String text) {
        return new StringBuilder(text).reverse().toString();
    }
}
