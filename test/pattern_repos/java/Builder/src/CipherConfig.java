public class CipherConfig {
    private String algorithm;
    private int keySize;
    private String mode;

    void setAlgorithm(String algorithm) {
        this.algorithm = algorithm;
    }

    void setKeySize(int keySize) {
        this.keySize = keySize;
    }

    void setMode(String mode) {
        this.mode = mode;
    }

    @Override
    public String toString() {
        return algorithm + "-" + keySize + "-" + mode;
    }
}
