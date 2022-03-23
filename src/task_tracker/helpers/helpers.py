# base imports
import json
import os
from pathlib import Path
from termcolor import colored

import pandas as pd

pkg_path = Path(__file__).parents[1]
data_path = f"{pkg_path}/.package_data"


def check_init():
    if not os.path.isdir(data_path):
        os.makedirs(data_path)
        json.dump([], open(f"{data_path}/project_list.json", "w"))
        json.dump([], open(f"{data_path}/hidden_project_list.json", "w"))
        os.makedirs(f"{data_path}/projects")


def print_special(string: str, n_tab: int = 1, flagged: bool = False) -> None:
    lines = [l.strip() for l in string.split(sep="|")]
    print("\t" + lines[0])
    [print("\t" * n_tab + l) for l in lines[1:]]


def print_entries(df: pd.DataFrame) -> None:
    """Print all entries in dataframe"""
    print("-" * 40)
    if len(df) > 0:
        for i, row in enumerate(df.to_dict("records")):
            entry = colored(row["entry"],"red",attrs=["bold"]) if row["flagged"] else row["entry"]
            print_special(f"{i}\t{entry}", n_tab=2, flagged=row['flagged'])
    print("-" * 40)


def print_description(df_row: pd.DataFrame) -> None:
    print_special(f"{df_row['description']}")


def define_idx(pos) -> int:
    if pos == "HEAD":
        return 0
    elif pos == "TAIL":
        return -1
    else:
        return int(pos)


def move(df: pd.DataFrame, from_index: int, to_index: int) -> pd.DataFrame:
    """Move DF row from_index to_index"""
    idx = list(df.index)
    idx.remove(idx[from_index])
    to_index = to_index if to_index != -1 else len(idx)
    idx.insert(to_index, from_index)
    return df.iloc[idx].reset_index(drop=True)
