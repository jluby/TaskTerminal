# base imports
import json
import os
from pathlib import Path
from termcolor import colored

import pandas as pd

pkg_path = Path(__file__).parents[1]
data_path = f"{pkg_path}/.package_data"

short_break = " "*4


def check_init():
    if not os.path.isdir(data_path):
        os.makedirs(data_path)
        json.dump([], open(f"{data_path}/project_list.json", "w"))
        json.dump([], open(f"{data_path}/hidden_project_list.json", "w"))
        os.makedirs(f"{data_path}/projects")

def split_to_width(string: str, linelen: int):
    string = string.strip()
    if len(string) <= linelen:
        string_ls = [string]
    else:
        string_ls = []
        remainder = string; check_idx = linelen
        while len(remainder) > linelen:
            if remainder[check_idx] == " ":
                string_ls.append(remainder[:check_idx])
                remainder = remainder[check_idx+1:]
                check_idx = linelen
            elif check_idx == 0:
                string_ls.append(remainder[:linelen])
                remainder = remainder[linelen:]
                check_idx = linelen
            else:
                check_idx -= 1
        string_ls.append(remainder)
    
    return [f'{l: <{linelen}}' for l in string_ls]

def print_special(string: str, n_tab: int = 0, time_estimate: float = None) -> None:
    entry_char_limit = 20
    lines = []
    for l in string.split(sep="|"):
        newlines = split_to_width(l, linelen=entry_char_limit)
        lines += newlines
    # TODO: split lines that are too long and pad to unit width
    # TODO: print time estimate next if task
    plural = 's' if time_estimate != 1 else ''
    print(short_break + lines[0] + short_break + f"{time_estimate}hr{plural}")
    [print(short_break + "\t" * n_tab + l) for l in lines[1:]]


def print_entries(df: pd.DataFrame, file: str) -> None:
    """Print all entries in dataframe"""
    print("-" * 40)
    if len(df) > 0:
        for i, row in enumerate(df.to_dict("records")):
            entry = colored(row["entry"],"red",attrs=["bold"]) if row["flagged"] else row["entry"]
            time_estimate = row["time_estimate"] if file == "tasks" else None
            print_special(f"{i}\t{entry}", n_tab=1, time_estimate=time_estimate)
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
