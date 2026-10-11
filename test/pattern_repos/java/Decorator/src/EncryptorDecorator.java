abstract public class EncryptorDecorator implements Encryptor {
    protected Encryptor wrapped;

    public EncryptorDecorator(Encryptor wrapped) {
        this.wrapped = wrapped;
    }
}
