import numpy as np
import itertools
from scipy.ndimage.interpolation import shift
import json


class LifeBoard:
    dicts_tilings = {}

    @staticmethod
    def read_tilings(type_tiling, width, height):
        dict_cast = json.load(open("..\\preprocess\\{}_{}_{}.json".format(type_tiling, width, height), "r"))
        LifeBoard.dicts_tilings[type_tiling, width, height] = \
            {LifeBoard(string=k, width=width, height=height)
             : [LifeBoard(string=v, width=width, height=height) for v in v_list]
             for k, v_list in dict_cast.items()}
        return

    def __init__(self, width=25, height=25, board=None,string=None):
        if string is not None:
            self.board = np.array([int(cell) for cell in string.split(",")])\
                .reshape((width,height))
            self.width = width
            self.height = height
        elif board is not None:
            self.width, self.height = board.shape
        else:
            self.width = width
            self.height = height
        self.board = board

    def cast(self, padding):
        # cast all possiblites - forward all and cast envelope
        # TODO - constraint part of the board
        iter_assignments = itertools.product([0, 1], repeat=self.width * self.height)
        #  padding: [(0, 1), (0, 1)] should be different
        old_boards = [LifeBoard(board=np.array(assignment)
                                .reshape((self.width, self.height)))
                      for assignment in iter_assignments]
        new_boards = [ob.add_envelope(padding).forward().remove_envelope(padding) for ob in old_boards]
        dict_cast = {}
        # TODO - check why 5*5 has long running
        for ob, nb in zip(old_boards, new_boards):
            # TODO -add sums
            # key - new board , value - old patterns (multi),we can remove duplicate for cells not in envelope
            # we might represnt value list as dict_envelopes(dependes on padding)
            if nb.simple_str() not in dict_cast.keys():
                dict_cast[nb.simple_str()] = []
            dict_cast[nb.simple_str()].append(ob.simple_str())
        return dict_cast

    def forward(self, num_steps=1):
        # @credit James McGuigan - (fix error of roll)
        # if count>3 => 0
        # if count=0,cnt_unknows = 2 =>0 = >rest are unknown
        while num_steps > 0:
            nbrs_count = sum(shift(self.board == 1, (i, j))
                             for i in (-1, 0, 1) for j in (-1, 0, 1)
                             if (i != 0 or j != 0))
            unkn_board = np.int32(self.board == -1)
            unkn_count = sum(shift(unkn_board, (i, j))
                             for i in (-1, 0, 1) for j in (-1, 0, 1)
                             if (i != 0 or j != 0))
            # X=0,c+x>=3 & c<4 ==> unknown
            # X=1, c+x >=2 & c<4 ==> unknown
            self.board = (nbrs_count == 3) | (self.board & (nbrs_count == 2))
            self.board[(nbrs_count < 4) & ((nbrs_count + unkn_count) >= (3 - self.board))] = -1
            num_steps -= 1
        return self

    # give all possiblities
    def reverse(self, num_steps=1):
        old_board = -1 * np.ones(self.board.shape)
        # levels - ranges of each tilling,tilling_type,rotation
        levels = [{"ranges": (0, 2, 0, 2), "type": "corner", "rotation": 0}]
        for level in levels:
            pass
        # iterate levels - use predefined tiling and constraint until the end
        # take only one possibility each time
        pass

    def envelope_as_str(self, envelope):
        return "".join([str(self.board[cell]) for cell in envelope])

    def interior_as_str(self, envelope):
        return "".join([str(self.board[cell]) for cell in
                        itertools.product(range(self.width), range(self.height)) if cell not in envelope])

    def add_envelope(self, padding):
        self.board = np.pad(self.board, padding, mode='constant',
                            constant_values=-1)
        self.width, self.height = self.board.shape
        return self

    def remove_envelope(self, padding):
        self.board = self.board[padding[0][0]:-padding[0][1], padding[1][0]:-padding[1][1]]
        self.width, self.height = self.board.shape
        return self

    def simple_str(self):
        return ",".join([str(cell) for cell in self.board.flatten()])


def __str__(self):
    colour_to_str = {1: '\030[47m', 0: '\037[40m'}
    return "\n".join(["".join([(colour_to_str[cell] + "  ") for cell in row])
                      for row in self.board])
