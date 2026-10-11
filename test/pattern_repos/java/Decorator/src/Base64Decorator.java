import java.util.Base64;

public class Base64Decorator extends EncryptorDecorator {
    public Base64Decorator(Encryptor wrapped) {
        super(wrapped);
    }

    @Override
    public String encrypt(String text) {
        String encrypted = wrapped.encrypt(text);
        return Base64.getEncoder().encodeToString(encrypted.getBytes());
    }
}
