public class Alice extends Participant {
    public Alice(Mediator mediator) {
        super(mediator);
    }

    @Override
    void receive(String message) {
        System.out.println("Alice received " + message);
    }
}
