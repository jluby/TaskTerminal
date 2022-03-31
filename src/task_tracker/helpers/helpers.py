# base imports
import json
import os
import time
from pathlib import Path

import numpy as np
import pandas as pd
from termcolor import colored

pkg_path = Path(__file__).parents[1]
data_path = f"{pkg_path}/.package_data"

halftab = " " * 4

def set_entry_size_manual(height, width):
    os.system("printf '\e[3;0;0t'")
    os.system(f"printf '\e[8;{height};{width}t'")


def set_entry_size(entry, additional_height=6, additional_width=22, min_width=60, max_width=70):
    print_width = np.max(
        [
            min_width,
            np.min(
                [
                    np.max([len(l) for l in entry.tolist() if type(l) is str])
                    + additional_width,
                    max_width,
                ]
            ),
        ]
    )
    set_entry_size_manual(len(entry)+additional_height, print_width)


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


def timed_sleep(t=1):
    time.sleep(t)


def print_lines(lines: list, width: int) -> None:
    print_width = width + 1
    height = len(lines) + 1
    set_entry_size_manual(height, print_width)
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
    string: str, linelen: int=40) -> None:
    lines = []
    for l in string.split(sep="|"):
        newlines = split_to_width(l, linelen=linelen)
        lines += newlines
    return lines


def parse_entries(df: pd.DataFrame, file: str, width: int) -> None:
    """Print all entries in dataframe"""
    lines = []
    linelen = width-20
    lines.append("-" * width)
    if len(df) > 0:
        for i, row in enumerate(df.to_dict("records")):
            time_estimate = (
                row["time_estimate"]
                if file in ["tasks", "backburner"]
                else None
            )
            rowlines = parse_row(
                row["entry"], linelen=linelen
            )
            rowlines_p = process_rowlines(idx=i, lines=rowlines, time_estimate=time_estimate, linelen=linelen, flagged=row["flagged"])
            lines += rowlines_p
    lines.append("-" * width)
    return lines

def process_rowlines(idx, lines, time_estimate, linelen, flagged):
    lines_p = []
    lines = [colored(l, "red", attrs=["bold"]) if flagged else l for l in lines]
    if flagged:
        linelen -= 13
    estimate_str = f"{time_estimate}hrs" if time_estimate else ""
    lines_p.append(f"{halftab}{idx: <{5}}{lines[0]: <{linelen}}{halftab}{estimate_str}")
    for line in lines[1:]:
        lines_p.append(f"{' '*9}{line: <{linelen}}")
    return lines_p

def parse_description(df_row: pd.DataFrame) -> list:
    return [""] + parse_row(f"{df_row['description']}") + [""]


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
