public class ClosedState implements ConnectionState {
    @Override
    public void send(SecureConnection connection, String data) {
        System.out.println("Connection closed");
    }
}
