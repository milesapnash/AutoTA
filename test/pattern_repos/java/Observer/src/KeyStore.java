import java.util.ArrayList;
import java.util.List;

public class KeyStore {
    private List<KeyObserver> observers = new ArrayList<>();
    private String key;

    public void attach(KeyObserver observer) {
        observers.add(observer);
    }

    public void detach(KeyObserver observer) {
        observers.remove(observer);
    }

    public void setKey(String key) {
        this.key = key;
        notifyObservers();
    }

    private void notifyObservers() {
        for (KeyObserver observer : observers) {
            observer.update(key);
        }
    }
}
