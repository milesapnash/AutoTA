import java.util.ArrayDeque;
import java.util.Deque;

public class RotorHistory {
    private Deque<RotorMemento> history = new ArrayDeque<>();

    public void push(RotorMemento memento) {
        history.push(memento);
    }

    public RotorMemento pop() {
        return history.pop();
    }
}
