public interface ConfigBuilder {
    void buildAlgorithm();

    void buildKeySize();

    void buildMode();

    CipherConfig getResult();
}
