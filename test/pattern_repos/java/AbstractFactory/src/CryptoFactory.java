public interface CryptoFactory {
    Cipher createCipher();

    Hash createHash();
}
