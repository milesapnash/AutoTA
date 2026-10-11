from key import Key


class MasterKey(Key):
    def __init__(self, material, rotations):
        self._material = material
        self._rotations = rotations

    def copy(self) -> Key:
        return MasterKey(self._material, self._rotations)
