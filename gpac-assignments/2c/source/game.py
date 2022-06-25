""" Module that allows one to play the pacman game as implemented in gpac for testing and fun. """
import random
import gpac

import utilities

getch = utilities.Getch()


def convert_move(raw_input):
    """ Convert move into cardinal directions """

    if raw_input == 'w':
        return gpac.UP
    if raw_input == 'a':
        return gpac.LEFT
    if raw_input == 'd':
        return gpac.RIGHT
    if raw_input == 's':
        return gpac.DOWN
    if raw_input == ' ':
        return gpac.HOLD
    return None


def play(map_filepath):
    """ Plays game in an interactive terminal. Players control Pac-Man
    while ghosts randomly move about.
    """

    game = gpac.GPac(map_filepath, .01, 0, 0, 10)
    ghosts = gpac.GHOST
    score = None

    game.print_board()
    while not game.is_gameover:
        pacman_moves = game.get_moves_for_unit(gpac.PACMAN)
        pacman_move = None
        while pacman_move not in pacman_moves:
            pacman_move_raw = getch()
            pacman_move = convert_move(pacman_move_raw)
        game.move(pacman_move, gpac.PACMAN)

        for ghost in ghosts:
            ghosts_moves = random.choice(game.get_moves_for_unit(ghost))
            game.move(ghosts_moves, ghost)

        score, _ = game.turn()
        game.print_board()

    print("Game Over! Score: ", score)


if __name__ == "__main__":
    play('maps/map0.txt')
