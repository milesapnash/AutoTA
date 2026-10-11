public class Sha256Hash implements Hash {
    @Override
    public String digest(String message) {
        return "SHA256(" + message + ")";
    }
}
