public class MasterKey implements Key {
    private String material;
    private int rotations;

    public MasterKey(String material, int rotations) {
        this.material = material;
        this.rotations = rotations;
    }

    @Override
    public Key copy() {
        return new MasterKey(material, rotations);
    }
}
