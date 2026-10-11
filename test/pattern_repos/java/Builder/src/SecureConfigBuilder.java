public class SecureConfigBuilder implements ConfigBuilder {
    private CipherConfig config = new CipherConfig();

    @Override
    public void buildAlgorithm() {
        config.setAlgorithm("AES");
    }

    @Override
    public void buildKeySize() {
        config.setKeySize(256);
    }

    @Override
    public void buildMode() {
        config.setMode("GCM");
    }

    @Override
    public CipherConfig getResult() {
        return config;
    }
}
