"""V1 probe: safe random walk, no sonar, splits a 2-segment child exactly on rounds divisible by 20 when legal."""
import helper as unswbc
from helper import Direction, EdgeType
import random

random.seed(1)


def turn(ct, game):
    if game.get_round_num() % 20 == 0 and ct.can_split(2):
        ct.do_split(2)
        return
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
        turn(ct, game)
        unswbc.end_turn()


if __name__ == '__main__':
    main()
