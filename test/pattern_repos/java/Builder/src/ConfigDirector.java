public class ConfigDirector {
    private ConfigBuilder builder;

    public ConfigDirector(ConfigBuilder builder) {
        this.builder = builder;
    }

    public CipherConfig construct() {
        builder.buildAlgorithm();
        builder.buildKeySize();
        builder.buildMode();
        return builder.getResult();
    }
}
