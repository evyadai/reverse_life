import z3
import pandas as pd
import numpy as np

from refernce.z3_method.constraint_satisfaction.z3_solver import game_of_life_solver
from refernce.z3_method.utils.util import csv_to_delta, csv_to_numpy, numpy_to_dict



def read_data():
    input_directory = "F:\\data\\conways-reverse-game-of-life-2020\\"
    train_file              = input_directory+"train.csv"
    test_file               = input_directory+"test.csv"
    #sample_submission_file  = f'{input_directory}\\sample_submission.csv'
    #submission_file         = f'{output_directory}/submission.csv'
    #timeout_file            = f'{output_directory}/timeouts.csv'
    #image_segmentation_file = f'{root_directory}/output/image_segmentation_solutions.csv'



    train_df              = pd.read_csv(train_file, index_col='id').astype(np.int)
    test_df               = pd.read_csv(test_file,  index_col='id').astype(np.int)
    #submission_df         = pd.read_csv(submission_file,  index_col='id').astype(np.int)
    #sample_submission_df  = pd.read_csv(sample_submission_file,  index_col='id').astype(np.int)
    #timeout_df            = pd.read_csv(timeout_file,  index_col='id') if os.path.exists(timeout_file) else pd.DataFrame(columns=['id','timeout'])
    #image_segmentation_df = pd.read_csv(image_segmentation_file,  index_col='id').astype(np.int)
    return train_df,test_df

def preprocess(df):
    idxs = range(100)  # exclude timeouts
    deltas = (csv_to_delta(df, idx) for idx in idxs)  # generator
    boards = (csv_to_numpy(df, idx, key='stop') for idx in idxs)

    for board,delta in zip(boards,deltas):
        game_of_life_solver(board, delta=delta, timeout=10000, verbose=True)




def main():
    train_df,test_df = read_data()
    preprocess(train_df)
    print("end")



if __name__ == "__main__":
    main()

