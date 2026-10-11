import java.util.ArrayList;
import java.util.List;

public class CipherPipeline implements CryptoStep {
    private List<CryptoStep> steps = new ArrayList<>();

    public void add(CryptoStep step) {
        steps.add(step);
    }

    @Override
    public String apply(String text) {
        for (CryptoStep step : steps) {
            text = step.apply(text);
        }
        return text;
    }
}
