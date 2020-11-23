import itertools

import pandas as pd
import numpy as np
import time
import json

import architecture
import architecture.LifeBoard
from utils.util import csv_to_delta, csv_to_numpy, numpy_to_dict

def read_data(production = False):
    if production:
        input_directory = "/kaggle/input/conways-reverse-game-of-life-2020/"
    else:
        input_directory = "F:\\data\\conways-reverse-game-of-life-2020\\"
    train_file = input_directory + "train.csv"
    test_file = input_directory + "test.csv"
    sample_submission_file  = input_directory+"sample_submission.csv"
    # submission_file         = f'{output_directory}/submission.csv'
    # timeout_file            = f'{output_directory}/timeouts.csv'
    # image_segmentation_file = f'{root_directory}/output/image_segmentation_solutions.csv'

    train_df = pd.read_csv(train_file, index_col='id').astype(np.int)
    test_df = pd.read_csv(test_file, index_col='id').astype(np.int)
    submission_df         = pd.read_csv(sample_submission_file,  index_col='id').astype(np.int)
    # sample_submission_df  = pd.read_csv(sample_submission_file,  index_col='id').astype(np.int)
    # timeout_df            = pd.read_csv(timeout_file,  index_col='id') if os.path.exists(timeout_file) else pd.DataFrame(columns=['id','timeout'])
    # image_segmentation_df = pd.read_csv(image_segmentation_file,  index_col='id').astype(np.int)
    return train_df, test_df, submission_df


def preprocess_tilings(size):
    init_board = architecture.LifeBoard.LifeBoard(width=size, height=size)
    envelope = [(i, size - 1) for i in range(size)]
    envelope.extend([(size - 1, i) for i in range(size)])
    padding = [(1, 1), (1, 1)]
    msb_bits=10
    iter_assignments_msb = itertools.product([0, 1], repeat=msb_bits)
    for assigment_msb in iter_assignments_msb:
        dict_cast = init_board.cast(padding=padding,assignment_msb=assigment_msb)
        json.dump(dict_cast, open("..\\preprocess\\cast_{}_{}_{}.json".
                                  format("".join([str(b) for b in assigment_msb]),size, size), "w"))
        print("finish msb bits",assigment_msb)


def solve(df,submission_df):
    #idxs = [4]
    idxs = (idx for idx in df.index)
    deltas = (csv_to_delta(df, idx) for idx in idxs)  # generator
    boards = (csv_to_numpy(df, idx, key='stop') for idx in idxs)

    tic_solve = time.time()
    for idx, board, delta in zip(idxs,boards, deltas):
        if time.time() - tic_solve < 10:
            rev_board = architecture.LifeBoard.LifeBoard(board=board)
            for _ in range(delta):
                rev_board = rev_board.reverse()
            solution_dict = numpy_to_dict(rev_board.board)
            submission_df.loc[idx] = pd.Series(solution_dict)
        if (idx % 1000 == 0):
            print(idx,time.time()-tic_solve)


    print("time to solve: ",time.time()-tic_solve)




def main(production = False):
    train_df,test_df,submission_df = read_data(production)
    if production:
        output_file = "/output/submission.csv"
    else:
        output_file = "..\\output\\submission.csv"
        architecture.LifeBoard.LifeBoard.path = ".." + "//" + "preprocess" + "//"

    solve(train_df,submission_df)

    submission_df.sort_index().to_csv(output_file)
    #preprocess(train_df)
    #preprocess_tilings(5)
    print("end main")

if __name__ == "__main__":
    tic = time.time()
    main()
    print("time elpassed: {}".format(time.time() - tic))
