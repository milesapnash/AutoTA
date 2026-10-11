public class LegacyCryptoFactory implements CryptoFactory {
    @Override
    public Cipher createCipher() {
        return new DesCipher();
    }

    @Override
    public Hash createHash() {
        return new Md5Hash();
    }
}
