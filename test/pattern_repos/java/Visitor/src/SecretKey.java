public class SecretKey implements CryptoItem {
    private String material;

    public SecretKey(String material) {
        this.material = material;
    }

    public String getMaterial() {
        return material;
    }

    @Override
    public void accept(ItemVisitor visitor) {
        visitor.visitKey(this);
    }
}
