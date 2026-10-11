public class CacheInvalidator implements KeyObserver {
    @Override
    public void update(String key) {
        System.out.println("Cache cleared for " + key);
    }
}
