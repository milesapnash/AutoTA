public class RotorMachine {
    private int position;

    public void advance() {
        position = (position + 1) % 26;
    }

    public RotorMemento save() {
        return new RotorMemento(position);
    }

    public void restore(RotorMemento memento) {
        position = memento.getPosition();
    }
}
