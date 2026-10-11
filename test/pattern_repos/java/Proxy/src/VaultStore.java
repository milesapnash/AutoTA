public class VaultStore implements SecretStore {
    @Override
    public String read(String id) {
        return "secret:" + id;
    }
}
