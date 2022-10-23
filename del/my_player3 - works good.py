import os
import copy
import random
import numpy as np

from host import GO

BOARD_SIZE = 5
INPUT = 'input.txt'
OUTPUT = 'output.txt'
test_input = "test_input.txt"

class Go:
    def __init__(self, n):
        """
        Class to setup the board and describe the rules and moves of the mini (5x5) Go game.
        :param n: the board size
        """
        self.size = n
        self.X_move = True  # True means X plays first, otherwise O plays first
        self.died_pieces = []  # a list to keep track of the died pieces once an opponent has made it's move
        self.n_move = 0  # variable to keep track of  the number of current moves in the game
        self.max_move = (n * n) - 1  # maximum number of moves allowed as per the given rule book
        self.komi = n / 2  # initialize the Komi rule

        self.previous_board = None

class MinMax:
    def __init__(self, n):
        self.size = n
        self.type = 'min-max agent'
        self.piece_type = None

        self.max_depth = 2
        self.encode_state = None

        self.possible_moves = []

    def read_input(self, path):
        with open(path, 'r') as f:
            lines = f.readlines()
            get_piece_type = int(lines[0])
            get_previous_board = [[int(char) for char in line.rstrip('\n')] for line in lines[1: self.size+1]]
            get_current_board = [[int(x) for x in line.rstrip('\n')] for line in lines[self.size+1: 2*self.size + 1]]

            return get_piece_type, get_previous_board, get_current_board

    def write_output(self, result, path="output.txt"):
        res = ""
        if result == "PASS":
            res = "PASS"
        else:
            res += str(result[0]) + ',' + str(result[1])

        with open(path, 'w') as f:
            f.write(res)

    def find_open_liberty(self, board_state, i, j):
        # function to find the open liberty for a given coordinate
        board = board_state.board
        get_ally_members = board_state.ally_dfs(i, j)
        liberty_set = set()
        for member in get_ally_members:
            neighbors = board_state.detect_neighbor(member[0], member[1])
            for guy in neighbors:
                if board[guy[0]][guy[1]] == 0:
                    liberty_set.add(guy)

        open_liberty = len(liberty_set)
        return open_liberty

    def heuristic_function(self, board_state, opponent):
        player_1 = 0
        player_2 = 0
        eval_player_1 = 0
        eval_player_2 = 0

        for i in range(self.size):
            for j in range(self.size):
                if board_state.board[i][j] == self.piece_type:
                    player_1 = player_1 + 1
                    liberty_player_1 = self.find_open_liberty(board_state, i, j)
                    eval_player_1 = eval_player_1 + player_1 + liberty_player_1
                elif board_state.board[i][j] == 3 - self.piece_type:
                    player_2 = player_2 + 1
                    liberty_player_2 = self.find_open_liberty(board_state, i, j)
                    eval_player_2 = eval_player_2 + player_2 + liberty_player_2

        resultant_eval = eval_player_1 - eval_player_2
        if opponent == self.piece_type:
            return resultant_eval

        return -1 * resultant_eval

    def min_max(self, agent_board, max_depth, alpha=-np.inf, beta=-np.inf):
        get_best_moves = []
        best = 0
        agent_board_new = copy.deepcopy(agent_board)

        for move in self.possible_moves:
            next_board_state = copy.deepcopy(agent_board)
            next_board_state.place_chess(move[0], move[1], self.piece_type)

            # Remove the dead pieces of opponent after our move
            next_board_state.died_pieces = next_board_state.remove_died_pieces(3 - self.piece_type)

            get_heur_value = self.heuristic_function(next_board_state, 3 - self.piece_type)
            evaluation = self.min_max2(next_board_state, max_depth,
                                         alpha, beta, get_heur_value, 3 - self.piece_type)

            curr_score = -1 * evaluation

            # check if moves is empty or if we have new best move(s)
            if curr_score > best or not get_best_moves:
                best = curr_score
                alpha = best
                get_best_moves = [move]
            # if we have another best move then we add to the moves list
            elif curr_score == best:
                get_best_moves.append(move)

        return get_best_moves

    # the second minimax 'helper' function that iterates through the branches
    def min_max2(self, curr_board, max_depth, alpha, beta, heur, next_player):
        if max_depth == 0:
            return heur
        best = heur

        curr_board_copy = copy.deepcopy(curr_board)

        new_possible_moves = []
        for i in range(curr_board.size):
            for j in range(curr_board.size):
                if curr_board.valid_place_check(i, j, next_player, test_check=True):
                    new_possible_moves.append((i, j))
        # iterate through all valid moves
        for move in new_possible_moves:
            # update the next board state
            next_state = copy.deepcopy(curr_board)
            next_state.place_chess(move[0], move[1], 3 - next_player)

            # Remove the dead pieces of opponent after our move
            next_state.died_pieces = next_state.remove_died_pieces(3 - self.piece_type)

            # get heuristic of next state
            heur = self.heuristic_function(next_state, 3 - next_player)
            evaluation = self.min_max2(next_state, max_depth - 1,
                                       alpha, beta, heur, 3 - next_player)

            curr_score = -1 * evaluation
            # check if new result is better than current best
            if curr_score > best:
                best = curr_score
            # update the score
            new_score = -1 * best

            # Alpha beta pruning
            # if we are looking at the minimizing player (opponent)
            if next_player == 3 - self.piece_type:
                this_player = new_score
                # check if prune
                if this_player < alpha:
                    return best
                # if we dont prune, update beta
                if best > beta:
                    beta = best
            # if we are looking at the maximizing player (ourselves)
            elif next_player == self.piece_type:
                opponent = new_score
                # check prune
                if opponent < beta:
                    return best
                # if we dont prune, update alpha
                if best > alpha:
                    alpha = best

        return best

    def get_input(self, go_board, piece):
        # set the player's piece type
        self.piece_type = piece

        # check if the game is still on
        if go_board.game_end(self.piece_type):
            return 'Game Over!!'

        # first get all the possible moves available on the board
        self.possible_moves = []
        for i in range(go_board.size):
            for j in range(go_board.size):
                if go_board.valid_place_check(i, j, self.piece_type, test_check=True):
                    self.possible_moves.append((i, j))

        if not self.possible_moves:
            return 'PASS'
        else:
            self.encode_state = ''.join(
                [str(go_board.board[i][j]) for i in range(go_board.size) for j in range(go_board.size)])

            if self.encode_state == "0000000000000000000000000" and self.piece_type == 1:
                action = (2, 2)
                return action
            else:
                max_depth = self.max_depth
                action = self.min_max(go_board, max_depth, alpha=-np.inf, beta=-np.inf)

                if not action:
                    return "PASS"
                else:
                    action = random.choice(action)
                    return action


if __name__ == '__main__':
    board_size = 5
    set_path = os.path.join("input.txt")
    player = MinMax(board_size)
    game_board = GO(board_size)
    piece_type, previous_board, current_board = player.read_input(set_path)
    game_board.set_board(piece_type, previous_board, current_board)
    get_action = player.get_input(game_board, piece_type)
    player.write_output(get_action)




