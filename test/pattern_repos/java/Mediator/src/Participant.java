abstract public class Participant {
    protected Mediator mediator;

    public Participant(Mediator mediator) {
        this.mediator = mediator;
    }

    public void send(String message) {
        mediator.relay(message, this);
    }

    abstract void receive(String message);
}
