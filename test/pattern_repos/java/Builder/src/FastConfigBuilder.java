public class FastConfigBuilder implements ConfigBuilder {
    private CipherConfig config = new CipherConfig();

    @Override
    public void buildAlgorithm() {
        config.setAlgorithm("ChaCha20");
    }

    @Override
    public void buildKeySize() {
        config.setKeySize(128);
    }

    @Override
    public void buildMode() {
        config.setMode("CTR");
    }

    @Override
    public CipherConfig getResult() {
        return config;
    }
}
