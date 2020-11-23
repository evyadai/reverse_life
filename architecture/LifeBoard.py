import numpy as np
import itertools
import json
import cProfile
import time

# from pyinstrument import Profiler
from sys import platform


class LifeBoard:
    path = ""
    def read_tilings(self, interior_str, width, height, level, max_tiling):
        print("read with path: ",LifeBoard.path)
        dict_interior = json.load(open(LifeBoard.path+"cast_{}_{}_{}.json"
                                       .format(interior_str.replace(",", ""), width, height), "r"))
        #dict_interior = {"":{"":",".join(["0" for i in range(25)])}}
        dict_boards = {nb_str: ob_dict
                       for nb_str, ob_dict in dict_interior.items()}
        if len(dict_boards)==1:
            return [LifeBoard(string=ob_str, width=width, height=height)
             for ob_str in list(list(dict_boards.values())[0].values())[:max_tiling]]

        dict_boards_selection = {nb_str: ob_dict for nb_str, ob_dict in dict_boards.items()
                                 if self.fit(LifeBoard(string=nb_str, width=width, height=height), level)}
        old_boards_tilings_list = list({ob_envelope: ob_str
                                        for ob_dict in dict_boards_selection.values()
                                        for ob_envelope, ob_str in ob_dict.items()}
                                       .values())
        # TODO - better selection - maybe probability
        old_boards_tilings = [LifeBoard(string=ob_str, width=width, height=height)
                              for ob_str in old_boards_tilings_list[:max_tiling]]
        return old_boards_tilings

    def __init__(self, width=25, height=25, board=None, string=None):
        if string is not None:
            self.board = np.array([int(cell) for cell in string.split(",")]) \
                .reshape((width, height))
            self.width = width
            self.height = height
        elif board is not None:
            self.width, self.height = board.shape
            self.board = board
        else:
            self.width = width
            self.height = height
            self.board = None

    def cast(self, padding, assignment_msb=[], remove_duplicate=True):
        # cast all possiblites - forward all and cast envelope
        # TODO - constraint part of the board
        msb_bits = len(assignment_msb)
        lsb_bits = self.width * self.height - msb_bits
        #  padding: [(0, 1), (0, 1)] should be different
        dict_cast, dict_boards = {}, {}
        # counter,counter_dict = 0, 0
        # pr = cProfile.Profile()
        # pr.enable()
        iter_assignments_lsb = itertools.product([0, 1], repeat=lsb_bits)
        # key1 - new board (iterior) , key2 - new board(all)
        # value - old patterns (multi),remove duplicate for envelope (put flag for it)
        # duplication envelope - values of envelope (TODO advanced - counts of outer envelope)
        obs = [LifeBoard(board=np.array(assignment_msb + assignment_lsb)
                         .reshape((self.width, self.height)))
               for assignment_lsb in iter_assignments_lsb]
        nbs = [ob.add_padding(padding).forward().remove_padding(padding) for ob in obs]
        for ob, nb in zip(obs, nbs):
            interior_str = nb.remove_padding(padding).simple_str()
            if interior_str not in dict_cast.keys():
                dict_cast[interior_str], dict_boards[interior_str] = {}, {}
            if nb.simple_str() not in dict_cast[interior_str].keys():
                dict_cast[interior_str][nb.simple_str()], dict_boards[interior_str][nb.simple_str()] = [], []
            if not remove_duplicate or \
                    all([not ob.equal_envelope(ob_rhs) for ob_rhs in dict_boards[interior_str][nb.simple_str()]]):
                dict_cast[interior_str][nb.simple_str()].append(ob.simple_str())
                dict_boards[interior_str][nb.simple_str()].append(ob)

            # profiler.stop()
            # print(profiler.output_text(unicode=True, color=True))
        # pr.disable()
        # pr.print_stats(sort="time")

        return dict_cast

    def forward(self, num_steps=1):
        # @credit James McGuigan - (fix error of roll)
        # if count>3 => 0
        # if count=0,cnt_unknows = 2 =>0 = >rest are unknown
        new_board = self.__copy__()
        while num_steps > 0:
            nbrs_count = sum(np.roll(new_board.board == 1, (i, j), (0, 1))
                             for i in (-1, 0, 1) for j in (-1, 0, 1)
                             if (i != 0 or j != 0))
            unkn_board = np.int32(new_board.board == -1)
            unkn_count = sum(np.roll(unkn_board, (i, j), (0, 1))
                             for i in (-1, 0, 1) for j in (-1, 0, 1)
                             if (i != 0 or j != 0))
            # X=0,c+x>=3 & c<4 ==> unknown
            # X=1, c+x >=2 & c<4 ==> unknown
            new_board.board = np.int32((nbrs_count == 3) | ((new_board.board == 1) & (nbrs_count == 2)))
            new_board.board[
                (unkn_count > 0) & (nbrs_count < 4) & ((nbrs_count + unkn_count) >= (3 - new_board.board))] = -1
            num_steps -= 1
        return new_board

    # give all possibilities
    def reverse(self, num_steps=1, width=5, height=5, msb_bits=10):
        old_boards_positions = [(1000,LifeBoard(board=-1 * np.ones(self.board.shape,dtype=np.int32)))]
        # levels - ranges of each tilling
        levels = self.build_levels(width, height)
        max_old_boards ,max_tiling = 10, 10
        # TODO - find good start (high density -  1's number)
        debug_performance = False
        if debug_performance:
            pr = cProfile.Profile()
            pr.enable()
        for level in levels:
            #print("level:", level)
            #tic_level = time.time()
            interior_str = self.interior_str([(1, 1), (1, 1)], level)
            print("inside reverse before read: ",LifeBoard.path)
            old_boards_tilings = self.read_tilings(interior_str, width, height, level, max_tiling)
            #print("stage 1: ", time.time()-tic_level)
            # TODO - soften selection (another parameter)
            # TODO - selection based on probability
            # TODO - selection based on real fit for delta
            old_boards_positions = old_boards_positions[:max_old_boards]
            #print("first selection: ", len(old_boards_tilings), len(old_boards_positions))
            old_boards_results = [ob_pos[1].position(ob_tiling, level, constraint=self)
                          for ob_pos in old_boards_positions for ob_tiling in old_boards_tilings]
            #print("stage 2: ", time.time() - tic_level)
            old_boards_positions =sorted(old_boards_results, key=lambda pos:pos[0])
            #print("stage 3: ", time.time() - tic_level)
            #print("second selection: ", len(old_boards_positions),old_boards_positions[0][0])
        if debug_performance:
            pr.disable()
            pr.print_stats(sort="time")
        print(len(old_boards_positions),old_boards_positions[0][0])
        return old_boards_positions[0][1]

    def add_padding(self, padding):
        result = self.__copy__()
        result.board = np.pad(self.board, padding, mode='constant',
                              constant_values=-1)
        result.width, result.height = result.board.shape
        return result

    def remove_padding(self, padding):
        result = self.__copy__()
        result.board = result.board[padding[0][0]:-padding[0][1], padding[1][0]:-padding[1][1]]
        result.width, result.height = result.board.shape
        return result

    def simple_str(self):
        return ",".join([str(cell) for cell in self.board.flatten()])

    def __str__(self):
        return str(self.board)
        # return "\n".join(["".join([(colour_to_str[cell] + "  ") for cell in row])
        #                for row in self.board])

    def __copy__(self):
        return LifeBoard(board=np.copy(self.board))

    def position(self, ob_tiling, level, constraint=None):
        res_board = np.copy(self.board)
        res_board[level[0]:level[1] + 1, level[2]:level[3] + 1] = ob_tiling.board
        acc_board = LifeBoard(board=res_board)
        if constraint is None:
            return 0,acc_board
        return constraint.fitness(acc_board.forward()),acc_board

    def fit(self, rhs, ranges=None):
        if ranges is None:
            ranges = (0, rhs.width, 0, rhs.height)
        board_ranges = self.board[ranges[0]:ranges[1] + 1, ranges[2]:ranges[3] + 1]
        return np.sum((board_ranges != rhs.board) & (rhs.board != -1) & (board_ranges != -1)) == 0

    def fitness(self, rhs, ranges=None):
        if ranges is None:
            ranges = (0, rhs.width-1, 0, rhs.height-1)
            board_ranges = self.board[ranges[0]:ranges[1] + 1, ranges[2]:ranges[3] + 1]
            return np.sum((board_ranges != rhs.board) & (rhs.board != -1) & (board_ranges != -1))
        return np.sum((self.board != rhs.board) & (rhs.board != -1) & (self.board != -1))


    def equal_envelope(self, ob_rhs):
        return np.all(self.board[0, :] == ob_rhs.board[0, :]) and np.all(self.board[-1, :] == ob_rhs.board[-1, :]) \
               and np.all(self.board[:, 0] == ob_rhs.board[:, 0]) and np.all(self.board[:, -1] == ob_rhs.board[:, -1])

    def interior_str(self, padding=None, ranges=None):
        board_ranges = self.board[ranges[0]:ranges[1] + 1, ranges[2]:ranges[3] + 1]
        board_ranges_nopad = board_ranges[padding[0][0]:-padding[0][1],
                             padding[1][0]:-padding[1][1]]
        return ",".join([str(cell) for cell in board_ranges_nopad.flatten()])

    def envelope_str(self):
        return ",".join([str(self.board[i, j]) for i in range(self.width) for j in range(self.height)
                         if i in [0, self.width - 1] or j in [0, self.height - 1]])
        envelope = list(self.board[0, :])
        envelope.extend(list(self.board[1:, -1]))
        envelope.extend(list(self.board[-1, -2::-1]))
        envelope.extend(list(self.board[-2:0:-1, 0]))
        return ",".join([str(cell) for cell in envelope])

    def build_levels(self, width, height):
        return [(i * width, (i + 1) * width - 1, j * height, (j + 1) * height - 1) for i in range(self.width // width)
                for j in range(self.height // height)]


    def __eq__(self,lhs):
        if self.width != lhs.width or self.height != lhs.height:
            return False
        return np.sum(self.board!=lhs.board) == 0



