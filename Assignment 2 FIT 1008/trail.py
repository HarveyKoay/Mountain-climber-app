from __future__ import annotations
from dataclasses import dataclass

from mountain import Mountain
from personality import PersonalityDecision

from typing import TYPE_CHECKING, Union
from data_structures.linked_stack import LinkedStack

# Avoid circular imports for typing.
if TYPE_CHECKING:
    from personality import WalkerPersonality

@dataclass
class TrailSplit:
    """
    A split in the trail.
       _____top______
      /              \
    -<                >-following-
      \____bottom____/
    """

    top: Trail
    bottom: Trail
    following: Trail

    def remove_branch(self) -> TrailStore:
        """Removes the branch, should just leave the remaining following trail."""
        return self.following.store

@dataclass
class TrailSeries:
    """
    A mountain, followed by the rest of the trail

    --mountain--following--

    """

    mountain: Mountain
    following: Trail

    def remove_mountain(self) -> TrailStore:
        """
        Returns a *new* trail which would be the result of:
        Removing the mountain at the beginning of this series.
        """
        return self.following.store

    def add_mountain_before(self, mountain: Mountain) -> TrailStore:
        """
        Returns a *new* trail which would be the result of:
        Adding a mountain in series before the current one.
        """
        return TrailSeries(mountain, Trail(TrailSeries(self.mountain, self.following)))

    def add_empty_branch_before(self) -> TrailStore:
        """Returns a *new* trail which would be the result of:
        Adding an empty branch, where the current trailstore is now the following path.
        """
        return TrailSplit(Trail(), Trail(), Trail(self))

    def add_mountain_after(self, mountain: Mountain) -> TrailStore:
        """
        Returns a *new* trail which would be the result of:
        Adding a mountain after the current mountain, but before the following trail.
        """
        return TrailSeries(self.mountain, Trail(TrailSeries(mountain, self.following)))
    
    def add_empty_branch_after(self) -> TrailStore:
        """
        Returns a *new* trail which would be the result of:
        Adding an empty branch after the current mountain, but before the following trail.
        """
        return TrailSeries(self.mountain, Trail(TrailSplit(Trail(), Trail(), self.following)))
    
    def maximum_difficulty(self) -> int:
        """Return the maximum difficulty within this series."""
        return max(self.mountain.difficulty_level, self.following.store.maximum_difficulty())

TrailStore = Union[TrailSplit, TrailSeries, None]

@dataclass
class Trail:

    store: TrailStore = None

    def add_mountain_before(self, mountain: Mountain) -> Trail:
        """
        Returns a *new* trail which would be the result of:
        Adding a mountain before everything currently in the trail.
        """
        return Trail(TrailSeries(mountain, self))

    def add_empty_branch_before(self) -> Trail:
        """
        Returns a *new* trail which would be the result of:
        Adding an empty branch before everything currently in the trail.
        """
        return Trail(TrailSplit(Trail(), Trail(), self))

    def follow_path(self, personality: WalkerPersonality) -> None:
        """Follow a path and add mountains according to a personality."""
        Starting = self.store
        current = Starting
        Trace = LinkedStack()
        while current is not None:
            if current.__class__.__name__ == "TrailSeries":
                current = self.follow_series(personality, current)
            
            if current.__class__.__name__ == "TrailSplit":
                current = self.follow_split(personality, Trace, current)
            
            while current is None and not Trace.is_empty():
                current = Trace.pop()

        
    def follow_split(self, personality, stack, current):
        decision = personality.select_branch(current.top, current.bottom)
        stack.push(current.remove_branch())

        if decision == PersonalityDecision.TOP:
            current = current.top.store 
        elif decision == PersonalityDecision.BOTTOM:
            current = current.bottom.store
        elif decision == PersonalityDecision.STOP:
            stack.clear()
            current = None

        return current

    def follow_series(self, personality, current):
        personality.add_mountain(current.mountain)
        return current.remove_mountain()

    def collect_all_mountains(self) -> list[Mountain]:
        """Returns a list of all mountains on the trail."""
        mountains = []

        # Start from the beginning of the trail
        current = self.store

        while current is not None:
            if isinstance(current, TrailSeries):
                # If it's a series, add the mountain to the list and move to the next
                mountains.append(current.mountain)
                current = current.following.store
            elif isinstance(current, TrailSplit):
                # If it's a split, explore both branches
                mountains.extend(current.top.collect_all_mountains())
                mountains.extend(current.bottom.collect_all_mountains())
                current = current.following.store

        return mountains



    def difficulty_maximum_paths(self, diff: int) -> list[list[Mountain]]:
        """Find all paths through the trail with a maximum difficulty not exceeding 'diff'."""
        paths = []
        trace = LinkedStack()

        def dfs(current, trace, current_path):
            trace = self.copy_stack(trace)
            if current is None:
                if trace.is_empty():
                    paths.append(current_path.copy())
                else:
                    dfs(trace.pop(), trace, current_path)

            # Check if we have reached a mountain (TrailSeries)
            elif isinstance(current, TrailSeries):
                if current.mountain.difficulty_level < diff:
                    current_path.append(current.mountain)
                    dfs(current.following.store, trace, current_path)

            # Check if we have reached a split (TrailSplit)
            elif isinstance(current, TrailSplit):
                trace.push(current.following.store)
                # Explore the top branch
                dfs(current.top.store, trace, current_path.copy())
                # Explore the bottom branch
                dfs(current.bottom.store, trace, current_path.copy())


        # Initial call to the DFS
        dfs(self.store, trace, [])

        return paths
    
    def copy_stack(self, stack):
        # Have to copy the stack because it is a reference type.
        # Thus creating a new stack with the same values.
        copy = LinkedStack()
        temp = LinkedStack()
        while not stack.is_empty():
            temp.push(stack.pop())
        while not temp.is_empty():
            trail = temp.pop()
            stack.push(trail)
            copy.push(trail)
        
        return copy
    
    # def difficulty_difference_paths(self, max_difference: int) -> list[list[Mountain]]: # Input to this should not exceed k > 50, at most 5 branches.
    #     # 1054 ONLY!
    #     raise NotImplementedError()
