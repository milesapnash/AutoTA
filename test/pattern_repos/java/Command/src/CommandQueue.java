import java.util.ArrayList;
import java.util.List;

public class CommandQueue {
    private List<Command> commands = new ArrayList<>();

    public void add(Command command) {
        commands.add(command);
    }

    public void runAll() {
        for (Command command : commands) {
            command.execute();
        }
    }
}
