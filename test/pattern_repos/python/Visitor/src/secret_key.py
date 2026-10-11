from crypto_item import CryptoItem
from item_visitor import ItemVisitor


class SecretKey(CryptoItem):
    def __init__(self, material):
        self._material = material

    def get_material(self):
        return self._material

    def accept(self, visitor: ItemVisitor):
        visitor.visit_key(self)
