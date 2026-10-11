public class DecryptCommand implements Command {
    private CipherEngine engine;
    private String text;

    public DecryptCommand(CipherEngine engine, String text) {
        this.engine = engine;
        this.text = text;
    }

    @Override
    public void execute() {
        engine.decrypt(text);
    }
}
