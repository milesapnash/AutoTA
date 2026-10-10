public class NotSingleton {
    private static NotSingleton instance;

    public NotSingleton() {
    }

    public static NotSingleton getInstance() {
        if (instance == null) {
            instance = new NotSingleton();
        }
        return instance;
    }
}
