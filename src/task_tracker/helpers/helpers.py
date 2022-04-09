# base imports
import json
import os
import time
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from termcolor import colored
from datetime import datetime, timedelta
from datetime import date as dt
from dateutil.relativedelta import relativedelta
from parse import *
import time

pkg_path = Path(__file__).parents[1]
data_path = f"{pkg_path}/.package_data"
project_list = json.load(open(f"{data_path}/project_list.json", "r"))
CONFIG = json.load(open(f"{pkg_path}/helpers/config.json", "r"))
file_options = list(CONFIG.keys()) + sum([CONFIG[k]["aliases"] for k in CONFIG.keys()], [])
columns = ["entry", "description", "time_estimate", "flagged", "datetime_created", "datetime_moved", "datetime_scheduled"]

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

def process_file(filename: str):
    files = CONFIG.keys()

    if filename in files:
        return filename
    else:
        for file in files:
            if filename in CONFIG[file]["aliases"]:
                return file
    raise ValueError(f"File {filename} not found in file names or aliases.")
            

def process_name(filename: str):
    file = process_file(filename)
    return CONFIG[file]["file_name"]

def transfer_row(idx, from_df, to_df):
    iloc = from_df.index.get_loc(idx)
    to_be_moved = from_df.iloc[iloc]
    to_df = to_df.append(to_be_moved.to_dict(), ignore_index=True)
    from_df = from_df.loc[from_df.index != idx]

    to_df.loc[len(to_df)-1, "datetime_moved"] = datetime.now().strftime("%m/%d/%Y %H:%M:%S")

    return from_df, to_df

def check_scheduled(project_list = project_list):

    chain_files = [file for file in CONFIG.keys() if "send_to" in CONFIG[file].keys()]

    moves = {k:0 for k in project_list}
    for project in project_list:
        for file in chain_files:
            from_path = f"{data_path}/projects/{project}/{file}.csv"
            to_path = f"{data_path}/projects/{project}/{CONFIG[file]['send_to']}.csv"
            from_df = pd.read_csv(from_path)
            to_df = pd.read_csv(to_path)

            for idx, row in enumerate(from_df.to_dict("records")):
                if pd.isna(row["datetime_scheduled"]):
                    pass
                else:
                    release_time = datetime.strptime(row["datetime_scheduled"], "%m/%d/%Y %H:%M:%S")
                    # Move if past date
                    if release_time < datetime.now():
                        from_df, to_df = transfer_row(idx, from_df, to_df)
                        from_df.to_csv(from_path, index=False)
                        to_df.loc[len(to_df)-1, "datetime_scheduled"] = float("NaN")
                        to_df.to_csv(to_path, index=False)
                        moves[project] += 1
    
    k_w_moves = sum([v > 0 for v in moves.values()])
    if k_w_moves:
        print("")
        for k,v in moves.items():
            if v > 0:
                p = "s" if v > 1 else ""
                print(f"{halftab}({v}) item{p} from {k} moved on schedule.")
        print("")
        set_entry_size_manual(height=k_w_moves+3, width=51)
        timed_sleep(1.5)
        

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
    string: str, linelen: int=40) -> list:
    lines = []
    for l in string.split(sep="|"):
        newlines = split_to_width(l, linelen=linelen)
        lines += newlines
    return lines


def parse_entries(df: pd.DataFrame, project: str, file: str, width: int) -> None:
    """Print all entries in dataframe"""
    lines = []
    lines += ["", project]
    lines.append("-" * width)
    if len(df) > 0:
        for i, row in enumerate(df.to_dict("records")):
            rowlines_p = process_rowlines(idx=i, row=row, width=width, file=file)
            lines += rowlines_p
    lines.append("-" * width)

    stats_str, hour_str = get_project_stats(project, file)
    lines.append(f"{stats_str: <{width-10}}{hour_str: <{10}}")
    
    return lines

def get_project_stats(project, file):
    stats_str = ""; hour_str = ""
    if "stats_from_prev" in CONFIG[file].keys():
        prev_file = get_prev(file)
        last_df = pd.read_csv(f"{data_path}/projects/{project}/{prev_file}.csv")
        stats = {"n": len(last_df), "total": round(np.nansum(last_df["time_estimate"]),2)}
        lst_stats = [str(stats[c]) for c in CONFIG[file]["stats_from_prev"]]
        lst_stats = ["0"] if list(set(lst_stats)) == ["0"] else lst_stats
        stats_str = f"<- {' | '.join(lst_stats)}" if len(lst_stats) > 0 else ""

    if "attrs" in CONFIG[file].keys() and "hours" in CONFIG[file]["attrs"]:
        current_df = pd.read_csv(f"{data_path}/projects/{project}/{file}.csv")
        p_hours = np.nansum(current_df["time_estimate"]) if len(current_df) > 1 else 0
        hour_str = "T: " + str(round(p_hours,2)) + 'hrs' if p_hours > 0 else ""

    return stats_str, hour_str

def process_rowlines(idx, row, width, file):

    if "stat" in CONFIG[file].keys() and "datetime" in CONFIG[file]["stat"]:
        linelen = width - 23
    else:
        linelen = width - 20

    lines = parse_row(
        row["entry"], linelen=linelen
    )
    
    lines_p = []
    lines = [colored(l, "red", attrs=["bold"]) if row["flagged"] else l for l in lines]
    if row["flagged"]:
        linelen -= 13
    if "stat" not in CONFIG[file].keys() or pd.isna(row[CONFIG[file]["stat"]]):
        lines_p.append(f"{halftab}{idx: <{5}}{lines[0]: <{linelen}}")
    else:
        stat = CONFIG[file]["stat"]
        if stat == "time_estimate":
            lines_p.append(f"{halftab}{idx: <{5}}{lines[0]: <{linelen}}{halftab}{row[stat]}hrs")
        elif "datetime" in stat:
            lines_p.append(f"{halftab}{idx: <{5}}{lines[0]: <{linelen}}{halftab}{process_date_str(row[stat]): >{10}}")

    for line in lines[1:]:
        lines_p.append(f"{' '*9}{line: <{linelen}}")
    return lines_p

def process_date_str(date_str: str) -> str:
    print(date_str)
    print(type(date_str))
    s = f"{date_str[:10]}".replace(" 0", " ").replace("/0", "/")
    print(s, len(s))
    return s

def parse_description(df_row: pd.DataFrame) -> list:
    return [""] + parse_row(f"{df_row['description']}") + [""]


def define_idx(pos:int, ref_obj) -> int:
    if pos == "HEAD":
        return 0
    elif pos == "TAIL":
        return len(ref_obj)-1
    else:
        return int(pos)


def move(df: pd.DataFrame, from_index: int, to_index: int) -> pd.DataFrame:
    """Move DF row from_index to_index"""
    idx = list(df.index)
    idx.remove(idx[from_index])
    to_index = to_index if to_index != -1 else len(idx)
    idx.insert(to_index, from_index)
    return df.iloc[idx].reset_index(drop=True)

def reformat_date(date_and_time: str):
    if date_and_time[-1] in ["a", "A", "p", "P"]:
        date_and_time += "m"
    if " " in date_and_time:
        date_str, time_str = date_and_time.split(" ")
    elif not date_and_time[-1] in ["M", "m"]:
        date_str, time_str = date_and_time, "00:00"
    else:
        date, time_str = dt.today(), date_and_time
        date_str = None
    
    if date_str:
        if date_str.count("/") == 0:
            today = dt.today()
            day = time.strptime(date_str, "%a").tm_wday
            remainder = (day-today.weekday()-1) % 7 + 1
            date = today + timedelta(days=remainder)
        else:
            p = [v.zfill(2) for v in parse("{}/{}", date_str)]
            date = datetime.strptime(f"{p[0]}/{p[1]}", "%m/%d")
            date += relativedelta(years=datetime.now().year - date.year)
            if datetime.now() > date:
                date += relativedelta(years=1)
    
    if ":" in time_str:
        p = [v.zfill(2) for v in parse("{}:{}", time_str[:-2])]
        tm = datetime.strptime(f"{p[0]}:{p[1]}{time_str[-2:]}", "%I:%M%p").time()
    else:
        tm = datetime.strptime(f"{time_str}", "%I%p").time()
    
    return datetime.combine(date, tm)

def define_chain(file: str) -> list:

    def fill_prev(file, chain):
        prev = get_prev(file)
        if prev:
            chain = [get_prev(file)] + chain
            return fill_prev(chain[0], chain)
        
        return chain

    def fill_next(file, chain):
        chain += [file]
        if "send_to" in CONFIG[file].keys():
            return fill_next(CONFIG[file]["send_to"], chain)
        
        return chain

    next = fill_next(file, [])
    prev = fill_prev(file, [])

    return prev + next

def get_prev(file):
    senders = [f for f in CONFIG.keys() if "send_to" in CONFIG[f].keys() and CONFIG[f]["send_to"] == file]
    if len(senders) > 1:
        warnings.warn(f"Multiple files send to the provided file. Using the first in config.json: {senders[0]}.")
    if len(senders) > 0:
        return senders[0]