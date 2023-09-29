from __future__ import annotations

from mountain import Mountain
from double_key_table import DoubleKeyTable
from algorithms.mergesort import mergesort
from algorithms.binary_search import binary_search
from data_structures.referential_array import ArrayR

class MountainOrganiser:
    def __init__(self) -> None:
        self.array  = DoubleKeyTable()
        self.mountain_storage = []

    def cur_position(self, mountain: Mountain) -> int:
        if (mountain.difficulty_level, mountain.name) not in self.organised:
            raise KeyError("Mountain not found.")
        return binary_search(self.organised, (mountain.difficulty_level, mountain.name))
            
    def add_mountains(self, mountains: list[Mountain]) -> None:
        for _ in range(len(self.mountain_storage)):
            item = self.mountain_storage.pop()
            mountains.append(item)
        
        self.organised = []
        mountains = mergesort(mountains, key=lambda x: x.difficulty_level)

        for mountain in mountains:
            self.mountain_storage.append(mountain)
            self.array[str(mountain.difficulty_level), str(mountain.name)] = mountain
        
        external_array = []
        internal_array = []
        for key in self.array.keys():
            if len(self.array.keys(key)) > 1:
                internal_array.extend(self.array.values(key))
                external_array.append(internal_array)
                internal_array = []

        new_array = []
        for internal_array in external_array:
            internal_array = mergesort(internal_array, key=lambda x: x.name)
            new_array.append(internal_array)
        
        for _ in range(len(mountains)):
            if new_array != []:
                if mountains[0].difficulty_level == new_array[0][0].difficulty_level or new_array == []:
                    mountains.pop(0)
                    mountain = new_array[0].pop(0)
                    self.organised.append((mountain.difficulty_level, mountain.name))
                    if len(new_array[0]) == 0:
                        new_array.pop(0)
                else:
                    mountain = mountains.pop(0)
                    self.organised.append((mountain.difficulty_level, mountain.name))
            else:
                mountain = mountains.pop(0)
                self.organised.append((mountain.difficulty_level, mountain.name))
        