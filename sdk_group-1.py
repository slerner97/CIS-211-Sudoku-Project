"""
A "group" is a collection of 9 Sudoku tiles, which
may form a row, a column, or a block (aka 'region'
or 'box').
AUTHOR: SAM LERNER

Constraint propagation are localized here.
"""
import typing
from typing import Sequence

import sdk_tile

import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class Group(object):
    """A group of 9 Sudoku tiles"""

    def __init__(self, title: str):
        """Intially empty.  The title is just for debugging."""
        self.title = title
        self.tiles: Sequence[sdk_tile.Tile] = []

    def add(self, tile: sdk_tile.Tile):
        """Add a tile to this group"""
        assert len(self.tiles) < 9
        self.tiles.append(tile)

    def __str__(self):
        """Represent as string of values"""
        values = []
        for tile in self.tiles:
            values.append(tile.value)
        return self.title + " " + "".join(values)

    def attend(self):
        """Announce that we are working on these tiles.  A view component
        may make this visible.
        """
        for tile in self.tiles:
            tile.attend()

    def unattend(self):
        """Announce that we are done working on these tiles for now"""
        for tile in self.tiles:
            tile.unattend()

    def is_complete(self) -> bool:
        """A group is complete if all of its tiles hold a
        value (not the wild-card symbol UNKNOWN)
        """
        for tile in self.tiles:
            if tile.value == sdk_tile.UNKNOWN:
                return False
        return True

    def is_consistent(self) -> bool:
        """A group is consistent if it has no duplicates,
        every tile has at least one candidate, and
        every value has a place to go.
        """
        can_place = set()
        used = set()
        for tile in self.tiles:
            # At least one candidate?
            if len(tile.candidates) == 0:
                log.debug("No candidates for tile {},{}:{}"
                          .format(tile.row, tile.col, tile.value))
                return False
            # Duplicate checking
            if tile.value in used:
                # Duplicate!
                log.debug("Tile {},{}:{} is a duplicate"
                          .format(tile.row, tile.col, tile.value))
                return False
            elif tile.value != sdk_tile.UNKNOWN:
                used.add(tile.value)
            # A place for every tile?
            can_place = can_place | tile.candidates
        if can_place != set(sdk_tile.CHOICES):
            log.debug("Group {}, no place for {}"
                      .format(self, set(sdk_tile.CHOICES) - can_place))
        return can_place == set(sdk_tile.CHOICES)

    def duplicates(self) -> Sequence[str]:
        """One line report per duplicate found"""
        reports = []
        used = set()
        for tile in self.tiles:
            if tile.value == sdk_tile.UNKNOWN:
                continue
            elif tile.value in used:
                reports.append("Duplicate in {}: {}, value {}"
                               .format(self.title, self, tile.value))
        return reports

    # ---------------------------------
    # Constraint propagation in a group
    # ----------------------------------
    def naked_single_constrain(self) -> bool:
        """A choice can be used at most once in the group."""
        self.attend()
        changed = False
        list = set([])
        for item in self.tiles:
            if item.value != sdk_tile.UNKNOWN:
                list.append(item.value)
        for item in self.tiles:
            if item.value == sdk_tile.UNKNOWN:
                changed = tile.eliminate(list) or changed
        self.unattend()
        return changed

    def hidden_single_constrain(self) -> bool:
        """Each choice must be used in the group"""
        self.attend()
        changed = False
        left = set(['1','2', '3', '4', '5', '6', '7', '8', '9'])
        for tile in self.tiles:
            left -= set(tile.value)
        for value in left:
            place = []
            #comparing with left
            for tile in self.tiles:
                if tile.could_be(value) == True:
                    place.append(tile)
            if len(place) == 1:
                place.pop().set_value(value)
                changed = True

        self.unattend()
        return changed
