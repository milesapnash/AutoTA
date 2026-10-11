public class Signer {
    public String sign(String text, String key) {
        return "sig(" + text + "," + key + ")";
    }
}
