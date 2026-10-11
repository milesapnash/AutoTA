public class Md5Hash implements Hash {
    @Override
    public String digest(String message) {
        return "MD5(" + message + ")";
    }
}
