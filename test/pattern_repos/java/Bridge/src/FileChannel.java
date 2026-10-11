public class FileChannel extends SecureChannel {
    public FileChannel(Cipher cipher) {
        super(cipher);
    }

    @Override
    String transmit(String data) {
        return "file:" + cipher.apply(data);
    }
}
