# base imports
import json
import os
import time
from pathlib import Path

import numpy as np
import pandas as pd
from termcolor import colored
from datetime import datetime

pkg_path = Path(__file__).parents[1]
data_path = f"{pkg_path}/.package_data"
project_list = json.load(open(f"{data_path}/project_list.json", "r"))

halftab = " " * 4

def set_entry_size_manual(height, width):
    os.system("printf '\e[3;0;0t'")
    os.system(f"printf '\e[8;{height};{width}t'")


def set_entry_size(entry, additional_height=6, additional_width=20, min_width=60, max_width=69):
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


def print_lines(lines: list, width: int, extra_height=1) -> None:
    print_width = width + 1
    height = len(lines) + extra_height
    set_entry_size_manual(height, print_width)
    [print(line) for line in lines]

file_options = [
    "notes",
    "note",
    "tasks",
    "task",
    "refs",
    "ref",
    "arc",
    "archive",
    "archives",
    "back",
    "backburner",
    "schedule",
    "scheduled",
    "sc",
    "sd",
    "scd",
]

def process_file(file: str):

    if file in ["task", "ref", "note", "archive"]:
        file_name = file + "s"
    elif file == "back":
        file_name = "backburner"
    elif file in ["sc", "sd", "scd", "schedule"]:
        file_name = "scheduled"
    elif file == "arc":
        file_name = "archives"
    else:
        file_name = file
    
    return file_name

def process_name(file: str):
    if file in ["tasks", "refs", "notes", "archives", "scheduled"]:
        name = file[:-1]
    elif file in ["sc", "sd", "scd"]:
        name = "schedule"
    elif file == "back":
        name = "backburner"
    elif file == "arc":
        name = "archives"
    else:
        name = file
    
    return name

def get_bonus_width(file_name: str):
    if file_name in ["archives", "scheduled"]:
        bonus_width = 1
    else:
        bonus_width = 0

    return bonus_width

def check_scheduled(project_list = project_list):
    moves = {k:0 for k in project_list}
    for project in project_list:
        sc_path = f"{data_path}/projects/{project}/scheduled.csv"
        back_path = f"{data_path}/projects/{project}/backburner.csv"
        sc_df = pd.read_csv(sc_path)
        back_df = pd.read_csv(back_path)
        for idx, row in enumerate(sc_df.to_dict("records")):
            release_time = datetime.strptime(row["scheduled_release"], "%m/%d/%Y %H:%M:%S")
            # Move if past date
            if release_time < datetime.now():
                iloc = sc_df.index.get_loc(idx)
                to_be_moved = sc_df.iloc[iloc]
                back_df.loc[len(back_df)] = to_be_moved.tolist()[:-1] # drop release time
                back_df.to_csv(back_path, index=False)
                sc_df = sc_df.loc[sc_df.index != idx]
                sc_df.to_csv(sc_path, index=False)
                moves[project] += 1
    
    k_w_moves = sum([v > 0 for v in moves.values()])
    if k_w_moves:
        print("")
        for k,v in moves.items():
            if v > 0:
                p = "s" if v > 1 else ""
                print(f"{halftab}({v}) item{p} from {k} activated from schedule.")
        print("")
        set_entry_size_manual(height=k_w_moves+3, width=51)
        timed_sleep()
        

def check_init() -> None:
    if not os.path.isdir(data_path):
        os.makedirs(data_path)
        json.dump([], open(f"{data_path}/project_list.json", "w"))
        json.dump([], open(f"{data_path}/hidden_project_list.json", "w"))
        os.makedirs(f"{data_path}/projects")

    check_scheduled()


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
    string: str, linelen: int=40) -> list:
    lines = []
    for l in string.split(sep="|"):
        newlines = split_to_width(l, linelen=linelen)
        lines += newlines
    return lines


def parse_entries(df: pd.DataFrame, file: str, width: int) -> None:
    """Print all entries in dataframe"""
    lines = []
    lines.append("-" * width)
    if len(df) > 0:
        for i, row in enumerate(df.to_dict("records")):
            rowlines_p = process_rowlines(idx=i, row=row, width=width, file=file)
            lines += rowlines_p
    lines.append("-" * width)
    return lines

def process_rowlines(idx, row, width, file):
    for key in ["flagged", "time_estimate", "scheduled_release" ,"datetime_archived"]:
        if key not in row:
            row[key] = None

    linelen = width - 23 if file in ["scheduled", "archives"] else width - 20
    lines = parse_row(
        row["entry"], linelen=linelen
    )
    
    lines_p = []
    lines = [colored(l, "red", attrs=["bold"]) if row["flagged"] else l for l in lines]
    if row["flagged"]:
        linelen -= 13
    if type(row["time_estimate"]) is float and not (row["scheduled_release"] or row["datetime_archived"]):
        lines_p.append(f"{halftab}{idx: <{5}}{lines[0]: <{linelen}}{halftab}{row['time_estimate']}hrs")
    elif row["scheduled_release"]:
        lines_p.append(f"{halftab}{idx: <{5}}{lines[0]: <{linelen}}{halftab}{process_date_str(row['scheduled_release']): >{10}}")
    elif row["datetime_archived"]:
        lines_p.append(f"{halftab}{idx: <{5}}{lines[0]: <{linelen}}{halftab}{process_date_str(row['datetime_archived']): >{10}}")
    else:
        lines_p.append(f"{halftab}{idx: <{5}}{lines[0]: <{linelen}}")

    for line in lines[1:]:
        lines_p.append(f"{' '*9}{line: <{linelen}}")
    return lines_p

def process_date_str(date_str: str) -> str:
    s = f" {date_str[:10]}".replace(" 0", " ").replace("/0", "/")
    print(s, len(s))
    return s

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
