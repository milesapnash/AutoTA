from crypto_item import CryptoItem
from item_visitor import ItemVisitor


class Certificate(CryptoItem):
    def __init__(self, subject, days_valid):
        self._subject = subject
        self._days_valid = days_valid

    def get_subject(self):
        return self._subject

    def get_days_valid(self):
        return self._days_valid

    def accept(self, visitor: ItemVisitor):
        visitor.visit_certificate(self)
