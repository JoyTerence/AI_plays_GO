import random
from read import readInput
from write import writeOutput
import math
from host import GO

class MyPlayer():
    def __init__(self):
        self.type = 'min-max alpha-beta agent'
        self.possible_placements = []
        self.piece_type = None
        self.max_depth = 2

    def get_opponent(self, player = None):
        if not player:
            return 3 - self.piece_type
        else:
            return 3 - player

    def max(self, state, alpha, beta, max_depth):
        best_moves = []
        v = 0
        for move in self.possible_placements:
            state.place_chess(move[0], move[1], self.piece_type)
            state.remove_died_pieces(self.get_opponent())

            score_after_our_move = self.evaluation_fn(state, self.get_opponent())
            score_after_opponent_move = self.min(state, score_after_our_move, alpha, beta, max_depth, self.get_opponent())

            result = self.evaluation_fn(move)

            if result >= v:
                v = result
                best_moves.append(move)
                alpha = max(alpha, v)

        return v, best_moves

    def min(self, state, score, alpha, beta, max_depth, opponent):

        if max_depth == 0: return score
        else:
            max_depth -= 1

        v = 0

        next_moves = []

        for i in range(state.size):
            for j in range(state.size):
                if state.valid_place_check(i, j, opponent, True):
                    next_moves.append((i, j))
        for move in next_moves:
            state.place_chess(move[0], move[1], self.get_opponent(opponent))
            state.remove_died_pieces(self.get_opponent())

            score_after_opponent_move = self.evaluation_fn(state, self.get_opponent(opponent))
            score_after_our_move = self.max(score_after_opponent_move, alpha, beta, max_depth, state)

            if score_after_our_move >= v:
                v = score_after_our_move

            if v <= alpha:
                return v
            beta = min(alpha, v)
        return v

    def evaluation_fn(self, state, opponent):
        player1_pieces, player2_pieces = 0, 0
        player1_score, player2_score = 0, 0

        for i in range(self.size):
            for j in range(self.size):
                if state.board[i][j] == self.piece_type:
                    player1_pieces += 1
                    player1_score += player1_pieces + self.open_liberty()
                elif state.board[i][j] == (self.get_opponent()):
                    player2_pieces += 1
                    player2_score += player2_pieces + self.open_liberty()
        
        if opponent == self.piece_type:
            return player1_score - player2_score
        else:
            return player2_score - player1_score

    def get_input(self, go, piece_type):
        '''
        Get one input.

        :param go: Go instance.
        :param piece_type: 1('X') or 2('O').
        :return: (row, column) coordinate of input.
        '''
        for i in range(go.size):
            for j in range(go.size):
                if go.valid_place_check(i, j, piece_type, test_check = True):
                    self.possible_placements.append((i,j))

        if not self.possible_placements:
            return "PASS"
        else:
            serialized = ''.join([str(a) for a in go for b in a])
            if serialized == "0" * 25 and self.piece_type == 1:
                return (2, 2)
            else:
                next_moves = self.max(go, self.max_depth, alpha=-math.inf, beta=math.inf)

                if next_moves:
                    return random.choice(next_moves)
                else:
                    return "PASS"

if __name__ == "__main__":
    N = 5
    piece_type, previous_board, board = readInput(N)
    go = GO(N)
    go.set_board(piece_type, previous_board, board)
    player = MyPlayer()
    action = player.get_input(go, piece_type)
    writeOutput(action)