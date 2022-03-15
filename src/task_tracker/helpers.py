# base imports
import pandas as pd


def print_ls(proj: str) -> None:
    """Print all tasks in reference project"""
    tasks = pd.read_csv(f"projects/{proj}/tasks.csv")
    print(tasks)


def move(df: pd.DataFrame, from_index: int, to_index: int) -> pd.DataFrame:
    """Move DF row from_index to_index"""
    idx = list(df.index)
    idx.remove(idx[from_index])
    to_index = to_index if to_index != -1 else len(idx)
    idx.insert(to_index, from_index)
    return df.iloc[idx].reset_index(drop=True)
