public class ScramblerAdapter implements Cipher {
    private LegacyScrambler scrambler;

    public ScramblerAdapter(LegacyScrambler scrambler) {
        this.scrambler = scrambler;
    }

    @Override
    public String encrypt(String plaintext) {
        return scrambler.scramble(plaintext, 3);
    }
}
