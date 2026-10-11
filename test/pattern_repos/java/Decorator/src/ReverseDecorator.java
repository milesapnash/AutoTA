public class ReverseDecorator extends EncryptorDecorator {
    public ReverseDecorator(Encryptor wrapped) {
        super(wrapped);
    }

    @Override
    public String encrypt(String text) {
        String encrypted = wrapped.encrypt(text);
        return new StringBuilder(encrypted).reverse().toString();
    }
}
