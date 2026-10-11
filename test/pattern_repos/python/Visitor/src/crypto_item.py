from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from item_visitor import ItemVisitor


class CryptoItem(ABC):
    @abstractmethod
    def accept(self, visitor: "ItemVisitor"):
        pass
