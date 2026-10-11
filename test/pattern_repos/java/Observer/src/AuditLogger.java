public class AuditLogger implements KeyObserver {
    @Override
    public void update(String key) {
        System.out.println("Key rotated: " + key);
    }
}
