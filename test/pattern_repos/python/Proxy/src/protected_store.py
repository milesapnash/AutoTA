from secret_store import SecretStore
from vault_store import VaultStore


class ProtectedStore(SecretStore):
    def __init__(self, authorised):
        self._vault: VaultStore = None
        self._authorised = authorised

    def read(self, secret_id):
        if not self._authorised:
            raise PermissionError("Access denied")
        if self._vault is None:
            self._vault = VaultStore()
        return self._vault.read(secret_id)
