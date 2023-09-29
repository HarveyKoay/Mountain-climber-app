from __future__ import annotations
from typing import Generic, TypeVar

from data_structures.referential_array import ArrayR
from data_structures.hash_table import LinearProbeTable, FullError

K = TypeVar("K")
V = TypeVar("V")
List = TypeVar("List")

class InfiniteHashTable(Generic[K, V]):
    """
    Infinite Hash Table.

    Type Arguments:
        - K:    Key Type. In most cases should be string.
                Otherwise `hash` should be overwritten.
        - V:    Value Type.

    Unless stated otherwise, all methods have O(1) complexity.
    """

    TABLE_SIZE = 27

    def __init__(self) -> None:
        self.array = ArrayR(InfiniteHashTable.TABLE_SIZE)
        self.level = 0
        self.count = 0


    def hash(self, key: K) -> int:
        if self.level < len(key):
            return ord(key[self.level]) % (self.TABLE_SIZE-1)
        return self.TABLE_SIZE-1
    
    def probe(self, key: K, is_insert) -> int:
        """
        Probe to get the position in the hash table. 
        """
        self.level = 0
        position = self.hash(key)
        current = self.array[position]

        location = []
        # if current is not none, means we have a collision
        while current is not None:
            location.append(position)
            # if current is a tuple, means we have a key, value pair
            if isinstance(current, tuple):
                if current[0] == key or is_insert:
                    return location 
                else:
                    raise KeyError(key)
            
            # if it is not a tuple, means we have to get second hash
            self.level += 1
            position = self.hash(key)
            # update the current to second level
            current = current[position]

        if is_insert:
            location.append(position)
            return location
        else:
            raise KeyError(key)


    def __getitem__(self, key: K) -> V:
        """
        Get the value at a certain key

        :raises KeyError: when the key doesn't exist.
        """
        lst_of_pos = self.probe(key, False)
        table = self.array
        for index in lst_of_pos:
            table = table[index]
        
        return table[1]

    def __setitem__(self, key: K, value: V) -> None:
        """
        Set an (key, value) pair in our hash table.
        """
        lst_of_pos = self.probe(key, True)
        table = self.array

        # move to the second last table of the whole list
        for index in lst_of_pos[:-1]:
            table = table[index]
        
        # store the next position
        next_level = lst_of_pos[-1]

        # if the last position is none, means we have a new key, value pair
        if table[next_level] is None:
            table[next_level] = (key, value)
            self.count += 1
            return
        #if the last position is a tuple, check if it is the same key
        else:
            if table[next_level][0] == key:
                table[next_level] = (key, value)
                return
                #if it is already occupied, we have to move to the next level
            else:
                collision = table[next_level]
                collision_key = collision[0]

                while self.hash(collision_key) == self.hash(key):
                    self.level += 1
                    table[next_level] = ArrayR(InfiniteHashTable.TABLE_SIZE)
                    table = table[next_level]
                    next_level = self.hash(key)
                
                table[next_level] = (key, value)
                collision_position = self.hash(collision_key)
                table[collision_position] = collision
                self.count += 1
        

    def __delitem__(self, key: K) -> None:
        """
        Deletes a (key, value) pair in our hash table.

        :raises KeyError: when the key doesn't exist.
        """
        lst_of_pos = self.probe(key, False)
        table = self.array
        for index in lst_of_pos[:-1]:
            table = table[index]
        
        next_level = lst_of_pos[-1]

        if table[next_level] is None:
            raise KeyError(key)
        else:
            table[next_level] = None
            self.count -= 1

        self.lower_level(table, lst_of_pos)
    

    def lower_level(self, table, lst_of_pos) -> None:
        count = 2
        tuple_list, has_another_array = self.status(table)
        while len(tuple_list) == 1 and not has_another_array and count < len(lst_of_pos):
            table = self.array   
            for pos in lst_of_pos[:-count]:
                table = table[pos]

            table[lst_of_pos[-count]] = tuple_list[0]

            tuple_list, has_another_array = self.status(table)

            count += 1 

        if len(tuple_list) == 1 and not has_another_array:
            self.array[lst_of_pos[0]] = tuple_list[0]
        


    def status(self, array) -> tuple[list[tuple], bool]:
        """
        Return the status of the hash table.
        """

        has_another_array = False
        lst = []
        for item in array:
            if isinstance(item, tuple):
                lst.append(item)
            elif isinstance(item, ArrayR):
                has_another_array = True
        
        return (lst, has_another_array)


    def __len__(self) -> int:
        return self.count

    def __str__(self) -> str:
        """
        String representation.

        Not required but may be a good testing tool.
        :complexity: O(n), where n is the number of items in the list.
        """
        return (self.get_items(self.array))

    def get_items(self, array: ArrayR) -> list[K]:
        """
        String representation.

        Not required but may be a good testing tool.
        :complexity: O(n), where n is the number of items in the list.
        """
        item_list = list()

        def helper(sub_array: ArrayR) -> list[K]:
            for item in sub_array:
                if isinstance(item, ArrayR):
                    helper(item)  # Recurse into the nested list
                else:
                    if item is not None:
                        item_list.append(item)
        helper(array)
        return str(item_list)

    def get_location(self, key: K) -> List[int]:
        return self.probe(key, False)

    def __contains__(self, key: K) -> bool:
        """
        Checks to see if the given key is in the Hash Table

        :complexity: See linear probe.
        """
        try:
            _ = self[key]
        except KeyError:
            return False
        else:
            return True

    def sort_keys(self, current=None) -> list[str]:
        """
        Returns all keys currently in the table in lexicographically sorted order.
        """
        lst = []
        
        def collect_keys(array):
            if array[self.TABLE_SIZE-1] is not None:
                lst.append(array[self.TABLE_SIZE-1][0])

            i = ord('a') % (self.TABLE_SIZE-1)
            for _ in range((self.TABLE_SIZE)-1):
                if isinstance(array[i], ArrayR):
                    collect_keys(array[i])
                elif array[i] is not None:
                    lst.append(array[i][0])

                i = (i+1) % (self.TABLE_SIZE-1)

        collect_keys(self.array)
        return lst








