from hash_function import Hash


class Md5Hash(Hash):
    def digest(self, message):
        return f"MD5({message})"
