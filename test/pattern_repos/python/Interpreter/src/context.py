class Context:
    def __init__(self, text):
        self._text = text

    def get_text(self):
        return self._text

    def set_text(self, text):
        self._text = text
