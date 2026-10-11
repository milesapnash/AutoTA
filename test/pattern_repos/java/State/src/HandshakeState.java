public class HandshakeState implements ConnectionState {
    @Override
    public void send(SecureConnection connection, String data) {
        System.out.println("Handshake complete");
        connection.setState(new EncryptedState());
    }
}
