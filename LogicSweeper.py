"""Self contained file for playing mine sweeper.

This uses a text based interface."""

__author__ = 'Ben T Norman'
##Copyright (c) Ben T Norman
##All Rights Reserved.

import random, itertools, functools, collections
from os import system
clear = lambda :system('cls')

width, height = int(), int()

tiles = list()

mines_to_place, blanks_to_place = int(), int()

seen_blanks, seen_mines = set(), set()
known_mines, known_blanks = set(), set()

perimeter_tiles = set()
tiles_to_satisfy = dict()

class Mine:
    """It's a mine!"""
    pass

def surrounding_tiles(x, y): return ((x+dx, y+dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if (dx != 0 or dy != 0) and 0 <= x+dx < width  and 0 <= y+dy < height)
def convert(x): return chr(x+40)
def decrypt(x): return ord(x.strip())-40

def place_mines(mines_to_place):
    while mines_to_place:
        x, y = random.randint(0, width-1), random.randint(0, height-1)
        if tiles[x][y] is not Mine:
            tiles[x][y] = Mine
            for st_x, st_y in surrounding_tiles(x, y):
                if tiles[st_x][st_y] is not Mine:
                    tiles[st_x][st_y] += 1
            mines_to_place -= 1

def check_tiles(x, y):
    global perimeter_tiles, known_mines, known_blanks
    tile = (x, y)
    if not(tile in seen_mines or tile in seen_blanks):
        if tiles[x][y] is Mine:
            if tile not in known_mines:
                for tile_to_satisfy in filter(lambda t: t in seen_blanks,
                                              surrounding_tiles(x, y)):
                    tiles_to_satisfy[tile_to_satisfy] -= 1
                known_mines.add(tile)
            seen_mines.add(tile)
            perimeter_tiles.discard(tile)
        else:        
            tiles_to_check = list()
            tiles_to_check.append(tile)
            while tiles_to_check:
                tile = tiles_to_check.pop()
                value = tiles[tile[0]][tile[1]]
                if value == 0:
                    for surrounding_tile in surrounding_tiles(*tile):
                        if surrounding_tile not in seen_blanks:
                            tiles_to_check.append(surrounding_tile)
                else:
                    surrounding_mines = 0
                    for st_x, st_y in surrounding_tiles(*tile):
                        if not((st_x, st_y) in known_blanks or (st_x, st_y) in known_mines):
                            perimeter_tiles.add((st_x, st_y))
                        if (st_x, st_y) in known_mines:
                            surrounding_mines += 1
                    tiles_to_satisfy[tile] = value - surrounding_mines
                seen_blanks.add(tile)
                known_blanks.add(tile)
                perimeter_tiles.discard(tile)
    else:
        if tiles[x][y] is Mine:
            seen_mines.add(tile) ##if the tile is in known_... then it should never be in perimeter_tiles
        else:
            seen_blanks.add(tile)

def basic_solve():
    tiles_sated = None
    while tiles_sated != set():
        tiles_sated = set()
        for tile in tiles_to_satisfy:
            mines_needed = tiles_to_satisfy[tile]
            perimeter_tiles_affected = list(filter(lambda t: t in perimeter_tiles,
                                                   surrounding_tiles(*tile)))
            if mines_needed == 0:
                for perimeter_tile in perimeter_tiles_affected:
                    known_blanks.add(perimeter_tile)
                    perimeter_tiles.remove(perimeter_tile)
                tiles_sated.add(tile)

            elif len(perimeter_tiles_affected) == mines_needed:
                for perimeter_tile in perimeter_tiles_affected:
                    known_mines.add(perimeter_tile)
                    perimeter_tiles.remove(perimeter_tile)
                    for tile_to_satisfy in filter(lambda t: t in seen_blanks,
                                                  surrounding_tiles(*perimeter_tile)):
                        tiles_to_satisfy[tile_to_satisfy] -= 1
                tiles_sated.add(tile)
    
        for tile_sated in tiles_sated:
            del tiles_to_satisfy[tile_sated]

def assumption_drive():
    tiles_done = set()
    regions, region_numbers = list(), list()
    while len(tiles_done) != len(tiles_to_satisfy):
        all_that_was_assumed = [[set(), set()],]
        first_tile = next(iter(tiles_to_satisfy.keys() - tiles_done)) 
        tiles_to_do = collections.deque([first_tile,])
        tiles_done.add(first_tile)
        while tiles_to_do:
            tile = tiles_to_do.popleft()
            mines_needed = tiles_to_satisfy[tile]
            tiles_surronding_tile = list(surrounding_tiles(*tile))
            perimeter_tiles_affected = set(filter(lambda t: t in perimeter_tiles,
                                                  tiles_surronding_tile))
            for tile_to_do in filter(lambda t: t in tiles_to_satisfy and t not in tiles_done,
                                     tiles_surronding_tile):
                tiles_done.add(tile_to_do)
                tiles_to_do.append(tile_to_do)

            new_all_that_was_assumed = list()
            for assumed_mines, assumed_blanks in all_that_was_assumed:
                for pending_mines, pending_blanks in filter(lambda m_b: not (m_b[0] & assumed_blanks or m_b[1] & assumed_mines),
                                                            map(lambda mines: (mines, perimeter_tiles_affected - mines),
                                                                map(set,
                                                                    itertools.combinations(perimeter_tiles_affected, mines_needed)
                                                                    )
                                                                )
                                                            ):
                    new_all_that_was_assumed.append((assumed_mines | pending_mines,
                                                     assumed_blanks | pending_blanks))
            all_that_was_assumed = new_all_that_was_assumed

        regions.append(all_that_was_assumed)
        mine_numbers = set()
        for possibility in all_that_was_assumed:
            mine_numbers.add(len(possibility[0]))
        region_numbers.append(mine_numbers)

    invalid_ones = [dict() for _ in range(len(region_numbers))]
    if region_numbers:
        for invalid_numbers in filter(lambda l: sum(l) > mines_to_place or len(perimeter_tiles) - min(l) > blanks_to_place,
               itertools.product(*region_numbers)): ##l is clearly from context not the number one
            for n, invalid_number in enumerate(invalid_numbers):
                if invalid_number not in invalid_ones[n]:
                    invalid_ones[n][invalid_number] = 1
                invalid_ones[n][invalid_number] += 1

    number_of_mines = 1
    for region_number in region_numbers:
        number_of_mines *= len(region_number)
        
    for n, invalid_numbers in enumerate(invalid_ones):
        number_of_possibilities = number_of_mines // len(region_numbers[n])
        for invalid_number in invalid_numbers:
            if invalid_numbers[invalid_number] >= number_of_possibilities:
                for to_remove in filter(lambda possibility: len(possibility[0]) == invalid_number, regions[n]):
                    regions[n].remove(to_remove)

    for region in regions:
        constant_mines, constant_blanks = None, None
        for assumed_mines, assumed_blanks in region:
            if constant_mines is None and constant_blanks is None: ## not needed but ...
                constant_mines, constant_blanks = assumed_mines, assumed_blanks
            else:
                constant_mines &= assumed_mines
                constant_blanks &= assumed_blanks
        yield constant_mines or [], constant_blanks or []

def print_known():
    clear()
    print("  "+"".join(map(str, range(width))))
    for y in range(height):
        line = [str(y)+":"]
        for x in range(width):
            if (x, y) in seen_blanks:
                line.append(str(tiles[x][y]))
            elif (x, y) in seen_mines:
                line.append("m")                
            elif (x, y) in known_mines:
                line.append("T")
            elif (x, y) in known_blanks:
                line.append("F")
            else:
                line.append('_')
        print("".join(line))
    print("Mines Left:", mines_to_place-len(known_mines))    

def print_seen():
    clear()
    print("  "+"".join(map(str, range(width))))
    for y in range(height):
        ##line = [chr(y+40)+":"]
        line = [str(y)+":"]
        for x in range(width):
            if (x, y) in seen_blanks:
                line.append(str(tiles[x][y]))
            elif (x, y) in seen_mines:
                line.append("m")
            else:
                line.append('_')
        print("".join(line))
    print("Mines Left:", mines_to_place-len(seen_mines))

def go(x, y):
    tile = (x, y)
    if tile in seen_blanks or tile in seen_mines:
        print("Tile", x, y, "has already been checked")        
    elif (x, y) in known_mines:
        print("Tile", x, y, "is calculated to be a mine.")
    elif (x, y) in known_blanks:
        print("Tile", x, y, "is calculated to not be a mine.")        
    else:
        print("I don't know the state of tile", x, str(y) + ".")
        if known_blanks - seen_blanks:
            return False

    if not ((x, y) in seen_blanks or (x, y) in seen_mines):        
        check_tiles(x, y)
        print_seen()
        
        basic_solve()

        for calculated_mines, calculated_blanks in assumption_drive():
            for mine in calculated_mines:
                known_mines.add(mine)
                perimeter_tiles.remove(mine)
                for tile_to_satisfy in filter(lambda t: t in seen_blanks,
                                              surrounding_tiles(*mine)):
                    tiles_to_satisfy[tile_to_satisfy] -= 1            
                
            for blank in calculated_blanks:
                known_blanks.add(blank)
                perimeter_tiles.remove(blank)
            
        if perimeter_tiles & (known_mines | known_blanks):
            raise Exception
        if known_mines & known_blanks:
            raise Exception
        if not seen_mines <= known_mines:
            raise Exception
        if not seen_blanks <= known_blanks:
            raise Exception
        for tile in known_mines:
            if tiles[tile[0]][tile[1]] is not Mine:
                raise Exception
        for tile in known_blanks:
            if tiles[tile[0]][tile[1]] is Mine:
                raise Exception
        return True

print("""
[]     OOOOO GGGGGG  IIIIIIIIIII   CCCCCCCCCCCCCC
[]     O   O G           III       CCCC
[]     O   O G  GGG      III       CCCC
[]     O   O G    G      III       CCCC
[][][] OOOOO GGGGGG  IIIIIIIIIII   CCCCCCCCCCCCCC
 SSSS W         WEEEE EEEE PPPPP EEEE RRRRR
S     W    w   W E    E    P   p E    R   R
 SSSS  W   W   W EEE  EEEE PPPPP EEEE RRRRR
     S  W W W W  E    E    P     E    R    R
SSSSs    W   W   EEEE EEEE P     EEEE R     R

The game: it doesn't matter whether it's a mine,
but whether you knew it was a mine or not...""")
input("Press SPACE to continue... ")
clear()

width = abs(int(input('how wide? ') or 10))
height = abs(int(input('how tall? ') or 10))
mines_to_place = abs(int(input('how many mines? ') or 30))
blanks_to_place = width*height - mines_to_place
tiles = [[0 for y in range(height)] for x in range(width)] ##tiles[x][y]
place_mines(mines_to_place)

def main():
    while True:
        i = input("x, y? ")
        if len(i) == 2:
            ##x, y = decrypt(i[0]), decrypt(i[1])
            x, y = int(i[0]), int(i[1])
            if not go(x, y):
                print("In addition, there where non-mines logically deductable...")
                print("as such, you just lost")
                print_known()
                break
            print_seen()
        elif i != "":
            if input("Do you want to quit, y? ").lower() == "y":
                break
    print("GAME OVER")

main()
input()
