import pandas as pd
import numpy as np


def csv_to_delta(df, idx):
    return int(df.loc[idx]['delta'])

def csv_column_names(key='start'):
    return [ f'{key}_{n}' for n in range(25**2) ]

def csv_to_numpy(df, idx, key='start') -> np.ndarray:
    try:
        columns = csv_column_names(key)
        board   = df.loc[idx][columns].values
    except:
        board = np.zeros((25, 25), dtype=np.int8)
    board = board.reshape((25,25))
    return board.astype(np.int8)

def numpy_to_dict(board: np.ndarray, key='start'):
    assert len(board.shape) == 2  # we want 2D solutions_3d[0] not 3D solutions_3d
    assert key in { 'start', 'stop' }

    board  = np.array(board).flatten().tolist()
    output = { f"{key}_{n}": board[n] for n in range(len(board))}
    return output