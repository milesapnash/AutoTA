import java.util.ArrayList;
import java.util.List;

public class KeyExchangeServer implements Mediator {
    private List<Participant> participants = new ArrayList<>();

    public void register(Participant participant) {
        participants.add(participant);
    }

    @Override
    public void relay(String message, Participant sender) {
        for (Participant participant : participants) {
            if (participant != sender) {
                participant.receive(message);
            }
        }
    }
}
