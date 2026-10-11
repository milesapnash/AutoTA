public class LegacyScrambler {
    public String scramble(String text, int rounds) {
        StringBuilder result = new StringBuilder(text);
        for (int i = 0; i < rounds; i++) {
            result.reverse();
        }
        return result.toString();
    }
}
