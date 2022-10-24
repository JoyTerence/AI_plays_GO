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

    def get_all_valid_moves(self, go, player):
        possible_placements = []
        for i in range(go.size):
            for j in range(go.size):
                if go.valid_place_check(i, j, player, test_check = True):
                    possible_placements.append((i,j))
        return possible_placements

    def open_liberty(self, go, i, j):
        ally_members = go.ally_dfs(i, j)
        liberty = set()
        for ally in ally_members:
            neighbors = go.detect_neighbor(ally[0], ally[1])
            for neighbor in neighbors:
                if go.board[neighbor[0]][neighbor[1]] == 0:
                    liberty.add(neighbor)
            
        return len(liberty)

    def evaluation_fn(self, go, player):
        player1_pieces, player2_pieces = 0, 0
        player1_score, player2_score = 0, 0

        for i in range(go.size):
            for j in range(go.size):
                if go.board[i][j] == player:
                    player1_pieces += 1
                    player1_score += player1_pieces + self.open_liberty(go, i, j)
                elif go.board[i][j] == self.get_opponent(player):
                    player2_pieces += 1
                    player2_score += player2_pieces + self.open_liberty(go, i, j)
        
        if player == self.piece_type:
            return player1_score - player2_score
        
        return player2_score - player1_score

    def begin_search(self, go, max_depth, alpha, beta):
        best_moves = []
        score = 0

        valid_moves = self.get_all_valid_moves(go, self.piece_type)

        opponent = self.get_opponent()

        for move in valid_moves:
            go.place_chess(move[0], move[1], self.piece_type)
            go.died_places = go.remove_died_pieces(opponent)

            score_after_our_move = self.evaluation_fn(go, opponent)
            #print("begin_search: score_after_our_move", score_after_our_move)
            score_after_opp_move = self.min(go, score_after_our_move, alpha, beta, max_depth)
            #print("begin_search: score_after_opp_move, score", score_after_opp_move, score)

            curr = -1 * score_after_opp_move
            if curr >= score:
                score = curr
                alpha = score
                best_moves.append(move)

        return best_moves

    def max(self, go, score, alpha, beta, max_depth):
        v = -math.inf
        if max_depth == 0:
            return score
        max_depth -= 1

        valid_moves = self.get_all_valid_moves(go, self.piece_type)

        for move in valid_moves:
            go.place_chess(move[0], move[1], self.piece_type)
            go.remove_died_pieces(self.get_opponent())

            score_after_our_move = self.evaluation_fn(go, self.get_opponent())
            # #print("max: score_after_our_move", score_after_our_move)
            score_after_opponent_move = self.min(go, score_after_our_move, alpha, beta, max_depth)
            # #print("max: score_after_opponent_move", score_after_opponent_move)
            v = max(v, -1 * score_after_opponent_move)

            if v >= beta:
                return v

            alpha = max(alpha, v)

        return v

    def min(self, go, score, alpha, beta, max_depth):
        v = math.inf
        if max_depth == 0: 
            return score
        max_depth -= 1

        valid_moves = self.get_all_valid_moves(go, self.get_opponent())

        for move in valid_moves:
            go.place_chess(move[0], move[1], self.get_opponent())
            go.remove_died_pieces(self.piece_type)

            score_after_opponent_move = self.evaluation_fn(go, self.get_opponent())
            # #print("min: score_after_opponent_move", score_after_opponent_move)
            score_after_our_move = self.max(go, score_after_opponent_move, alpha, beta, max_depth)
            #print("min: score_after_our_move", score_after_our_move, "v", v, "alpha", alpha)

            v = min(v, -1 * score_after_our_move)
            if v <= alpha:
                return v

            beta = min(alpha, v)
        return v

    def get_input(self, go, piece_type):
        self.piece_type = piece_type
        possible_placements = self.get_all_valid_moves(go, self.piece_type)
        size = go.size

        if not possible_placements:
            return "PASS"
        else:
            serialized = ''.join([str(go.board[i][j]) for i in range(size) for j in range(size)])
            if serialized == "0" * 25 and self.piece_type == 1:
                return (2, 2)
            else:
                next_moves = self.begin_search(go, self.max_depth, alpha=-math.inf, beta=math.inf)

                #print(next_moves)
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
    #print("HERE", action)
    writeOutput(action)