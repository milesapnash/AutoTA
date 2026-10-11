public class CryptoFacade {
    private KeyDeriver keyDeriver = new KeyDeriver();
    private Encryptor encryptor = new Encryptor();
    private Signer signer = new Signer();

    public String protect(String text, String password) {
        String key = keyDeriver.derive(password);
        String encrypted = encryptor.encrypt(text, key);
        return signer.sign(encrypted, key);
    }
}
