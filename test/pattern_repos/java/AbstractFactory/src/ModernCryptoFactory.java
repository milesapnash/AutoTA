public class ModernCryptoFactory implements CryptoFactory {
    @Override
    public Cipher createCipher() {
        return new AesCipher();
    }

    @Override
    public Hash createHash() {
        return new Sha256Hash();
    }
}
