class LegacyScrambler:
    def scramble(self, text, rounds):
        for _ in range(rounds):
            text = text[::-1]
        return text
