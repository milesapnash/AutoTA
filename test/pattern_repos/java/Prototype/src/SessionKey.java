public class SessionKey implements Key {
    private String material;

    public SessionKey(String material) {
        this.material = material;
    }

    @Override
    public Key copy() {
        return new SessionKey(material);
    }
}
