public class KeyRingIterator implements KeyIterator {
    private String[] keys;
    private int position = 0;

    public KeyRingIterator(String[] keys) {
        this.keys = keys;
    }

    @Override
    public boolean hasNext() {
        return position < keys.length;
    }

    @Override
    public String next() {
        return keys[position++];
    }
}
