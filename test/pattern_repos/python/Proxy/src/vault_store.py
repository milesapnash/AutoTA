from secret_store import SecretStore


class VaultStore(SecretStore):
    def read(self, secret_id):
        return f"secret:{secret_id}"
