public class KeyRing implements KeyCollection {
    private String[] keys;

    public KeyRing(String[] keys) {
        this.keys = keys;
    }

    @Override
    public KeyIterator createIterator() {
        return new KeyRingIterator(keys);
    }
}
