import java.util.HashMap;
import java.util.Map;

public class KeyRegistry {
    private Map<String, Key> prototypes = new HashMap<>();

    public void register(String name, Key prototype) {
        prototypes.put(name, prototype);
    }

    public Key create(String name) {
        return prototypes.get(name).copy();
    }
}
