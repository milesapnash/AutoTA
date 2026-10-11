from secure_channel import SecureChannel


class TextChannel(SecureChannel):
    def transmit(self, data):
        return "text:" + self._cipher.apply(data)
