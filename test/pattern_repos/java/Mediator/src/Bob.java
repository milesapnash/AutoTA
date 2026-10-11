public class Bob extends Participant {
    public Bob(Mediator mediator) {
        super(mediator);
    }

    @Override
    void receive(String message) {
        System.out.println("Bob received " + message);
    }
}
