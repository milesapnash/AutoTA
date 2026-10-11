public class NamedAlgorithm implements CipherAlgorithm {
    private final String name;

    public NamedAlgorithm(String name) {
        this.name = name;
    }

    @Override
    public String encrypt(String text, String key) {
        return name + "(" + text + "," + key + ")";
    }
}
