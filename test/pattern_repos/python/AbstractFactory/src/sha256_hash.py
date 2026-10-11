from hash_function import Hash


class Sha256Hash(Hash):
    def digest(self, message):
        return f"SHA256({message})"
