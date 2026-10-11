public class UpperStep implements CryptoStep {
    @Override
    public String apply(String text) {
        return text.toUpperCase();
    }
}
