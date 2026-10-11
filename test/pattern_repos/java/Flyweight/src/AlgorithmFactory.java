import java.util.HashMap;
import java.util.Map;

public class AlgorithmFactory {
    private Map<String, CipherAlgorithm> pool = new HashMap<>();

    public CipherAlgorithm get(String name) {
        if (!pool.containsKey(name)) {
            pool.put(name, new NamedAlgorithm(name));
        }
        return pool.get(name);
    }
}
