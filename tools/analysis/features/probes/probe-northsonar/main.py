"""V1 probe: safe random walk, exactly one NORTH sonar per turn, never splits, never sprints."""
import helper as unswbc
from helper import Direction, EdgeType
import random

random.seed(0)


def turn(ct):
    ct.send_sonar(Direction.NORTH, 7)
    here = ct.get_position()
    tile = ct.get_tile(here)
    dirs = Direction.get_direction_list()
    random.shuffle(dirs)
    for d in dirs:
        if tile.get_edge(d).get_edge_type() == EdgeType.KELP:
            continue
        ahead = ct.get_tile(here.add_dir(d))
        if ahead is not None and ahead.get_dragon() is not None:
            continue
        ct.make_move(d)
        return
    ct.make_move(Direction.NORTH)


def main():
    ct, game = unswbc.init()
    while unswbc.update(ct, game):
        turn(ct)
        unswbc.end_turn()


if __name__ == '__main__':
    main()
