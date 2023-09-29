from __future__ import annotations
from mountain import Mountain
from double_key_table import DoubleKeyTable
from algorithms.mergesort import mergesort

class MountainManager:

    def __init__(self) -> None:
        self.mountains = DoubleKeyTable()

    def add_mountain(self, mountain: Mountain) -> None:
        self.mountains[mountain.difficulty_level, mountain.name] = mountain

    def remove_mountain(self, mountain: Mountain) -> None:
        del self.mountains[mountain.difficulty_level, mountain.name]

    def edit_mountain(self, old: Mountain, new: Mountain) -> None:
        self.remove_mountain(old)
        self.add_mountain(new)

    def mountains_with_difficulty(self, diff: int) -> list[Mountain]:
        mount_list = []
        try:
            mount_list = self.mountains.values(diff)
        except:
            pass
        return mount_list

    def group_by_difficulty(self) -> list[list[Mountain]]:
        mount_list = []
        lst_of_keys = mergesort(self.mountains.keys(), key=lambda x: x[0])
        for i in range(len(lst_of_keys)):
            mount_list.append(self.mountains.values(lst_of_keys[i]))
        return mount_list