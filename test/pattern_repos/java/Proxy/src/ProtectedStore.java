public class ProtectedStore implements SecretStore {
    private VaultStore vault;
    private boolean authorised;

    public ProtectedStore(boolean authorised) {
        this.authorised = authorised;
    }

    @Override
    public String read(String id) {
        if (!authorised) {
            throw new SecurityException("Access denied");
        }
        if (vault == null) {
            vault = new VaultStore();
        }
        return vault.read(id);
    }
}
