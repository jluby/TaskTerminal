# base imports
import json
import os
from pathlib import Path
import time

import pandas as pd
import numpy as np
from termcolor import colored

pkg_path = Path(__file__).parents[1]
data_path = f"{pkg_path}/.package_data"

halftab = " " * 4

def set_entry_size(entry):
    print_width = np.max([60,np.min([np.max([len(l) for l in entry.tolist() if type(l) is str])+21, 70])])
    os.system("printf '\e[3;0;0t'")
    os.system(f"printf '\e[8;{len(entry)+6};{print_width}t'")

def reformat(string: str, input_type: str = None):
    string = string.replace(". ", ".@")
    sentences = [s for s in string.split(sep="@")]
    newstring = ""
    for s in sentences:
        s = f"{halftab}{s}"
        if input_type == "input":
            s = f"{s}\n\t"
        if input_type == "error":
            s = f"\n{s}"
        newstring += s
    return newstring

def timed_sleep():
    time.sleep(1.5)

def print_lines(lines: list) -> None:
    width = np.max([len(line) for line in lines]) + 2
    height = len(lines) + 1
    os.system("printf '\e[3;0;0t'")
    os.system(f"printf '\e[8;{height};{width}t'")
    [print(line) for line in lines]

def check_init() -> None:
    if not os.path.isdir(data_path):
        os.makedirs(data_path)
        json.dump([], open(f"{data_path}/project_list.json", "w"))
        json.dump([], open(f"{data_path}/hidden_project_list.json", "w"))
        os.makedirs(f"{data_path}/projects")


def split_to_width(string: str, linelen: int) -> list:
    string = string.strip()
    if len(string) <= linelen:
        string_ls = [string]
    else:
        string_ls = []
        remainder = string
        check_idx = linelen
        while len(remainder) > linelen:
            if remainder[check_idx] == " ":
                string_ls.append(remainder[:check_idx])
                remainder = remainder[check_idx + 1 :]
                check_idx = linelen
            elif check_idx == 0:
                string_ls.append(remainder[:linelen])
                remainder = remainder[linelen:]
                check_idx = linelen
            else:
                check_idx -= 1
        string_ls.append(remainder)

    return [f"{l: <{linelen}}" for l in string_ls]


def parse_row(
    string: str, n_tab: int = 0, time_estimate: float = None
) -> None:
    entry_char_limit = 30
    lines = []
    for l in string.split(sep="|"):
        newlines = split_to_width(l, linelen=entry_char_limit)
        lines += newlines
    timestamp = f"{time_estimate}hrs" if time_estimate else ""
    line0 = halftab + lines[0] + halftab + timestamp
    extra_lines = [halftab + "\t" * n_tab + l for l in lines[1:]]
    return [line0] + extra_lines


def parse_entries(df: pd.DataFrame, file: str) -> None:
    """Print all entries in dataframe"""
    lines = []
    width = 50
    lines.append("-" * width)
    if len(df) > 0:
        for i, row in enumerate(df.to_dict("records")):
            entry = (
                colored(row["entry"], "red", attrs=["bold"])
                if row["flagged"]
                else row["entry"]
            )
            time_estimate = row["time_estimate"] if file == "tasks" else None
            rowlines = parse_row(f"{i}\t{entry}", n_tab=1, time_estimate=time_estimate)
            lines += rowlines
    lines.append("-" * width)
    return lines

def parse_description(df_row: pd.DataFrame) -> list:
    return [''] + parse_row(f"{df_row['description']}") + ['']


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
