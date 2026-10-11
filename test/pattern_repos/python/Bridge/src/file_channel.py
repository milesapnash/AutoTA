from secure_channel import SecureChannel


class FileChannel(SecureChannel):
    def transmit(self, data):
        return "file:" + self._cipher.apply(data)
