public class EncryptCommand implements Command {
    private CipherEngine engine;
    private String text;

    public EncryptCommand(CipherEngine engine, String text) {
        this.engine = engine;
        this.text = text;
    }

    @Override
    public void execute() {
        engine.encrypt(text);
    }
}
