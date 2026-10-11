public class SecureConnection {
    private ConnectionState state;

    public SecureConnection() {
        this.state = new HandshakeState();
    }

    void setState(ConnectionState state) {
        this.state = state;
    }

    public void send(String data) {
        state.send(this, data);
    }

    public void close() {
        state = new ClosedState();
    }
}
