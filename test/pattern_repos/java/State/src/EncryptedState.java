public class EncryptedState implements ConnectionState {
    @Override
    public void send(SecureConnection connection, String data) {
        System.out.println("Sending encrypted " + data);
    }
}
